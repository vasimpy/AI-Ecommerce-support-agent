from main import check_inventory, detect_intent, process_customer_message


def test_detect_intent_for_order_status():
    assert detect_intent("Where is my order #100234?") == "order_status"


def test_detect_intent_for_inventory():
    assert detect_intent("Do you have Nike Air Max size 10 in stock?") == "inventory_check"


def test_inventory_lookup_returns_available_units():
    result = check_inventory("Nike Air Max 270", "size 10")
    assert result["available"] is True
    assert result["units"] == 12


def test_process_customer_message_for_order_status():
    reply = process_customer_message("Where is my order #100234?")
    assert "order #100234" in reply.lower()


def test_process_customer_message_for_inventory():
    reply = process_customer_message("Do you have Nike Air Max size 10 in stock?")
    assert "in stock" in reply.lower()
