from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Dict

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from data.orders import ORDERS, PAYMENTS
from data.products import PRODUCTS

try:
    from langgraph.graph import END, StateGraph
except ImportError:  # pragma: no cover - optional dependency for minimal runtime
    END = None
    StateGraph = None


app = FastAPI(title="CommerceAI Support Agent", version="1.0.0")
app.mount("/static", StaticFiles(directory=str(Path(__file__).parent / "app" / "static")), name="static")

RETURNS: Dict[str, Dict[str, Any]] = {}


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=500)


def normalize_size(size: str | None) -> str:
    if not size:
        return "default"
    cleaned = size.strip().lower()
    if cleaned.startswith("size "):
        return cleaned
    return f"size {cleaned}"


def extract_order_id(message: str) -> str:
    matches = re.findall(r"#?(\d{5,})", message)
    if matches:
        return matches[0]
    return "100234"


def get_order(order_id: str) -> Dict[str, Any] | None:
    return ORDERS.get(order_id)


def get_payment(order_id: str) -> Dict[str, Any] | None:
    return PAYMENTS.get(order_id)


def get_product(product_name: str) -> Dict[str, Any] | None:
    return PRODUCTS.get(product_name)


def check_inventory(product_name: str, size: str | None = None) -> Dict[str, Any]:
    product = get_product(product_name)
    if not product:
        return {"available": False, "message": f"I couldn't find {product_name} in the catalog."}

    variant_key = normalize_size(size)
    variant = product["variants"].get(variant_key)
    if not variant:
        human_size = size or "default"
        return {"available": False, "message": f"{product_name} does not have a {human_size} variant."}

    if variant["in_stock"]:
        label = size or "default"
        return {
            "available": True,
            "message": f"Yes. {product_name}, {label} is in stock with {variant['available_units']} units available.",
            "units": variant["available_units"],
        }

    return {"available": False, "message": f"{product_name} is currently out of stock."}


def create_return(order_id: str, item: str, reason: str) -> Dict[str, Any]:
    return_id = f"RET-{len(RETURNS) + 10045}"
    RETURNS[return_id] = {"order_id": order_id, "item": item, "reason": reason, "status": "created"}
    return {
        "return_id": return_id,
        "status": "created",
        "message": f"Your return request has been created successfully. Return ID: {return_id}.",
    }


def cancel_order(order_id: str) -> Dict[str, Any]:
    order = get_order(order_id)
    if not order:
        return {"success": False, "message": f"Order #{order_id} was not found."}

    if order["status"] in {"cancelled", "delivered"}:
        return {"success": False, "message": f"Order #{order_id} cannot be cancelled in its current state."}

    order["status"] = "cancelled"
    return {"success": True, "message": f"Order #{order_id} has been cancelled successfully."}


def detect_intent(message: str) -> str:
    lower = message.lower()
    if any(keyword in lower for keyword in ["where is my order", "track", "status", "shipment", "delivered", "order #"]):
        return "order_status"
    if any(keyword in lower for keyword in ["available", "stock", "in stock", "size", "product", "nike air max"]):
        return "inventory_check"
    if any(keyword in lower for keyword in ["cancel", "cancellation"]):
        return "cancel_order"
    if any(keyword in lower for keyword in ["return", "refund"]):
        return "return_request"
    if any(keyword in lower for keyword in ["payment", "charged", "deducted", "declined", "transaction"]):
        return "payment_issue"
    return "general"


def build_langgraph() -> Any | None:
    if StateGraph is None or END is None:
        return None

    workflow = StateGraph(dict)

    def classify(state: Dict[str, Any]) -> Dict[str, Any]:
        state["intent"] = detect_intent(state["message"])
        return state

    def fetch_context(state: Dict[str, Any]) -> Dict[str, Any]:
        intent = state["intent"]
        text = state["message"]

        if intent == "order_status":
            order_id = extract_order_id(text)
            order = get_order(order_id)
            shipment = order["shipment"] if order else {}
            state["context"] = {"order": order, "shipment": shipment}
        elif intent == "inventory_check":
            state["context"] = check_inventory("Nike Air Max 270", "size 10")
        elif intent == "payment_issue":
            order_id = extract_order_id(text)
            state["context"] = {"order": get_order(order_id), "payment": get_payment(order_id)}
        elif intent == "cancel_order":
            order_id = extract_order_id(text)
            state["context"] = {"confirmation_needed": True, "order": get_order(order_id)}
        elif intent == "return_request":
            order_id = extract_order_id(text)
            state["context"] = {"order": get_order(order_id), "return": create_return(order_id, "Nike Air Max 270", "size mismatch")}
        else:
            state["context"] = {"message": "I can help with orders, payments, inventory, and returns."}
        return state

    def compose_response(state: Dict[str, Any]) -> Dict[str, Any]:
        intent = state["intent"]
        context = state["context"]

        if intent == "order_status":
            order = context.get("order")
            shipment = context.get("shipment", {})
            if order:
                state["response"] = (
                    f"Your order #{order['id']} was shipped on {shipment.get('expected_delivery', '2026-10-06')} and is currently {shipment.get('status', 'in_transit')}. "
                    f"The expected delivery date is {shipment.get('expected_delivery', '2026-10-10')}."
                )
            else:
                state["response"] = "I couldn't find that order. Please share the order number."
        elif intent == "inventory_check":
            state["response"] = context.get("message", "Item availability is currently unknown.")
        elif intent == "payment_issue":
            order = context.get("order")
            payment = context.get("payment")
            if order and payment:
                state["response"] = (
                    f"Your payment of ₹{payment['amount']} was successfully captured, but the order is still processing. "
                    "I have flagged this for a support review."
                )
            else:
                state["response"] = "I couldn't verify the payment details yet."
        elif intent == "cancel_order":
            state["response"] = "Order #100234 is eligible for cancellation. Would you like me to cancel it?"
        elif intent == "return_request":
            state["response"] = context.get("return", {}).get("message", "Return request created.")
        else:
            state["response"] = "I can help you track orders, check stock, review payments, manage cancellations, and start returns."
        return state

    workflow.add_node("classify", classify)
    workflow.add_node("fetch_context", fetch_context)
    workflow.add_node("compose_response", compose_response)
    workflow.set_entry_point("classify")
    workflow.add_edge("classify", "fetch_context")
    workflow.add_edge("fetch_context", "compose_response")
    workflow.add_edge("compose_response", END)
    return workflow.compile()


LANGGRAPH_WORKFLOW = build_langgraph()


def process_customer_message(message: str) -> str:
    if LANGGRAPH_WORKFLOW is not None:
        result = LANGGRAPH_WORKFLOW.invoke({"message": message})
        return result.get("response", "I couldn't determine the next step.")

    intent = detect_intent(message)
    lower = message.lower()

    if intent == "order_status":
        order_id = extract_order_id(message)
        order = get_order(order_id)
        if order:
            return (
                f"Your order #{order['id']} was shipped and is currently {order['shipment']['status']}. "
                f"Expected delivery is {order['shipment']['expected_delivery']}."
            )
        return "I couldn't find that order."

    if intent == "inventory_check":
        outcome = check_inventory("Nike Air Max 270", "size 10")
        return outcome.get("message", "I couldn't find that item in stock.")

    if intent == "payment_issue":
        order_id = extract_order_id(message)
        payment = get_payment(order_id)
        if payment:
            return f"Your payment of ₹{payment['amount']} was successfully captured, but the order is still processing. I have flagged this for support review."
        return "I couldn't verify the payment status."

    if intent == "cancel_order":
        return "Order #100234 is eligible for cancellation. Would you like me to cancel it?"

    if intent == "return_request":
        return create_return(extract_order_id(message), "Nike Air Max 270", "size mismatch")["message"]

    if "hello" in lower or "hi" in lower:
        return "Hi! I can help you track orders, check product availability, review payments, and start returns."

    return "I can help you with orders, shipping, inventory, returns, and payments."


@app.get("/health")
def healthcheck() -> Dict[str, str]:
    return {"status": "ok", "service": "commerceai-support-agent"}


@app.post("/chat")
def chat(request: ChatRequest) -> Dict[str, Any]:
    response = process_customer_message(request.message)
    return {"response": response, "agent": "CommerceAI Support Agent", "status": "ok"}


@app.get("/")
def home() -> FileResponse:
    html_path = Path(__file__).parent / "app" / "static" / "index.html"
    return FileResponse(html_path)
