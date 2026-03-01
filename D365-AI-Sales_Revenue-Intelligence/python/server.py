"""
server.py — D365 AI Sales & Revenue Intelligence
==================================================
Four endpoints.

  GET  /health           — confirm server is running
  GET  /test-sales-data  — validate OData data vs SQL ground truth
  POST /ask-chart        — return sales dashboard HTML (original)
  GET  /dashboard        — return sales dashboard HTML for D365 iframe embedding

Run:
  uvicorn server:app --host 0.0.0.0 --port 8000 --reload
"""

import logging

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from config import OLLAMA_MODEL, COMPANY
from odata import fetch_sales_lines, summarise_sales_performance
from chart_engine import build_sales_dashboard_html
from ai_engine import generate_sales_narrative, warm_up_ollama

# ── Logging ───────────────────────────────────────────────────────────────────

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
log = logging.getLogger(__name__)


# ── App ───────────────────────────────────────────────────────────────────────

app = FastAPI(
    title="D365 AI Sales & Revenue Intelligence",
    version="1.0.0",
    description="AI-powered sales performance dashboard — D365 AI Series by Omar Hesham Shehab (OHMS Model)"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Startup ───────────────────────────────────────────────────────────────────

@app.on_event("startup")
async def startup_event():
    """
    Warm up Ollama on server start — exact same pattern as Projects 1 & 2.

    REMINDER: Wake AOS before calling /test-sales-data or /ask-chart.
    Navigate to: Accounts Receivable -> Inquiries -> Open transactions
    or any D365 page that triggers AOS activity.
    """
    log.info("Server starting — warming up Ollama...")
    log.info("REMINDER: Wake AOS — open any D365 page before calling OData endpoints")
    await warm_up_ollama()
    log.info("Server ready.")


# ── Models ────────────────────────────────────────────────────────────────────

class ChartRequest(BaseModel):
    question: str = "Show me the sales revenue dashboard"


# ── Endpoints ─────────────────────────────────────────────────────────────────

@app.get("/health")
async def health():
    """Confirm server is running. Check this first."""
    return {
        "status":  "ok",
        "model":   OLLAMA_MODEL,
        "company": COMPANY,
        "project": "D365 AI Sales & Revenue Intelligence v1.0",
    }


@app.get("/test-sales-data")
async def test_sales_data():
    """
    Validate OData data against SQL ground truth.
    match_customers must be true before building X++ components.
    """
    try:
        records = fetch_sales_lines()
        summary = summarise_sales_performance(records)

        return {
            "status":          "ok",
            "total_lines":     summary["total_lines"],
            "total_customers": summary["total_customers"],
            "total_orders":    summary["total_orders"],
            "grand_total":     summary["grand_total"],
            "top_customer":    summary["top_customer"],
            "top_product":     summary["top_product"],
            "top_5_customers": [
                {
                    "customer_account": c["customer_account"],
                    "total_revenue":    c["total_revenue"],
                    "total_orders":     c["total_orders"],
                    "unique_products":  c["unique_products"],
                    "revenue_tier":     c["revenue_tier"],
                    "revenue_pct":      c["revenue_pct"],
                }
                for c in summary["customer_stats"][:5]
            ],
            "top_5_products": [
                {
                    "item_number":    p["item_number"],
                    "product_name":   p["product_name"],
                    "total_revenue":  p["total_revenue"],
                    "customer_count": p["customer_count"],
                }
                for p in summary["product_stats"][:5]
            ],
            "validation": {
                "odata_customers":    summary["total_customers"],
                "odata_grand_total":  summary["grand_total"],
                "odata_top_customer": summary["top_customer"],
                "odata_top_product":  summary["top_product"],
                "match_customers":    summary["total_customers"] >= 25,
                "match_revenue":      summary["grand_total"] >= 99_000_000,
                "match_top_product":  "Projector" in summary["top_product"],
            }
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/ask-chart", response_class=HTMLResponse)
async def ask_chart(req: ChartRequest):
    """
    Original dashboard endpoint — POST version.
    Kept for backward compatibility and direct testing.
    """
    try:
        log.info("[/ask-chart] Request received")
        records = fetch_sales_lines()
        log.info(f"[/ask-chart] Fetched {len(records)} lines")
        if not records:
            return HTMLResponse(content=_error_html("No sales order lines found in USMF."))
        summary   = summarise_sales_performance(records)
        narrative = await generate_sales_narrative(summary)
        html      = build_sales_dashboard_html(summary, narrative)
        log.info("[/ask-chart] Dashboard built — returning HTML")
        return HTMLResponse(content=html)
    except Exception as e:
        log.error(f"[/ask-chart] Error: {e}", exc_info=True)
        return HTMLResponse(content=_error_html(str(e)), status_code=500)


@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard():
    """
    GET version of dashboard — used by D365 Extensible Control iframe.
    iframe src="http://localhost:8000/dashboard"
    Same logic as /ask-chart but accessible via GET so iframe can load it directly.
    This is the endpoint called by the D365 FO form.
    """
    try:
        log.info("[/dashboard] Request received")
        records = fetch_sales_lines()
        log.info(f"[/dashboard] Fetched {len(records)} lines")
        if not records:
            return HTMLResponse(content=_error_html("No sales order lines found in USMF."))
        summary   = summarise_sales_performance(records)
        narrative = await generate_sales_narrative(summary)
        html      = build_sales_dashboard_html(summary, narrative)
        log.info("[/dashboard] Dashboard built — returning HTML")
        return HTMLResponse(content=html)
    except Exception as e:
        log.error(f"[/dashboard] Error: {e}", exc_info=True)
        return HTMLResponse(content=_error_html(str(e)), status_code=500)


# ── Error page ────────────────────────────────────────────────────────────────

def _error_html(message: str) -> str:
    return f"""<!DOCTYPE html>
<html><head>
<style>
  body {{ font-family:'Segoe UI',sans-serif; display:flex; align-items:center;
          justify-content:center; height:100vh; background:#fff5f5; margin:0; }}
  .box {{ background:white; border-left:4px solid #7c3aed; padding:24px 32px;
          border-radius:8px; box-shadow:0 2px 8px rgba(0,0,0,.1); max-width:500px; }}
  h3 {{ color:#7c3aed; margin-bottom:8px; }}
  p  {{ color:#374151; font-size:14px; }}
</style>
</head><body>
<div class="box">
  <h3>⚠ Sales Intelligence Dashboard Error</h3>
  <p>{message}</p>
  <p style="margin-top:12px;font-size:12px;color:#9ca3af;">
    Check uvicorn terminal for full traceback.
  </p>
</div>
</body></html>"""


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
