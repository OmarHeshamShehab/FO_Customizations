"""
ai_engine.py — D365 AI Sales & Revenue Intelligence
Builds sales performance prompts and calls Ollama qwen3:8b.
Async httpx pattern identical to Projects 1 & 2.
"""

import re
import logging
import asyncio
import httpx

from config import OLLAMA_URL, OLLAMA_MODEL

log = logging.getLogger(__name__)


# ── Warm-up (exact Projects 1 & 2 pattern) ───────────────────────────────────

async def warm_up_ollama():
    """Ping Ollama on startup — exact same pattern as Projects 1 & 2."""
    payload = {
        "model":      OLLAMA_MODEL,
        "messages":   [{"role": "user", "content": "hello"}],
        "stream":     False,
        "keep_alive": "10m",
        "options":    {"num_predict": 5},
    }
    try:
        log.info(f"Warming up Ollama: {OLLAMA_MODEL}")
        async with httpx.AsyncClient(timeout=300.0) as client:
            r = await client.post(f"{OLLAMA_URL}/api/chat", json=payload)
            if r.status_code == 200:
                log.info("Ollama warm-up complete")
            else:
                log.warning(f"Ollama warm-up status: {r.status_code}")
    except Exception as e:
        log.warning(f"Ollama warm-up failed (non-fatal): {e}")


# ── Ollama Call ───────────────────────────────────────────────────────────────

async def call_ollama(prompt: str) -> str:
    """
    Send prompt to Ollama, return clean response.
    Retries once if first attempt fails.
    Strips <think> tags from qwen3 output.
    """
    payload = {
        "model":      OLLAMA_MODEL,
        "messages":   [{"role": "user", "content": prompt}],
        "stream":     False,
        "think":      False,
        "keep_alive": "10m",
        "options":    {"temperature": 0.3, "num_predict": 400},
    }

    for attempt in range(2):
        try:
            if attempt == 1:
                log.info("Retrying Ollama after warm-up...")
                await warm_up_ollama()
                await asyncio.sleep(3)

            async with httpx.AsyncClient(timeout=300.0) as client:
                r = await client.post(f"{OLLAMA_URL}/api/chat", json=payload)
                if r.status_code == 200:
                    raw   = r.json().get("message", {}).get("content", "")
                    clean = re.sub(r"<think>.*?</think>", "", raw, flags=re.DOTALL).strip()
                    log.info(f"Ollama responded: {len(clean)} chars")
                    return clean or "AI narrative unavailable — empty response."
                log.error(f"Ollama {r.status_code}: {r.text[:200]}")

        except Exception as e:
            log.error(f"Ollama attempt {attempt + 1} failed: {e}")
            if attempt == 1:
                return f"Cannot reach Ollama after retry: {e}"

    return "Ollama did not respond. Check that Ollama is running."


# ── Prompt Builder ────────────────────────────────────────────────────────────

def build_sales_prompt(summary: dict) -> str:
    """Build Ollama prompt from sales performance summary."""
    customer_stats = summary["customer_stats"][:10]
    product_stats  = summary["product_stats"][:5]
    grand_total    = summary["grand_total"]
    total_customers = summary["total_customers"]
    total_orders   = summary["total_orders"]
    top_customer   = summary["top_customer"]
    top_product    = summary["top_product"]

    # Top 5 customers
    customer_lines = []
    for i, c in enumerate(customer_stats[:5], 1):
        customer_lines.append(
            f"  {i}. {c['customer_account']}: ${c['total_revenue']:,.0f} revenue, "
            f"{c['total_orders']} orders, {c['unique_products']} products, "
            f"Tier: {c['revenue_tier']}"
        )

    # Top 5 products
    product_lines = []
    for i, p in enumerate(product_stats, 1):
        product_lines.append(
            f"  {i}. {p['product_name']}: ${p['total_revenue']:,.0f} revenue, "
            f"{p['customer_count']} customers"
        )

    return f"""You are a senior sales analyst reviewing customer revenue and sales performance data for a company using Microsoft Dynamics 365.

OVERALL SALES PERFORMANCE:
  Total revenue    : ${grand_total:,.2f}
  Total customers  : {total_customers}
  Total orders     : {total_orders}
  Top customer     : {top_customer}
  Top product      : {top_product}

TOP 5 CUSTOMERS BY REVENUE:
{chr(10).join(customer_lines)}

TOP 5 PRODUCTS BY REVENUE:
{chr(10).join(product_lines)}

Write a concise executive sales performance summary (3-4 sentences) that:
1. States the overall revenue health and key concentration risks
2. Identifies the highest-value customers by name with specific revenue figures
3. Highlights the best performing products and their market reach
4. Recommends 1-2 specific actions to grow revenue or reduce concentration risk

Be direct, use the actual numbers. No disclaimers."""


# ── Narrative Pipeline ────────────────────────────────────────────────────────

async def generate_sales_narrative(summary: dict) -> str:
    """Build prompt -> call Ollama -> return narrative."""
    return await call_ollama(build_sales_prompt(summary))
