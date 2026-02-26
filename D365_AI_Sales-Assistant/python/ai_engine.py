"""
ai_engine.py — AI Intent Detection, Context Building, and Ollama Integration
=============================================================================
The brain of the Sales AI Assistant. Converts natural language questions
into structured D365 data queries, formats the data into prompts, and
calls the local Ollama LLM to generate business-friendly answers.

Responsibilities:
  - Intent detection: extracts order numbers, customer IDs, and question type
    from free-form natural language input
  - Context fetching: determines what D365 data is needed based on intent
    and fetches it via odata.py
  - Prompt building: formats D365 data into a structured prompt that guides
    the LLM to give accurate, professional business answers
  - Ollama integration: sends prompts to the local qwen3:8b model and
    returns the generated answer

Dependencies:
  - httpx: async HTTP client for Ollama API calls
  - odata.py: for fetching D365 data
  - config.py: Ollama URL and model name

Usage:
  from ai_engine import detect_intent, fetch_context, build_prompt, call_ollama, warm_up_ollama

  intent  = detect_intent("What is the status of order 000697?", "", "")
  context = fetch_context(intent)
  prompt  = build_prompt(question, context, intent)
  answer  = await call_ollama(prompt)

Notes:
  - think=False disables Ollama chain-of-thought mode for faster responses
  - Temperature is set to 0.2 for consistent, factual answers
  - num_predict=600 limits response length for concise business answers
  - Backorder filtering is done in Python because F&O OData enum filtering
    is not supported via URL parameters
  - Customer credit data (CreditLimit, PaymentTerms) is fetched from
    CustomersV3 entity when risk or credit questions are detected
  - Ollama model is kept warm via a keep-alive ping on startup
"""

import re
import logging
import asyncio
import httpx

from config import OLLAMA_URL, OLLAMA_MODEL, ODATA_BASE_URL, COMPANY
from odata import fetch_odata, fetch_odata_entity, HEADER_FIELDS

log = logging.getLogger(__name__)


# ── CUSTOMER FIELDS ───────────────────────────────────────────────────────────

# Fields fetched from CustomersV3 for credit and risk analysis
CUSTOMER_FIELDS = (
    "CustomerAccount,OrganizationName,CustomerGroupId,"
    "CreditLimit,CreditLimitIsMandatory,PaymentTerms,"
    "SalesCurrencyCode,OnHoldStatus,"
    "CredManCreditLimitExpiryDate,CredManAccountStatusId,"
    "CredManGroupId,CredManEligibleCreditMax"
)


# ── OLLAMA WARM-UP ────────────────────────────────────────────────────────────

async def warm_up_ollama():
    """
    Send a lightweight ping to Ollama on startup to load the model into memory.

    This prevents the first real request from timing out due to model load time.
    Called once during FastAPI startup. Failures are logged but not fatal.

    The keep_alive value of "10m" tells Ollama to keep the model in memory
    for 10 minutes after the last request, reducing cold-start delays.
    """
    payload = {
        "model":      OLLAMA_MODEL,
        "messages":   [{"role": "user", "content": "hello"}],
        "stream":     False,
        "keep_alive": "10m",
        "options":    {"num_predict": 5}
    }
    try:
        log.info(f"Warming up Ollama model: {OLLAMA_MODEL}")
        async with httpx.AsyncClient(timeout=300.0) as client:
            r = await client.post(f"{OLLAMA_URL}/api/chat", json=payload)
            if r.status_code == 200:
                log.info("Ollama warm-up complete — model loaded into memory")
            else:
                log.warning(f"Ollama warm-up returned status {r.status_code}")
    except Exception as e:
        log.warning(f"Ollama warm-up failed (non-fatal): {e}")


# ── INTENT DETECTION ──────────────────────────────────────────────────────────

def detect_intent(question, sales_order_id, customer_id):
    """
    Analyze the user's question to determine what data is needed.

    Extracts order numbers and customer IDs from natural language using
    regex patterns. Detects question type (order lookup, customer summary,
    backorder inquiry, recent orders, credit/risk analysis) using keyword matching.

    Args:
        question       (str): The user's natural language question
        sales_order_id (str): Explicit order ID passed from the form (optional)
        customer_id    (str): Explicit customer ID passed from the form (optional)

    Returns:
        dict: Intent dictionary with keys:
            - sales_order_id   (str):  Extracted or provided order number
            - customer_id      (str):  Extracted or provided customer account
            - fetch_order      (bool): True if a specific order should be fetched
            - fetch_customer   (bool): True if customer order history is needed
            - fetch_backorders (bool): True if backorder data is needed
            - fetch_recent     (bool): True if recent orders summary is needed
            - fetch_credit     (bool): True if customer credit/risk data is needed
    """
    q = question.lower()

    # Extract order number from question text if not explicitly provided
    # Matches patterns like 000697, 000002 etc.
    if not sales_order_id:
        m = re.search(r'\b0+\d{3,6}\b', question)
        if m:
            sales_order_id = m.group(0)

    # Extract customer account from question text if not explicitly provided
    # Matches patterns like US-001, DE-013 etc.
    if not customer_id:
        m = re.search(r'\b(us-\d{3}|de-\d{3})\b', question, re.IGNORECASE)
        if m:
            customer_id = m.group(0).upper()

    # Detect if credit or risk analysis is needed
    fetch_credit = any(w in q for w in [
        "credit", "risk", "limit", "payment terms", "cod",
        "overdue", "outstanding", "financial", "at risk",
        "credit limit", "owing", "debt"
    ])

    # Also fetch credit data whenever backorders are involved
    # because backorder + credit analysis is a common combined question
    fetch_backorders = any(w in q for w in [
        "backorder", "back order", "stuck", "delayed", "outstanding orders"
    ])

    if fetch_backorders:
        fetch_credit = True

    intent = {
        "sales_order_id":   sales_order_id,
        "customer_id":      customer_id,
        "fetch_order":      bool(sales_order_id),
        "fetch_customer":   bool(customer_id),
        "fetch_backorders": fetch_backorders,
        "fetch_recent":     any(w in q for w in [
            "recent", "latest", "last", "how many", "summary", "count", "overview"
        ]),
        "fetch_credit":     fetch_credit,
    }

    log.info(f"Intent detected: {intent}")
    return intent


# ── CONTEXT FETCHING ──────────────────────────────────────────────────────────

def fetch_context(intent):
    """
    Fetch all relevant D365 data based on the detected intent.

    Makes one or more OData calls depending on what data is needed.
    Multiple data types can be fetched in a single request cycle.

    Args:
        intent (dict): Intent dictionary from detect_intent()

    Returns:
        dict: Context dictionary with zero or more of these keys:
            - order           (dict): Single order record or None
            - customer_orders (list): List of orders for a customer
            - customer_id     (str):  Customer account number
            - backorders      (list): List of backorder records
            - recent_orders   (list): List of most recent orders
            - customers       (list): Customer master data with credit info

    Notes:
        - Backorders require fetching up to 5000 records and filtering in Python
          because F&O OData does not support enum value filtering in URL
        - Customer orders are sorted newest first (OrderCreationDateTime desc)
        - Credit data is fetched from CustomersV3 entity
    """
    context = {}

    # Fetch a specific sales order by order number
    if intent["fetch_order"] and intent["sales_order_id"]:
        records = fetch_odata(
            "SalesOrderHeadersV2",
            filters=f"SalesOrderNumber eq '{intent['sales_order_id']}'",
            select=HEADER_FIELDS,
            top=1
        )
        context["order"] = records[0] if records else None
        log.info(f"Order fetch: {'found' if context['order'] else 'not found'}")

    # Fetch all orders for a specific customer account
    if intent["fetch_customer"] and intent["customer_id"]:
        records = fetch_odata(
            "SalesOrderHeadersV2",
            filters=f"OrderingCustomerAccountNumber eq '{intent['customer_id']}'",
            select=HEADER_FIELDS,
            top=50,
            orderby="OrderCreationDateTime desc"
        )
        context["customer_orders"] = records
        context["customer_id"]     = intent["customer_id"]
        log.info(f"Customer orders: {len(records)} orders for {intent['customer_id']}")

    # Fetch all orders and filter backorders in Python
    # (OData enum filtering not supported for SalesOrderStatus)
    if intent["fetch_backorders"]:
        all_orders = fetch_odata(
            "SalesOrderHeadersV2",
            select=HEADER_FIELDS,
            top=5000
        )
        backorders = [o for o in all_orders if o.get("SalesOrderStatus") == "Backorder"]
        log.info(f"Backorders: {len(backorders)} from {len(all_orders)} total orders")

        # Further filter by customer if one was specified
        if intent["customer_id"]:
            backorders = [
                o for o in backorders
                if o.get("OrderingCustomerAccountNumber") == intent["customer_id"]
            ]

        context["backorders"] = backorders

    # Fetch most recent orders for summary questions
    if intent["fetch_recent"] and not intent["fetch_order"] and not intent["fetch_customer"]:
        records = fetch_odata(
            "SalesOrderHeadersV2",
            select=HEADER_FIELDS,
            top=20,
            orderby="OrderCreationDateTime desc"
        )
        context["recent_orders"] = records
        log.info(f"Recent orders: {len(records)} orders")

    # Fetch customer credit and master data for risk/credit questions
    if intent["fetch_credit"]:
        # If specific customer requested fetch only that customer
        if intent["customer_id"]:
            filters = f"dataAreaId eq '{COMPANY}' and CustomerAccount eq '{intent['customer_id']}'"
        else:
            filters = f"dataAreaId eq '{COMPANY}'"

        customers = fetch_odata_entity(
            "CustomersV3",
            filters=filters,
            select=CUSTOMER_FIELDS,
            top=100
        )
        context["customers"] = customers
        log.info(f"Customer credit data: {len(customers)} customers fetched")

    return context


# ── PROMPT BUILDER ────────────────────────────────────────────────────────────

def build_prompt(question, context, intent):
    """
    Build a structured prompt for the Ollama LLM.

    Combines system instructions with formatted D365 data and the user's
    question. The prompt is designed to guide the model to give concise,
    accurate, business-appropriate answers based only on provided data.

    Args:
        question (str):  The user's original question
        context  (dict): Data fetched from D365 via fetch_context()
        intent   (dict): Intent dictionary from detect_intent()

    Returns:
        str: Complete prompt string ready to send to Ollama
    """
    # System instructions that define the AI assistant's behavior
    system = """You are a helpful sales assistant for a business using Microsoft Dynamics 365.
Answer questions about sales orders clearly and professionally.
RULES:
- Base your answer ONLY on the data provided. Never invent values.
- If data is missing say so clearly.
- Be concise. A sales rep needs quick clear answers.
- Format dates in readable form e.g. December 7 2016 not 2016-12-07T08:52:45Z.
- Never show raw field names or JSON in your answer.
- Use business language.
- When analyzing risk consider: number of backorders, credit limit, payment terms, and on-hold status.
- For credit limit of 0 this means no credit limit is set not that the limit is zero.
"""
    data = "\n\nDATA FROM DYNAMICS 365:\n"

    # Single order details
    if context.get("order"):
        o = context["order"]
        data += f"""
ORDER DETAILS:
  Order Number  : {o.get('SalesOrderNumber')}
  Customer      : {o.get('OrderingCustomerAccountNumber')} - {o.get('SalesOrderName')}
  Status        : {o.get('SalesOrderStatus')}
  Processing    : {o.get('SalesOrderProcessingStatus')}
  Created       : {o.get('OrderCreationDateTime')}
  Requested Ship: {o.get('RequestedShippingDate')}
  Confirmed Ship: {o.get('ConfirmedShippingDate')}
  Currency      : {o.get('CurrencyCode')}
  Payment Terms : {o.get('PaymentTermsName')}
  Payment Method: {o.get('CustomerPaymentMethodName')}
  Delivery Mode : {o.get('DeliveryModeCode')}
  Delivery Terms: {o.get('DeliveryTermsCode')}
  Origin        : {o.get('SalesOrderOriginCode')}
  Ship To       : {o.get('DeliveryAddressName')}, {o.get('DeliveryAddressCity')}, {o.get('DeliveryAddressStateId')}
"""
    elif intent.get("sales_order_id"):
        data += f"\nOrder {intent['sales_order_id']} was not found.\n"

    # Customer order history summary
    if context.get("customer_orders") is not None:
        orders  = context["customer_orders"]
        cust_id = context.get("customer_id", "")

        # Calculate status breakdown
        counts = {}
        for o in orders:
            s = o.get("SalesOrderStatus", "Unknown")
            counts[s] = counts.get(s, 0) + 1

        # Calculate date range
        dates  = [o.get("OrderCreationDateTime", "") for o in orders if o.get("OrderCreationDateTime")]
        oldest = min(dates)[:10] if dates else "N/A"
        newest = max(dates)[:10] if dates else "N/A"

        data += f"""
CUSTOMER {cust_id} ORDER HISTORY:
  Total Orders    : {len(orders)}
  Status Breakdown: {', '.join(f'{v} {k}' for k, v in counts.items())}
  Date Range      : {oldest} to {newest}
  Currency        : {orders[0].get('CurrencyCode') if orders else 'N/A'}
  Payment Terms   : {orders[0].get('PaymentTermsName') if orders else 'N/A'}
  Recent Orders:
"""
        # Show up to 8 most recent orders
        for o in orders[:8]:
            data += f"    {o.get('SalesOrderNumber')} | {o.get('SalesOrderStatus')} | {o.get('OrderCreationDateTime','')[:10]}\n"
        if len(orders) > 8:
            data += f"    ... and {len(orders)-8} more\n"

    # Backorder summary grouped by customer
    if context.get("backorders") is not None:
        backorders = context["backorders"]
        data += f"\nBACKORDERS:\n  Total: {len(backorders)}\n"

        if backorders:
            # Group backorders by customer account
            by_cust = {}
            for o in backorders:
                c = o.get("OrderingCustomerAccountNumber", "Unknown")
                by_cust.setdefault(c, []).append(o.get("SalesOrderNumber"))

            # Sort by number of backorders descending so worst customers appear first
            # Only include customers with more than 1 backorder to keep prompt concise
            filtered = {c: nums for c, nums in by_cust.items() if len(nums) > 1}
            for cust, nums in sorted(filtered.items(), key=lambda x: len(x[1]), reverse=True):
                sample = ', '.join(nums[:3]) + ('...' if len(nums) > 3 else '')
                data += f"  {cust}: {len(nums)} backorders ({sample})\n"

            if not filtered:
                # Fall back to all if none have >1
                for cust, nums in sorted(by_cust.items(), key=lambda x: len(x[1]), reverse=True):
                    sample = ', '.join(nums[:3]) + ('...' if len(nums) > 3 else '')
                    data += f"  {cust}: {len(nums)} backorders ({sample})\n"
        else:
            data += "  No backorders found.\n"

    # Recent orders summary
    if context.get("recent_orders"):
        orders = context["recent_orders"]
        counts = {}
        for o in orders:
            s = o.get("SalesOrderStatus", "Unknown")
            counts[s] = counts.get(s, 0) + 1

        data += f"\nRECENT ORDERS (latest {len(orders)}):\n"
        data += f"  Status Mix: {', '.join(f'{v} {k}' for k, v in counts.items())}\n"

        for o in orders[:10]:
            data += (
                f"  {o.get('SalesOrderNumber')} | "
                f"{o.get('OrderingCustomerAccountNumber')} | "
                f"{o.get('SalesOrderStatus')} | "
                f"{o.get('OrderCreationDateTime','')[:10]}\n"
            )

    # Customer credit and master data
    if context.get("customers"):
        # If backorders exist, only show credit data for customers who have backorders
        # This keeps the prompt concise and focused
        backorder_customers = set()
        if context.get("backorders"):
            for o in context["backorders"]:
                backorder_customers.add(o.get("OrderingCustomerAccountNumber", ""))

        customers_to_show = context["customers"]
        if backorder_customers:
            customers_to_show = [
                c for c in context["customers"]
                if c.get("CustomerAccount") in backorder_customers
            ]
            # Fall back to all if filter produces nothing
            if not customers_to_show:
                customers_to_show = context["customers"]

        data += "\nCUSTOMER CREDIT AND MASTER DATA:\n"
        for c in customers_to_show:
            credit_limit = c.get("CreditLimit", 0)
            credit_display = "No limit set" if credit_limit == 0 else f"{credit_limit:,.2f}"
            data += (
                f"  {c.get('CustomerAccount')} | "
                f"Name: {c.get('OrganizationName')} | "
                f"Group: {c.get('CustomerGroupId')} | "
                f"Currency: {c.get('SalesCurrencyCode')} | "
                f"Payment Terms: {c.get('PaymentTerms')} | "
                f"Credit Limit: {credit_display} | "
                f"On Hold: {c.get('OnHoldStatus')} | "
                f"Credit Status: {c.get('CredManAccountStatusId')}\n"
            )

    return f"{system}{data}\n\nQUESTION: {question}\n\nAnswer:"


# ── OLLAMA INTEGRATION ────────────────────────────────────────────────────────

async def call_ollama(prompt):
    """
    Send a prompt to the local Ollama LLM and return the generated answer.

    Uses async httpx for non-blocking HTTP calls. Connects to the locally
    running Ollama service on localhost:11434.

    Includes automatic retry logic: if the first attempt fails, the model
    is re-warmed and one retry is attempted before returning an error.

    Args:
        prompt (str): Complete prompt string from build_prompt()

    Returns:
        str: Generated answer text from the LLM
             Error message string if Ollama is unreachable after retry

    Model settings:
        - model:       qwen3:8b (configured in config.py)
        - think:       False — disables chain-of-thought for faster responses
        - temperature: 0.2 — low for consistent, factual business answers
        - num_predict: 600 — limits response length for concise answers
        - keep_alive:  10m — keeps model in memory between requests
    """
    payload = {
        "model":      OLLAMA_MODEL,
        "messages":   [{"role": "user", "content": prompt}],
        "stream":     False,
        "think":      False,
        "keep_alive": "10m",
        "options":    {
            "temperature": 0.2,
            "num_predict": 600
        }
    }

    for attempt in range(2):  # Try twice — second attempt after re-warm
        try:
            if attempt == 1:
                log.info("Retrying Ollama after warm-up pause...")
                await warm_up_ollama()
                await asyncio.sleep(3)

            async with httpx.AsyncClient(timeout=300.0) as client:
                r = await client.post(f"{OLLAMA_URL}/api/chat", json=payload)

                if r.status_code == 200:
                    answer = r.json().get("message", {}).get("content", "No response.")
                    log.info(f"Ollama responded with {len(answer)} characters")
                    return answer

                log.error(f"Ollama error {r.status_code}: {r.text[:200]}")

        except Exception as e:
            log.error(f"Ollama attempt {attempt + 1} failed: {e}")
            if attempt == 1:
                return f"Cannot reach Ollama after retry: {e}"

    return "Ollama did not respond after retry. Please check that Ollama is running."
