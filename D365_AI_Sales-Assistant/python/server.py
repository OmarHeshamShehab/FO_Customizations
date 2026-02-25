"""
server.py — FastAPI Web Server and API Endpoints
================================================
The entry point for the D365 Sales AI Assistant backend service.
Exposes HTTP endpoints that are called by the X++ form in F&O
and can also be tested directly via the browser or Postman.

Responsibilities:
  - FastAPI application setup and configuration
  - CORS middleware for cross-origin requests
  - Request/response model definitions
  - API endpoint routing and orchestration
  - Delegates all business logic to ai_engine.py and odata.py

Endpoints:
  GET  /health      — Health check, confirms server and model are running
  GET  /test-odata  — Tests OData connectivity, returns 3 sample records
  POST /ask         — Main endpoint, returns full JSON response with answer
  POST /ask-text    — Same as /ask but returns plain text only (used by X++)

Dependencies:
  - fastapi: Web framework
  - uvicorn: ASGI server (run with: uvicorn server:app --port 8000 --reload)
  - ai_engine.py: Intent detection, context fetching, prompt building, Ollama
  - odata.py: OData connectivity test

Running the server:
  cd C:\\Users\\localadmin\\Desktop\\D365AI\\python
  .venv\\Scripts\\activate
  uvicorn server:app --host 0.0.0.0 --port 8000 --reload

Environment:
  All configuration is loaded from .env via config.py
  Python 3.14+ compatible (no pinned package versions)
"""

import logging

from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from config import OLLAMA_MODEL, COMPANY
from odata import fetch_odata
from ai_engine import detect_intent, fetch_context, build_prompt, call_ollama

# ── LOGGING ───────────────────────────────────────────────────────────────────

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
log = logging.getLogger(__name__)


# ── APP SETUP ─────────────────────────────────────────────────────────────────

app = FastAPI(
    title="D365 Sales AI Assistant",
    version="1.0.0",
    description="AI-powered sales order assistant for Microsoft Dynamics 365 F&O"
)

# Allow all origins for VHD local development
# Restrict to specific origins in production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── REQUEST / RESPONSE MODELS ─────────────────────────────────────────────────

class AskRequest(BaseModel):
    """
    Request body for /ask and /ask-text endpoints.

    Fields:
        question       (str): Natural language question from the user (required)
        sales_order_id (str): Optional explicit order number e.g. '000697'
        customer_id    (str): Optional explicit customer account e.g. 'US-001'
    """
    question:       str
    sales_order_id: str = ""
    customer_id:    str = ""


class AskResponse(BaseModel):
    """
    Response body for /ask endpoint.

    Fields:
        answer    (str):  AI-generated answer in plain English
        question  (str):  Original question echoed back
        data_used (dict): Metadata about what data was fetched and used
    """
    answer:    str
    question:  str
    data_used: dict


# ── ENDPOINTS ─────────────────────────────────────────────────────────────────

@app.get("/health")
async def health():
    """
    Health check endpoint.
    Returns server status, configured model, and active company.
    Use this to verify the server is running before testing other endpoints.
    """
    return {
        "status":  "ok",
        "model":   OLLAMA_MODEL,
        "company": COMPANY
    }


@app.get("/test-odata")
async def test_odata():
    """
    OData connectivity test endpoint.
    Fetches 3 sample sales orders from D365 to verify authentication
    and OData connectivity are working correctly.

    If connected=false, check:
    1. F&O AOS is awake (open All Sales Orders in browser first)
    2. Azure AD credentials in .env are correct
    3. VPN or network connectivity to F&O
    """
    records = fetch_odata(
        "SalesOrderHeadersV2",
        select="SalesOrderNumber,SalesOrderStatus,OrderingCustomerAccountNumber",
        top=3
    )
    return {
        "connected": len(records) > 0,
        "sample":    records
    }


@app.post("/ask", response_model=AskResponse)
async def ask(req: AskRequest):
    """
    Main AI assistant endpoint — returns full JSON response.
    Use this endpoint for testing via Postman or the /docs UI.

    Flow:
        1. Detect intent from question + optional context fields
        2. Fetch relevant D365 data based on intent
        3. Build structured prompt with D365 data
        4. Call Ollama LLM and get answer
        5. Return answer with metadata
    """
    log.info(f"Question: {req.question}")

    intent  = detect_intent(req.question, req.sales_order_id, req.customer_id)
    context = fetch_context(intent)
    prompt  = build_prompt(req.question, context, intent)
    answer  = await call_ollama(prompt)

    return AskResponse(
        answer=answer,
        question=req.question,
        data_used={
            "intent":          intent,
            "order_found":     context.get("order") is not None,
            "backorders":      len(context.get("backorders", [])),
            "customer_orders": len(context.get("customer_orders", [])),
        }
    )


@app.post("/ask-text")
async def ask_text(req: AskRequest):
    """
    Plain text AI assistant endpoint — used by X++ in F&O.

    Returns the answer as plain text (text/plain) instead of JSON.
    This avoids the need for JSON parsing in X++ which has limited
    string handling capabilities and a 256 character str limit.

    The X++ SalesAIAssistantService class calls this endpoint directly
    and displays the response text in the AnswerDisplay form control.
    """
    log.info(f"Question (text): {req.question}")

    intent  = detect_intent(req.question, req.sales_order_id, req.customer_id)
    context = fetch_context(intent)
    prompt  = build_prompt(req.question, context, intent)
    answer  = await call_ollama(prompt)

    return Response(content=answer, media_type="text/plain")


# ── LOCAL DEV ENTRY POINT ─────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
