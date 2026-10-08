# CommerceAI Support Agent

## Overview
CommerceAI Support Agent is an MVP e-commerce support assistant built to demonstrate an AI agent architecture for customer support workflows. It combines a conversational interface, LangGraph-style orchestration, and mock ecommerce data to handle common support scenarios such as order tracking, inventory checks, payment issues, returns, and cancellations.

## Product Goal
The goal of this project is to showcase the design and implementation of an AI-powered customer support system that can safely interact with business systems through tools and structured workflows, rather than simply generating generic text.

## Key Features
- Order status lookup
- Shipment tracking summary
- Product availability lookup
- Payment issue review
- Return request creation
- Cancellation eligibility prompt
- Human approval workflow for actions requiring confirmation
- FastAPI backend
- Browser-based chat interface
- Mock data-driven workflows
- Test coverage for core behaviors

## Tech Stack
- Python 3.14+
- FastAPI for REST API and web app serving
- Pydantic for request validation and data models
- LangGraph-inspired workflow orchestration for agent reasoning
- HTML/CSS/JavaScript for the chat frontend
- pytest for automated validation
- Local mock data layer for product, order, payment, and return operations

## Architecture
- Frontend: lightweight HTML/JavaScript chat UI
- Backend: FastAPI application
- Agent orchestration: LangGraph workflow pattern
- Data layer: separated mock product and order data modules
- Runtime: Python 3.14+
- Operational pattern: intent detection, context retrieval, response generation, and confirmation-based actions

## How the Agent Works
```text
User Message
    ↓
Intent Detection
    ↓
Context Retrieval
    ↓
Policy / Eligibility Check
    ↓
Tool Call (order, product, payment, return, cancel)
    ↓
Response Generation
    ↓
Customer Response / Human Handoff / Approval Step
```

This flow is designed to simulate a realistic AI customer support system where the model does not act blindly. It first identifies the customer intent, loads context from the mock order and product datasets, checks business conditions, and then determines whether a recommendation, approval step, or support escalation is appropriate.

## Docker Setup
You can also run the project in a containerized environment.

### Dockerfile
```dockerfile
FROM python:3.14-slim

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Build and Run
```bash
docker build -t commerceai-support-agent .
docker run -p 8000:8000 commerceai-support-agent
```

## Portfolio Positioning
This project is positioned as an AI E-commerce Engineer portfolio initiative rather than a generic chatbot demo. It demonstrates a production-style mindset in which the assistant is treated as an operational system that:

- understands customer intent,
- safely retrieves business context,
- checks eligibility rules,
- invokes tools or system actions,
- and supports human oversight for sensitive operations.

This makes the project relevant for hiring managers looking for AI engineering capability across the full stack: backend APIs, orchestration logic, workflow design, business logic, and real-world support automation patterns.

## Future Roadmap
### Phase 1: Production-ready MVP improvements
- Add authentication and customer identity validation
- Support multiple customer records and account sessions
- Persist conversations and agent actions
- Add structured tool calling for real e-commerce APIs
- Improve policy checks for cancellation and return approvals

### Phase 2: Enterprise workflow integration
- Connect to real order management, inventory, payment, and ERP systems
- Add MCP-based tool adapters for external services
- Add admin dashboard for monitoring agent activity and tool usage
- Implement role-based access for agents and support staff

### Phase 3: Observability and scale
- Add tracing and logging for every user request and tool execution
- Track latency, success rate, and policy violations
- Add metrics dashboards for customer support performance
- Introduce retry logic and failure handling for external service calls

### Phase 4: Multi-channel support
- Expand beyond the web chat interface to WhatsApp, email, and live chat
- Add multilingual support for international storefronts
- Integrate with customer support CRMs and helpdesk systems

## Project Structure
```text
CommerceAI Support Agent/
├── app/
│   ├── __init__.py
│   └── static/
│       └── index.html
├── data/
│   ├── __init__.py
│   ├── orders.py
│   └── products.py
├── tests/
│   └── test_main.py
├── .gitignore
├── credentials.nv
├── main.py
├── README.md
├── requirements.txt
└── .pytest_cache/
```

## Setup
1. Create and activate a Python virtual environment if desired.
2. Install dependencies:

```bash
py -3 -m pip install -r requirements.txt
```

3. Run the app:

```bash
py -3 -m uvicorn main:app --host 127.0.0.1 --port 8000
```

4. Open the browser at:

```text
http://127.0.0.1:8000
```

## Example Requests
- "Where is my order #100234?"
- "Do you have Nike Air Max size 10 in stock?"
- "My payment was deducted but my order is still pending."
- "I want to return the shoes from order #100234."
- "Cancel my order #100234."

## Notes
This is an MVP and uses mock datasets for demonstration. It is intended as a portfolio project that shows an AI support agent architecture and business workflow patterns in a realistic ecommerce context.

## Security
Sensitive values should be stored in the local file `credentials.nv` and should not be committed to source control. The `.gitignore` file excludes this file from Git tracking.
