"""
chart_engine.py — D365 AI Sales & Revenue Intelligence
Builds Chart.js HTML visualisations from sales performance summary.
Single self-contained HTML string for D365 WebControl rendering.
All styles are INLINE — D365 strips <style> blocks, inline styles survive sandboxing.
Chart.js loaded from D365 AOT resource: /resources/scripts/SalesIntelligenceChartJS.js
"""

import re

# ── Helpers ───────────────────────────────────────────────────────────────────

def _safe_label(text: str) -> str:
    """Escape quotes/backslashes so the label is safe inside a JS double-quoted string."""
    return text.replace("\\", "\\\\").replace('"', '\\"').replace("'", "\\'")

# ── Tier Colours ──────────────────────────────────────────────────────────────

TIER_COLOURS = {
    "Platinum": "#7c3aed",
    "Gold":     "#d97706",
    "Silver":   "#6b7280",
    "Bronze":   "#92400e",
}

# ── Inline Style Constants ────────────────────────────────────────────────────

S = {
    "body":           "font-family:'Segoe UI',Tahoma,Geneva,Verdana,sans-serif;background:#f8f9fa;color:#212529;padding:16px;margin:0;box-sizing:border-box;",
    "h2":             "font-size:20px;font-weight:600;color:#1a1a2e;margin:0 0 4px 0;",
    "subtitle":       "font-size:12px;color:#6c757d;margin:0 0 16px 0;",
    "stats_bar":      "display:flex;gap:12px;margin-bottom:20px;flex-wrap:wrap;",
    "stat_card":      "background:white;border-radius:8px;padding:12px 18px;flex:1;min-width:140px;box-shadow:0 1px 4px rgba(0,0,0,0.08);border-left:4px solid #7c3aed;",
    "stat_card_gold": "background:white;border-radius:8px;padding:12px 18px;flex:1;min-width:140px;box-shadow:0 1px 4px rgba(0,0,0,0.08);border-left:4px solid #d97706;",
    "stat_card_grn":  "background:white;border-radius:8px;padding:12px 18px;flex:1;min-width:140px;box-shadow:0 1px 4px rgba(0,0,0,0.08);border-left:4px solid #22c55e;",
    "stat_card_blu":  "background:white;border-radius:8px;padding:12px 18px;flex:1;min-width:140px;box-shadow:0 1px 4px rgba(0,0,0,0.08);border-left:4px solid #3b82f6;",
    "stat_label":     "font-size:11px;color:#6c757d;text-transform:uppercase;letter-spacing:0.5px;margin:0;",
    "stat_value":     "font-size:20px;font-weight:700;color:#1a1a2e;margin:2px 0 0 0;",
    "stat_value_sm":  "font-size:14px;font-weight:700;color:#1a1a2e;margin:2px 0 0 0;",
    "stat_sub":       "font-size:11px;color:#6c757d;margin:2px 0 0 0;",
    "chart_section":  "background:white;border-radius:8px;padding:16px;box-shadow:0 1px 4px rgba(0,0,0,0.08);margin-bottom:16px;",
    "chart_section0": "background:white;border-radius:8px;padding:16px;box-shadow:0 1px 4px rgba(0,0,0,0.08);margin-bottom:0;",
    "chart_title":    "font-size:14px;font-weight:600;color:#374151;margin:0 0 12px 0;padding-bottom:8px;border-bottom:1px solid #f0f0f0;",
    "chart_cont":     "position:relative;height:320px;",
    "chart_cont_md":  "position:relative;height:280px;",
    "charts_row":     "display:grid;grid-template-columns:2fr 1fr;gap:16px;margin-bottom:16px;",
    "tier_legend":    "display:flex;gap:16px;margin-top:8px;flex-wrap:wrap;margin-bottom:0;",
    "tier_item":      "display:flex;align-items:center;gap:6px;font-size:11px;color:#6c757d;margin:0;",
    "tier_dot":       "width:10px;height:10px;border-radius:50%;display:inline-block;",
    "narrative":      "background:#1a1a2e;color:#e2e8f0;border-radius:8px;padding:16px;margin-bottom:16px;box-shadow:0 1px 4px rgba(0,0,0,0.15);",
    "narr_title":     "font-size:13px;font-weight:600;color:#94a3b8;text-transform:uppercase;letter-spacing:0.5px;margin:0 0 10px 0;",
    "narr_text":      "font-size:13px;line-height:1.7;color:#cbd5e1;margin:0;",
    "footer":         "font-size:11px;color:#adb5bd;text-align:center;margin-top:8px;",
}


# ── Main Entry Point ──────────────────────────────────────────────────────────

def build_sales_dashboard_html(summary: dict, narrative: str = "") -> str:
    stats_html     = _build_stats_bar(summary)
    chart1_js      = _build_customer_revenue_chart(summary["customer_stats"][:15])
    chart2_js      = _build_product_revenue_chart(summary["product_stats"][:10])
    chart3_js      = _build_category_chart(summary["category_stats"])
    narrative_html = _build_narrative_section(narrative) if narrative else ""

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>D365 AI Sales &amp; Revenue Intelligence</title>
  <style>* {{ box-sizing: border-box; margin: 0; padding: 0; }}</style>
  <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
</head>
<body style="{S['body']}">

  <h2 style="{S['h2']}">AI Sales &amp; Revenue Intelligence</h2>
  <p style="{S['subtitle']}">Customer Sales Performance Analysis — USMF | Live data via D365 OData</p>

  {stats_html}

  <div style="{S['chart_section']}">
    <div style="{S['chart_title']}">&#x1F4B0; Top 15 Customers by Revenue</div>
    <div style="{S['tier_legend']}">
      <div style="{S['tier_item']}"><span style="{S['tier_dot']}background:#7c3aed;"></span>&nbsp;Platinum ($10M+)</div>
      <div style="{S['tier_item']}"><span style="{S['tier_dot']}background:#d97706;"></span>&nbsp;Gold ($5M-$10M)</div>
      <div style="{S['tier_item']}"><span style="{S['tier_dot']}background:#6b7280;"></span>&nbsp;Silver ($1M-$5M)</div>
      <div style="{S['tier_item']}"><span style="{S['tier_dot']}background:#92400e;"></span>&nbsp;Bronze (under $1M)</div>
    </div>
    <br>
    <div style="{S['chart_cont']}">
      <canvas id="customerChart"></canvas>
    </div>
  </div>

  <div style="{S['charts_row']}">
    <div style="{S['chart_section0']}">
      <div style="{S['chart_title']}">&#x1F4E6; Top 10 Products by Revenue</div>
      <div style="{S['chart_cont_md']}">
        <canvas id="productChart"></canvas>
      </div>
    </div>
    <div style="{S['chart_section0']}">
      <div style="{S['chart_title']}">&#x1F5C2;&#xFE0F; Revenue by Category</div>
      <div style="{S['chart_cont_md']}">
        <canvas id="categoryChart"></canvas>
      </div>
    </div>
  </div>

  <br>
  {narrative_html}

  <p style="{S['footer']}">D365 AI Sales &amp; Revenue Intelligence &middot; OHMS Model &middot; Omar Hesham Shehab</p>

  <script>
    function initCharts() {{
      var canvases = ['customerChart', 'productChart', 'categoryChart'];
      var ready = canvases.every(function(id) {{
        return document.getElementById(id) !== null;
      }});
      if (!ready || typeof Chart === 'undefined') {{
        setTimeout(initCharts, 100);
        return;
      }}
      {chart1_js}
      {chart2_js}
      {chart3_js}
    }}
    if (document.readyState === 'loading') {{
      document.addEventListener('DOMContentLoaded', function() {{ setTimeout(initCharts, 200); }});
    }} else {{
      setTimeout(initCharts, 200);
    }}
  </script>

</body>
</html>"""


# ── Chart 1 — Customer Revenue ────────────────────────────────────────────────

def _build_customer_revenue_chart(customer_stats: list) -> str:
    labels  = []
    values  = []
    colours = []

    for c in customer_stats:
        labels.append(f'"{_safe_label(c["customer_account"])}"')
        values.append(round(c["total_revenue"], 0))
        colours.append(f'"{TIER_COLOURS[c["revenue_tier"]]}"')

    return f"""
    new Chart(document.getElementById('customerChart'), {{
      type: 'bar',
      data: {{
        labels: [{", ".join(labels)}],
        datasets: [{{
          label: 'Total Revenue (USD)',
          data: [{", ".join(str(v) for v in values)}],
          backgroundColor: [{", ".join(colours)}],
          borderRadius: 4,
        }}]
      }},
      options: {{
        indexAxis: 'y',
        responsive: true,
        maintainAspectRatio: false,
        plugins: {{
          legend: {{ display: false }},
          tooltip: {{
            callbacks: {{
              label: ctx => ' $' + ctx.parsed.x.toLocaleString('en-US', {{minimumFractionDigits: 0}})
            }}
          }}
        }},
        scales: {{
          x: {{
            ticks: {{ callback: val => '$' + (val/1000000).toFixed(1) + 'M' }},
            grid: {{ color: '#f0f0f0' }}
          }},
          y: {{ grid: {{ display: false }} }}
        }}
      }}
    }});
    """


# ── Chart 2 — Product Revenue ─────────────────────────────────────────────────

def _build_product_revenue_chart(product_stats: list) -> str:
    labels = []
    values = []

    for p in product_stats:
        name = p["product_name"][:20] if p["product_name"] else p["item_number"]
        labels.append(f'"{_safe_label(name)}"')
        values.append(round(p["total_revenue"], 0))

    return f"""
    new Chart(document.getElementById('productChart'), {{
      type: 'bar',
      data: {{
        labels: [{", ".join(labels)}],
        datasets: [{{
          label: 'Revenue (USD)',
          data: [{", ".join(str(v) for v in values)}],
          backgroundColor: '#3b82f6',
          borderRadius: 4,
        }}]
      }},
      options: {{
        indexAxis: 'y',
        responsive: true,
        maintainAspectRatio: false,
        plugins: {{
          legend: {{ display: false }},
          tooltip: {{
            callbacks: {{
              label: ctx => ' $' + ctx.parsed.x.toLocaleString('en-US')
            }}
          }}
        }},
        scales: {{
          x: {{
            ticks: {{ callback: val => '$' + (val/1000000).toFixed(1) + 'M' }},
            grid: {{ color: '#f0f0f0' }}
          }},
          y: {{ grid: {{ display: false }} }}
        }}
      }}
    }});
    """


# ── Chart 3 — Category Doughnut ───────────────────────────────────────────────

def _build_category_chart(category_stats: dict) -> str:
    sorted_cats = sorted(category_stats.items(), key=lambda x: x[1]["revenue"], reverse=True)

    labels  = []
    values  = []
    colours = [
        "#7c3aed", "#3b82f6", "#22c55e", "#f97316",
        "#ec4899", "#14b8a6", "#d97706", "#6b7280",
        "#dc2626", "#0ea5e9"
    ]

    for cat, data in sorted_cats:
        labels.append(f'"{_safe_label(cat)}"')
        values.append(round(data["revenue"], 0))

    colours_js = ", ".join(f'"{c}"' for c in colours[:len(labels)])

    return f"""
    new Chart(document.getElementById('categoryChart'), {{
      type: 'doughnut',
      data: {{
        labels: [{", ".join(labels)}],
        datasets: [{{
          data: [{", ".join(str(v) for v in values)}],
          backgroundColor: [{colours_js}],
          borderWidth: 2,
          borderColor: '#fff',
        }}]
      }},
      options: {{
        responsive: true,
        maintainAspectRatio: false,
        plugins: {{
          legend: {{
            position: 'bottom',
            labels: {{ boxWidth: 10, font: {{ size: 10 }} }}
          }},
          tooltip: {{
            callbacks: {{
              label: ctx => ' $' + ctx.parsed.toLocaleString('en-US')
            }}
          }}
        }}
      }}
    }});
    """


# ── Stats Bar ─────────────────────────────────────────────────────────────────

def _build_stats_bar(summary: dict) -> str:
    total       = summary["grand_total"]
    customers   = summary["total_customers"]
    orders      = summary["total_orders"]
    top_cust    = summary["top_customer"]
    top_product = summary["top_product"]

    top_stats   = summary["customer_stats"][0] if summary["customer_stats"] else {}
    top_rev     = top_stats.get("total_revenue", 0)
    top_pct     = top_stats.get("revenue_pct", 0)

    return f"""
    <div style="{S['stats_bar']}">
      <div style="{S['stat_card']}">
        <p style="{S['stat_label']}">Total Revenue</p>
        <p style="{S['stat_value']}">${total/1_000_000:.1f}M</p>
        <p style="{S['stat_sub']}">{customers} customers | {orders} orders</p>
      </div>
      <div style="{S['stat_card_gold']}">
        <p style="{S['stat_label']}">Top Customer</p>
        <p style="{S['stat_value']}">{top_cust}</p>
        <p style="{S['stat_sub']}">${top_rev/1_000_000:.1f}M — {top_pct}% of total</p>
      </div>
      <div style="{S['stat_card_grn']}">
        <p style="{S['stat_label']}">Top Product</p>
        <p style="{S['stat_value_sm']}">{top_product[:20]}</p>
        <p style="{S['stat_sub']}">by total revenue</p>
      </div>
      <div style="{S['stat_card_blu']}">
        <p style="{S['stat_label']}">Avg Order Value</p>
        <p style="{S['stat_value']}">${total/orders/1000:.1f}K</p>
        <p style="{S['stat_sub']}">across all customers</p>
      </div>
    </div>
    """


# ── Narrative Section ─────────────────────────────────────────────────────────

def _build_narrative_section(narrative: str) -> str:
    clean = re.sub(r"<think>.*?</think>", "", narrative, flags=re.DOTALL).strip()
    clean = clean.replace("\n", "<br>")
    return f"""
    <div style="{S['narrative']}">
      <p style="{S['narr_title']}">&#x1F916; AI Sales Intelligence</p>
      <p style="{S['narr_text']}">{clean}</p>
    </div>
    """
