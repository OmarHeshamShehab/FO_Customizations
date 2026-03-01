"""
odata.py — D365 AI Sales & Revenue Intelligence
Fetches sales order lines from SalesOrderLines OData entity.
Calculates revenue, product diversity, and order performance per customer.
OData entity confirmed working: SalesOrderLines
SQL ground truth validated: 58 customers, $110M+ revenue (USMF).
"""

import requests
import logging
from datetime import datetime
from config import (
    AAD_TENANT_ID,
    AAD_CLIENT_ID,
    AAD_CLIENT_SECRET,
    AAD_RESOURCE,
    LOGIN_URL,
    ODATA_BASE_URL,
    COMPANY,
)

log = logging.getLogger(__name__)


# ── Auth (exact Project 1 & 2 pattern) ───────────────────────────────────────

def get_token() -> str:
    """Acquire OAuth2 Bearer token — exact same pattern as Projects 1 & 2."""
    token_url = f"{LOGIN_URL}{AAD_TENANT_ID}/oauth2/token"
    data = {
        "grant_type":    "client_credentials",
        "client_id":     AAD_CLIENT_ID,
        "client_secret": AAD_CLIENT_SECRET,
        "resource":      AAD_RESOURCE,
    }
    try:
        r = requests.post(token_url, data=data, timeout=30)
        if r.status_code == 200:
            log.info("Token acquired successfully")
            return r.json().get("access_token")
        log.error(f"Token error {r.status_code}: {r.text[:300]}")
        return None
    except Exception as e:
        log.error(f"Token request failed: {e}")
        return None


# ── Fetch ─────────────────────────────────────────────────────────────────────

def fetch_sales_lines() -> list:
    """
    Fetch all sales order lines from SalesOrderLines for USMF.

    Returns list of dicts with:
        sales_order_num  : str   — e.g. '000002'
        customer_account : str   — e.g. 'US-007'
        item_number      : str   — product/item ID
        product_name     : str   — line description
        quantity         : float — ordered quantity
        unit_price       : float — sales price
        line_amount      : float — total line value in USD
        currency         : str   — currency code
        requested_date   : date  — requested receipt date
        line_status      : str   — Invoiced, Delivered, etc.
        category         : str   — product category
    """
    token = get_token()
    if not token:
        raise RuntimeError("Could not acquire Azure AD token — check .env credentials")

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept":        "application/json",
        "OData-Version": "4.0",
    }
    params = {
        "$filter": f"dataAreaId eq '{COMPANY}'",
        "$select": "SalesOrderNumber,SalesOrderLineStatus,ItemNumber,LineDescription,"
                   "OrderedSalesQuantity,SalesPrice,LineAmount,CurrencyCode,"
                   "RequestedReceiptDate,SalesProductCategoryName",
        "$top":    10000,
        "$expand": "SalesOrderHeader($select=OrderingCustomerAccountNumber,SalesOrderStatus)",
    }

    url        = f"{ODATA_BASE_URL}/SalesOrderLines"
    all_recs   = []
    first_call = True

    while url:
        r = requests.get(
            url,
            headers=headers,
            params=params if first_call else None,
            verify=False,
            timeout=300,
        )
        first_call = False

        if r.status_code != 200:
            raise RuntimeError(f"OData failed: {r.status_code} — {r.text[:300]}")

        page = r.json()
        all_recs.extend(page.get("value", []))
        log.info(f"Fetched {len(all_recs)} records so far...")
        url = page.get("@odata.nextLink")

    log.info(f"SalesOrderLines fetch complete: {len(all_recs)} records")

    result = []
    for rec in all_recs:
        try:
            date_raw = rec.get("RequestedReceiptDate", "")[:10]
            req_date = datetime.fromisoformat(date_raw).date()
            if req_date.year < 1990:
                req_date = None
        except (ValueError, TypeError):
            req_date = None

       # Get customer and order status from expanded header
        header        = rec.get("SalesOrderHeader") or {}
        customer_acc  = header.get("OrderingCustomerAccountNumber", "")
        header_status = header.get("SalesOrderStatus", "")

        # Skip non-invoiced lines
        line_status = rec.get("SalesOrderLineStatus", "")
        if line_status != "Invoiced":
            continue

        # Skip lines where header is not fully invoiced (matches SQL SALESSTATUS = 3)
        if header_status != "Invoiced":
            continue

        line_amount = float(rec.get("LineAmount", 0) or 0)
        if line_amount <= 0:
            continue

        result.append({
            "sales_order_num":  rec.get("SalesOrderNumber", ""),
            "customer_account": customer_acc,
            "item_number":      rec.get("ItemNumber", ""),
            "product_name":     rec.get("LineDescription", ""),
            "quantity":         float(rec.get("OrderedSalesQuantity", 0) or 0),
            "unit_price":       float(rec.get("SalesPrice", 0) or 0),
            "line_amount":      line_amount,
            "currency":         rec.get("CurrencyCode", "USD"),
            "requested_date":   req_date,
            "line_status":      rec.get("SalesOrderLineStatus", ""),
            "category":         rec.get("SalesProductCategoryName", ""),
        })

    return result


# ── Summarise ─────────────────────────────────────────────────────────────────

def summarise_sales_performance(records: list) -> dict:
    """
    Aggregate raw sales line records into dashboard-ready summary.

    Returns:
        customer_stats    : [ { customer_account, total_revenue, total_orders,
                                unique_products, unique_categories, avg_order_value,
                                revenue_tier } ]  sorted by total_revenue desc
        product_stats     : [ { item_number, product_name, total_revenue,
                                total_quantity, customer_count } ] sorted desc
        category_stats    : { category: { revenue, quantity, orders } }
        grand_total       : float
        total_customers   : int
        total_orders      : int
        total_lines       : int
        top_customer      : str
        top_product       : str
    """
    customer_map  = {}
    product_map   = {}
    category_map  = {}
    order_map     = {}  # track unique orders per customer

    for rec in records:
        acct     = rec["customer_account"]
        item     = rec["item_number"]
        cat      = rec["category"] or "Other"
        order    = rec["sales_order_num"]
        amount   = rec["line_amount"]
        qty      = rec["quantity"]
        pname    = rec["product_name"]

        if not acct:
            continue

        # ── Customer aggregation ──
        if acct not in customer_map:
            customer_map[acct] = {
                "customer_account": acct,
                "total_revenue":    0.0,
                "unique_products":  set(),
                "unique_categories": set(),
                "orders":           set(),
            }
        customer_map[acct]["total_revenue"]      += amount
        customer_map[acct]["unique_products"].add(item)
        customer_map[acct]["unique_categories"].add(cat)
        customer_map[acct]["orders"].add(order)

        # ── Product aggregation ──
        if item not in product_map:
            product_map[item] = {
                "item_number":    item,
                "product_name":   pname,
                "total_revenue":  0.0,
                "total_quantity": 0.0,
                "customers":      set(),
            }
        product_map[item]["total_revenue"]  += amount
        product_map[item]["total_quantity"] += qty
        product_map[item]["customers"].add(acct)

        # ── Category aggregation ──
        if cat not in category_map:
            category_map[cat] = {"revenue": 0.0, "quantity": 0.0, "orders": set()}
        category_map[cat]["revenue"]  += amount
        category_map[cat]["quantity"] += qty
        category_map[cat]["orders"].add(order)

    # ── Build customer stats ──
    grand_total   = sum(r["line_amount"] for r in records)
    customer_stats = []

    for acct, data in customer_map.items():
        total_rev  = data["total_revenue"]
        num_orders = len(data["orders"])
        avg_order  = total_rev / num_orders if num_orders > 0 else 0
        rev_pct    = (total_rev / grand_total * 100) if grand_total > 0 else 0

        customer_stats.append({
            "customer_account":   acct,
            "total_revenue":      round(total_rev, 2),
            "total_orders":       num_orders,
            "unique_products":    len(data["unique_products"]),
            "unique_categories":  len(data["unique_categories"]),
            "avg_order_value":    round(avg_order, 2),
            "revenue_pct":        round(rev_pct, 1),
            "revenue_tier":       _revenue_tier(total_rev),
        })

    customer_stats.sort(key=lambda x: x["total_revenue"], reverse=True)

    # ── Build product stats ──
    product_stats = []
    for item, data in product_map.items():
        product_stats.append({
            "item_number":    item,
            "product_name":   data["product_name"],
            "total_revenue":  round(data["total_revenue"], 2),
            "total_quantity": round(data["total_quantity"], 2),
            "customer_count": len(data["customers"]),
        })
    product_stats.sort(key=lambda x: x["total_revenue"], reverse=True)

    # ── Clean category stats ──
    clean_cats = {
        cat: {
            "revenue":  round(v["revenue"], 2),
            "quantity": round(v["quantity"], 2),
            "orders":   len(v["orders"]),
        }
        for cat, v in category_map.items()
    }

    total_orders = len(set(r["sales_order_num"] for r in records))

    return {
        "customer_stats":  customer_stats,
        "product_stats":   product_stats,
        "category_stats":  clean_cats,
        "grand_total":     round(grand_total, 2),
        "total_customers": len(customer_stats),
        "total_orders":    total_orders,
        "total_lines":     len(records),
        "top_customer":    customer_stats[0]["customer_account"] if customer_stats else "N/A",
        "top_product":     product_stats[0]["product_name"] if product_stats else "N/A",
    }


# ── Revenue Tier ──────────────────────────────────────────────────────────────

def _revenue_tier(revenue: float) -> str:
    """Classify customer by revenue tier."""
    if revenue >= 10_000_000:
        return "Platinum"
    elif revenue >= 5_000_000:
        return "Gold"
    elif revenue >= 1_000_000:
        return "Silver"
    else:
        return "Bronze"
