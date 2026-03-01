# D365 AI Sales & Revenue Intelligence Dashboard

> **OHMS Model — Omar Hesham Shehab**  
> Part of the D365 AI Series | Microsoft Dynamics 365 Finance & Operations

An AI-powered, fully embedded sales revenue intelligence dashboard built as a **custom Extensible Control** inside Microsoft Dynamics 365 F&O. The dashboard fetches live invoiced sales data from D365 via OData, aggregates it in Python, renders three interactive Chart.js charts, and generates an executive AI narrative using a locally running Ollama LLM — all rendered natively inside a D365 form with zero external browser dependencies.

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [System Architecture](#2-system-architecture)
3. [Data Flow — End to End](#3-data-flow--end-to-end)
4. [Repository Structure](#4-repository-structure)
5. [D365 AOT Project Structure](#5-d365-aot-project-structure)
6. [Component Deep Dive](#6-component-deep-dive)
   - [SalesIntelligenceControl.htm](#61-salesintelligencecontrolhtm)
   - [SalesIntelligenceControlScript.js](#62-salesintelligencecontrolscriptjs)
   - [SalesIntelligenceChartJS.js](#63-salesintelligencechartjsjs)
   - [SalesIntelligenceDashboard (Form)](#64-salesintelligencedashboard-form)
   - [SalesIntelligenceControl (X++ Class)](#65-salesintelligencecontrol-x-class)
   - [SalesIntelligenceControlBuild (X++ Class)](#66-salesintelligencecontrolbuild-x-class)
   - [SalesIntelligenceService (X++ Class)](#67-salesintelligenceservice-x-class)
   - [SalesIntelligenceTest (X++ Runnable Class)](#68-salesintelligencetest-x-runnable-class)
7. [Python Service Layer](#7-python-service-layer)
   - [server.py](#71-serverpy)
   - [odata.py](#72-odatapy)
   - [chart_engine.py](#73-chart_enginepy)
   - [ai_engine.py](#74-ai_enginepy)
   - [config.py](#75-configpy)
8. [Prerequisites](#8-prerequisites)
9. [Installation & Setup](#9-installation--setup)
10. [Configuration — .env File](#10-configuration--env-file)
11. [AOT Resource Deployment](#11-aot-resource-deployment)
12. [Running the Python Server](#12-running-the-python-server)
13. [API Endpoints](#13-api-endpoints)
14. [Data Validation & SQL Ground Truth](#14-data-validation--sql-ground-truth)
15. [Revenue Tier Classification](#15-revenue-tier-classification)
16. [Technical Notes & Gotchas](#16-technical-notes--gotchas)
17. [Troubleshooting](#17-troubleshooting)

---

## 1. Project Overview

This project solves a real problem: **D365 F&O has no native AI-powered sales analytics dashboard**. The standard D365 reporting tools (SSRS, Power BI embedded) require separate licensing, infrastructure, and configuration. This solution delivers a fully self-contained AI dashboard that:

- Reads **live invoiced sales data** directly from D365 via OData — no data exports, no ETL pipelines
- Filters to **fully invoiced orders only** (header status = Invoiced AND line status = Invoiced) for financial accuracy
- Aggregates revenue by customer, product, and category in Python
- Renders **three interactive Chart.js charts** natively inside a D365 form
- Generates an **AI executive narrative** using a locally running `qwen3:8b` model via Ollama
- Is **entirely embedded** in D365 as a custom Extensible Control — no iframe, no popup, no external browser tab

**Validated data (USMF company):**
- Total Revenue: **$99,451,085.50**
- Total Customers: **29**
- Total Orders: **708**
- Top Customer: **DE-001** ($7.66M)
- Top Product: **Projector Television** ($34.9M)

---

## 2. System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    D365 F&O (AOS / Browser)                     │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │           SalesIntelligenceDashboard (Form)              │   │
│  │                                                          │   │
│  │   [Generate Dashboard Button]                            │   │
│  │        │                                                 │   │
│  │        ▼ DashboardControl.loadDashboard()                │   │
│  │   ┌──────────────────────────────────────────────┐       │   │
│  │   │   SalesIntelligenceControl (Extensible Ctrl) │       │   │
│  │   │                                              │       │   │
│  │   │   SalesIntelligenceControl.htm               │       │   │
│  │   │   └── #SalesIntelligenceDashboardContainer   │       │   │
│  │   │                                              │       │   │
│  │   │   SalesIntelligenceControlScript.js          │       │   │
│  │   │   └── Observes HtmlContent observable        │       │   │
│  │   │   └── Injects HTML into container div        │       │   │
│  │   │   └── Extracts & re-executes <script> tags   │       │   │
│  │   │   └── Loads Chart.js from AOT resource       │       │   │
│  │   │                                              │       │   │
│  │   │   SalesIntelligenceChartJS.js (AOT Resource) │       │   │
│  │   │   └── Chart.js v4.4.0 UMD build              │       │   │
│  │   └──────────────────────────────────────────────┘       │   │
│  └──────────────────────────────────────────────────────────┘   │
│                        │                                        │
│              X++ HTTP call (SalesIntelligenceService)           │
└────────────────────────┼────────────────────────────────────────┘
                         │
                         ▼ POST /ask-chart
┌─────────────────────────────────────────────────────────────────┐
│                   Python FastAPI Server (:8000)                  │
│                                                                 │
│   server.py ──► odata.py ──► D365 OData API                    │
│                    │                                            │
│                    ▼ (filtered, aggregated records)             │
│              chart_engine.py ──► HTML + Chart.js config         │
│                    │                                            │
│                    ▼                                            │
│              ai_engine.py ──► Ollama (qwen3:8b) ──► Narrative   │
│                    │                                            │
│                    ▼                                            │
│         Complete HTML string returned to X++                   │
└─────────────────────────────────────────────────────────────────┘
                         │
                         ▼ OAuth2 client_credentials
┌─────────────────────────────────────────────────────────────────┐
│                  Azure Active Directory                          │
│            Token issued for D365 OData access                   │
└─────────────────────────────────────────────────────────────────┘
```

---

## 3. Data Flow — End to End

```
1. User clicks "Generate Dashboard" button in D365 form
        │
        ▼
2. GenerateButton.clicked() calls DashboardControl.loadDashboard()
        │
        ▼
3. SalesIntelligenceControl.loadDashboard() calls
   SalesIntelligenceService::getDashboardHtml()
        │
        ▼
4. X++ makes HTTP POST to http://localhost:8000/ask-chart
        │
        ▼
5. Python server: odata.py acquires Azure AD token
        │
        ▼
6. odata.py fetches SalesOrderLines from D365 OData
   Filter: dataAreaId eq 'usmf'
   Expand: SalesOrderHeader (OrderingCustomerAccountNumber, SalesOrderStatus)
   Select: SalesOrderNumber, SalesOrderLineStatus, ItemNumber, LineDescription,
           OrderedSalesQuantity, SalesPrice, LineAmount, CurrencyCode,
           RequestedReceiptDate, SalesProductCategoryName
        │
        ▼
7. Python-side filtering (OData enum filtering not supported in URL):
   - Skip if SalesOrderLineStatus != 'Invoiced'
   - Skip if SalesOrderHeader.SalesOrderStatus != 'Invoiced'
   - Skip if LineAmount <= 0
        │
        ▼
8. summarise_sales_performance() aggregates:
   - Revenue, orders, products per customer
   - Revenue, quantity, customer count per product
   - Revenue per category
   - Grand total, top customer, top product
        │
        ▼
9. ai_engine.py builds prompt → calls Ollama qwen3:8b → returns narrative
        │
        ▼
10. chart_engine.py builds complete HTML with:
    - KPI cards (total revenue, top customer, top product, avg order value)
    - Chart 1: Top 15 customers horizontal bar (colour-coded by tier)
    - Chart 2: Top 10 products horizontal bar
    - Chart 3: Revenue by category doughnut
    - AI narrative section
    - All styles INLINE (D365 strips <style> blocks)
    - CDN fallback for Chart.js (for localhost testing)
        │
        ▼
11. HTML string returned to X++ via HTTP response
        │
        ▼
12. SalesIntelligenceControl.parmHtmlContent(html) sets HtmlContent observable
        │
        ▼
13. SalesIntelligenceControlScript.js observes HtmlContent change:
    - Injects HTML into #SalesIntelligenceDashboardContainer
    - Extracts all <script> tags, removes them from DOM
    - Checks if Chart global exists
    - If not: loads Chart.js from /resources/scripts/SalesIntelligenceChartJS.js
    - Executes chart scripts after 300ms delay (DOM settle time)
        │
        ▼
14. Chart.js renders all 3 charts on HTML5 canvas elements
    Dashboard is fully visible inside the D365 form
```

---

## 4. Repository Structure

```
D365-AI-Sales_Revenue-Intelligence/
│
├── python/                              # Python FastAPI service layer
│   ├── .env                             # Environment variables (secrets — never commit)
│   ├── server.py                        # FastAPI app — 4 endpoints
│   ├── odata.py                         # D365 OData fetch + data aggregation
│   ├── chart_engine.py                  # HTML/Chart.js dashboard builder
│   ├── ai_engine.py                     # Ollama LLM integration
│   └── config.py                        # Environment variable loader
│
├── SalesRevenueIntelligence/            # D365 Visual Studio AOT project
│   └── (AOT metadata — managed by VS)
│
└── SalesIntelligence_Output.html        # Test output file (generated by SalesIntelligenceTest)
```

---

## 5. D365 AOT Project Structure

```
SalesRevenueIntelligence (USR) [OHMS]
│
├── Base Enums
│   └── IsEnabled                        # Yes/No enum for enabling/disabling the feature
│
├── Classes
│   ├── SalesIntelligenceControl         # Extensible control class — core bridge
│   ├── SalesIntelligenceControlBuild    # Build class — required by D365 control framework
│   ├── SalesIntelligenceService         # HTTP service — calls Python server
│   └── SalesIntelligenceTest            # Runnable test class — outputs HTML to disk
│
├── Display Menu Items
│   └── SalesIntelligenceDashboard       # Menu item — makes form accessible from navigation
│
├── Forms
│   └── SalesIntelligenceDashboard       # The D365 form containing the dashboard
│
├── Menu Extensions
│   └── AccountsReceivable.OHMS          # Adds dashboard to Accounts Receivable menu
│
├── Resources
│   ├── SalesIntelligenceChartJS         # AOT resource containing Chart.js v4.4.0 UMD
│   │   └── SalesIntelligenceChartJS.js
│   ├── SalesIntelligenceControlHTM      # AOT resource: HTML shell template
│   │   └── SalesIntelligenceControl.htm
│   └── SalesIntelligenceControlScript   # AOT resource: control JavaScript logic
│       └── SalesIntelligenceControlScript.js
│
└── Tables
    └── SalesIntelligenceParameters      # Configuration table (server URL, timeout, IsEnabled)
```

---

## 6. Component Deep Dive

### 6.1 SalesIntelligenceControl.htm

**File:** `SalesRevenueIntelligence/Resources/SalesIntelligenceControlHTM/SalesIntelligenceControl.htm`  
**AOT Resource name:** `SalesIntelligenceControlHTM`  
**Served at:** `/resources/html/SalesIntelligenceControl`

```html
<script src="/resources/scripts/SalesIntelligenceControl.js"></script>
<div id="SalesIntelligenceControl"
     data-dyn-bind="sizing: $dyn.layout.sizing($data), visible: $data.Visible">
    <div id="SalesIntelligenceDashboardContainer"></div>
</div>
```

**Purpose and explanation:**

This is the **HTML shell template** for the Extensible Control. It defines the DOM structure that D365 renders when the control is placed on a form. It has two critical roles:

1. **Loads the control's JavaScript** — the `<script src="/resources/scripts/SalesIntelligenceControl.js">` tag tells D365 to load `SalesIntelligenceControlScript.js` from its AOT resource server. The URL pattern `/resources/scripts/{ResourceName}.js` is D365's internal resource serving convention.

2. **Provides the injection target** — the inner `<div id="SalesIntelligenceDashboardContainer">` is the empty container that `SalesIntelligenceControlScript.js` will later fill with the complete dashboard HTML received from Python.

The `data-dyn-bind` attribute on the outer div is D365's **Knockout.js binding syntax**. It wires the control's sizing and visibility to D365's layout engine so the control respects the form's sizing rules.

**How to create this for a new project:**
- In Visual Studio AOT, add a new Resource of type HTML
- Name it `{YourControl}HTM` (the HTM suffix is convention)
- The file must contain the outer control div with `data-dyn-bind`, the script tag pointing to your JS resource, and an inner container div with a unique ID
- The resource name in the `FormControlAttribute` on your X++ class must match: `/resources/html/{ResourceName}`

---

### 6.2 SalesIntelligenceControlScript.js

**File:** `SalesRevenueIntelligence/Resources/SalesIntelligenceControlScript/SalesIntelligenceControlScript.js`  
**AOT Resource name:** `SalesIntelligenceControlScript`  
**Served at:** `/resources/scripts/SalesIntelligenceControl.js`

**Purpose and explanation:**

This is the **JavaScript brain of the Extensible Control**. It implements D365's client-side control framework using the `$dyn` API — D365's internal JavaScript framework built on Knockout.js. When D365 loads the HTM template, this script runs and wires the control to the server-side X++ properties.

**Key sections explained:**

```javascript
$dyn.ui.defaults.SalesIntelligenceControl = {};
$dyn.controls.SalesIntelligenceControl = function (data, element) {
```
Registers the control with D365's control registry. `data` contains the observable properties from X++ (including `HtmlContent`), `element` is the DOM element rendered from the HTM template.

```javascript
$dyn.observe(self.HtmlContent, function (htmlValue) {
```
Sets up a **reactive observer** on the `HtmlContent` property. Every time X++ calls `parmHtmlContent(html)`, this callback fires automatically — this is the bridge between X++ server-side and browser client-side.

```javascript
container.html(htmlValue);
var scripts = [];
container.find('script').each(function () {
    scripts.push($(this).text());
    $(this).remove();
});
```
**Critical technique:** When you inject HTML containing `<script>` tags via jQuery's `.html()`, browsers block their execution for security reasons. This code extracts all script content into an array and removes the `<script>` tags from the DOM before injection.

```javascript
function runCharts() {
    setTimeout(function () {
        for (var i = 0; i < scripts.length; i++) {
            try { new Function(scripts[i])(); } catch (e) {}
        }
    }, 300);
}
```
Re-executes the extracted scripts using `new Function()` — this bypasses the browser's script injection block. The **300ms delay** is intentional: it allows the DOM to fully settle after HTML injection before Chart.js tries to find canvas elements.

```javascript
if (typeof Chart !== 'undefined') {
    runCharts();
} else {
    var chartUrl = $dyn.internal.getResourceUrl('ChartJS');
    var script = document.createElement('script');
    script.src = chartUrl;
    script.onload = runCharts;
    document.head.appendChild(script);
}
```
**Chart.js loading logic:** Checks if Chart.js is already loaded (preventing double-loading). If not, uses `$dyn.internal.getResourceUrl('ChartJS')` — D365's internal API to resolve an AOT resource URL by its resource name — to load `SalesIntelligenceChartJS.js` from the D365 resource server. Only runs charts after the library is confirmed loaded.

**How to create this for a new project:**
- Create a new JavaScript file as an AOT Resource
- Register it with `$dyn.ui.defaults.{ControlName}` and `$dyn.controls.{ControlName}`
- Always observe properties with `$dyn.observe` — never read them directly
- Always extract and re-execute scripts manually — never rely on jQuery `.html()` to run them
- Always check `typeof Chart !== 'undefined'` before loading Chart.js again

---

### 6.3 SalesIntelligenceChartJS.js

**File:** `SalesRevenueIntelligence/Resources/SalesIntelligenceChartJS/SalesIntelligenceChartJS.js`  
**AOT Resource name:** `SalesIntelligenceChartJS`  
**Served at:** `/resources/scripts/SalesIntelligenceChartJS.js`

**Purpose and explanation:**

This file **contains the entire Chart.js v4.4.0 library** in UMD (Universal Module Definition) minified format. It is not written by hand — it is a copy of the official Chart.js distribution file, stored as a D365 AOT Resource so D365 can serve it to the browser from its own resource server without any external network dependency.

**Why this approach is necessary:**

D365 F&O OneBox and on-premise environments often **block outbound internet requests** from the browser. A `<script src="https://cdn.jsdelivr.net/...">` tag would silently fail. By embedding Chart.js in an AOT Resource, D365 serves it internally via `/resources/scripts/SalesIntelligenceChartJS.js` — always available, regardless of network access.

**How to get Chart.js UMD content:**

1. Go to: `https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js`
2. Or download from: `https://github.com/chartjs/Chart.js/releases/tag/v4.4.0`
3. Open the file — it is a single minified JavaScript file starting with `!function(...`
4. Copy the **entire content** (Ctrl+A, Ctrl+C)

**How to populate it in AOT:**

1. In Visual Studio Solution Explorer, click on `SalesIntelligenceChartJS.js`
2. Press **F4** to open the Properties panel
3. Find the **Full Path** property — this is the file on disk
4. Open that path in VS Code or Notepad++
5. Select All (Ctrl+A) → Delete → Paste the Chart.js content → Save
6. Rebuild the project in Visual Studio → Deploy to LocalDB

**Why UMD format specifically:**

D365's control script runs in a browser context without a module bundler (no webpack, no require.js). UMD format is the only Chart.js distribution that works as a plain `<script>` tag and exposes the `Chart` global variable — which is what the control script checks with `typeof Chart !== 'undefined'`.

**For a new project using a different version:**

Simply replace the content of your AOT resource JS file with the new version's `chart.umd.min.js` content. The resource name and URL remain the same — no AOT metadata changes needed.

---

### 6.4 SalesIntelligenceDashboard (Form)

**File:** `SalesRevenueIntelligence/Forms/SalesIntelligenceDashboard.xml`

The D365 form is minimal by design — it contains only two controls:

```xml
<Controls>
  <AxFormButtonControl>
    <n>GenerateButton</n>
    <Text>Generate Dashboard</Text>
    <!-- clicked() calls DashboardControl.loadDashboard() -->
  </AxFormButtonControl>

  <AxFormControl>
    <n>DashboardControl</n>
    <AutoDeclaration>Yes</AutoDeclaration>
    <Height>700</Height>
    <HeightMode>Manual</HeightMode>
    <WidthMode>SizeToAvailable</WidthMode>
    <FormControlExtension>
      <n>SalesIntelligenceControl</n>  <!-- links to the Extensible Control -->
    </FormControlExtension>
  </AxFormControl>
</Controls>
```

- `AutoDeclaration>Yes` makes `DashboardControl` available as a typed variable in the form's X++ code, allowing `DashboardControl.loadDashboard()` to be called directly from the button's `clicked()` method.
- `Height=700` with `HeightMode=Manual` gives the dashboard fixed height. Increase this if the dashboard content is taller than the form area.
- `WidthMode=SizeToAvailable` makes the control fill the available form width.
- `FormControlExtension` with `<n>SalesIntelligenceControl</n>` is what tells D365 this control should use the custom Extensible Control registered under that name.

---

### 6.5 SalesIntelligenceControl (X++ Class)

This is the **server-side half of the Extensible Control**. It bridges X++ properties to the browser-side JavaScript.

```xpp
[FormControlAttribute(
    'SalesIntelligenceControl',
    '/resources/html/SalesIntelligenceControl',
    classStr(SalesIntelligenceControlBuild))]
public class SalesIntelligenceControl extends FormTemplateControl
```

The `FormControlAttribute` registers this class as the server-side implementation of an Extensible Control. Three parameters:
- `'SalesIntelligenceControl'` — the control name, must match `$dyn.controls.SalesIntelligenceControl` in the JS
- `'/resources/html/SalesIntelligenceControl'` — the AOT resource path of the HTM template
- `classStr(SalesIntelligenceControlBuild)` — the associated build class

```xpp
[FormPropertyAttribute(FormPropertyKind::Value, 'HtmlContent', true)]
public str parmHtmlContent(str _value = ...)
```

Declares `HtmlContent` as a **two-way observable property**. When X++ sets this property, D365's framework automatically notifies the browser-side `$dyn.observe(self.HtmlContent, ...)` callback. The `true` parameter marks it as bindable.

```xpp
[FormCommandAttribute('LoadDashboard')]
public void loadDashboard()
{
    str html = SalesIntelligenceService::getDashboardHtml();
    this.parmHtmlContent(html);
}
```

Declares `loadDashboard` as a **form command** callable from the form. Fetches HTML from Python and pushes it to the observable property, triggering the browser-side observer.

---

### 6.6 SalesIntelligenceControlBuild (X++ Class)

```xpp
[FormDesignControlAttribute('SalesIntelligenceControl')]
public class SalesIntelligenceControlBuild extends FormBuildControl
{
}
```

This is a **required companion class** for any Extensible Control. It is used by the D365 form designer at design time to recognize and place the control. The class body is empty — it simply needs to exist and carry the `FormDesignControlAttribute` decorator with the control's name.

---

### 6.7 SalesIntelligenceService (X++ Class)

The HTTP service layer. Makes a synchronous `System.Net.HttpWebRequest` to the Python FastAPI server.

**Key design decisions:**
- Uses `SalesIntelligenceParameters::find()` to read the server URL and timeout from a D365 configuration table — making the server address configurable without redeployment
- Calls `/ask-chart` (POST) with a JSON body — kept for backward compatibility. The `/dashboard` endpoint (GET) exists for direct browser testing
- Returns an HTML error page string on failure (rather than throwing) so the control always has something to display
- Timeout is configurable via `SalesIntelligenceParameters.TimeoutSeconds` — set this to at least 120 seconds on first run as AOS may be idle

---

### 6.8 SalesIntelligenceTest (X++ Runnable Class)

A **developer utility** for testing the full pipeline without opening the D365 form. Run it from Visual Studio (right-click → Run) to:
1. Call `SalesIntelligenceService::getDashboardHtml()`
2. Save the returned HTML to disk at the repo root as `SalesIntelligence_Output.html`
3. Open `SalesIntelligence_Output.html` in a browser to visually verify the dashboard before deploying the form

This is invaluable during development — it bypasses the D365 form/control layer entirely and lets you verify the Python server is returning correct HTML.

---

## 7. Python Service Layer

### 7.1 server.py

FastAPI application exposing four endpoints. Starts Ollama warm-up on startup.

| Endpoint | Method | Purpose |
|---|---|---|
| `/health` | GET | Confirm server is running, returns model and company info |
| `/test-sales-data` | GET | Validate OData data — check totals, top customers, top products |
| `/ask-chart` | POST | Primary endpoint called by X++, returns full dashboard HTML |
| `/dashboard` | GET | GET version of ask-chart, for direct browser access and localhost testing |

**Important notes:**
- `StaticFiles` mount has been removed — Chart.js is now served from D365 AOT resource
- CORS is open (`allow_origins=["*"]`) — appropriate for local VHD development
- Ollama is warmed up on startup with a dummy request to avoid cold-start timeout on first dashboard load

---

### 7.2 odata.py

Handles all D365 OData communication and data aggregation.

**Authentication:** Uses Azure AD client credentials flow (OAuth2). A fresh token is acquired before each fetch call. Token URL: `https://login.windows.net/{tenant_id}/oauth2/token`.

**OData entity used:** `SalesOrderLines`  
This entity was chosen over `SalesOrderHeadersV2` because it provides line-level detail (item, quantity, price, category) needed for product and category analytics, while the header is accessed via `$expand`.

**OData parameters:**
```python
"$filter": f"dataAreaId eq '{COMPANY}'",
"$select": "SalesOrderNumber,SalesOrderLineStatus,ItemNumber,LineDescription,
             OrderedSalesQuantity,SalesPrice,LineAmount,CurrencyCode,
             RequestedReceiptDate,SalesProductCategoryName",
"$expand": "SalesOrderHeader($select=OrderingCustomerAccountNumber,SalesOrderStatus)",
"$top":    10000
```

**Critical filtering decision — why Python-side filtering:**

D365 F&O OData does not support filtering enum fields directly in the URL `$filter` parameter. Attempting `SalesOrderLineStatus eq 'Invoiced'` returns a 400 error:
```
"A binary operator with incompatible types was detected. Found operand types 
'Microsoft.Dynamics.DataEntities.SalesStatus' and 'Edm.String'"
```

The solution is to fetch all records and filter in Python:
```python
if line_status != "Invoiced":      # line-level filter
    continue
if header_status != "Invoiced":    # header-level filter (matches SQL SALESSTATUS = 3)
    continue
if line_amount <= 0:               # exclude zero/negative lines
    continue
```

**Why both header AND line status must be checked:**

D365 can have orders where the header status is still "Open" (being processed) but individual lines have been invoiced. Filtering on line status alone would incorrectly include revenue from open/unconfirmed orders. Filtering on header status alone would include cancelled lines within invoiced orders. Both checks together exactly match SQL: `SALESSTATUS = 3 (header) AND SALESSTATUS = 3 (line)`.

**Aggregation output (`summarise_sales_performance`):**

| Field | Description |
|---|---|
| `customer_stats` | List of customers sorted by revenue desc, with tier, order count, product diversity |
| `product_stats` | List of products sorted by revenue desc, with customer reach |
| `category_stats` | Dict of categories with revenue, quantity, order count |
| `grand_total` | Sum of all invoiced line amounts |
| `total_customers` | Count of unique customer accounts |
| `total_orders` | Count of unique sales order numbers |
| `total_lines` | Raw count of line records after filtering |

---

### 7.3 chart_engine.py

Builds the complete self-contained HTML dashboard string.

**Critical design decision — all CSS is inline:**

D365's Extensible Control framework **strips `<style>` block content** when injecting HTML into the control container. Any CSS defined in a `<style>` tag will be ignored. The solution is to use inline `style=""` attributes on every HTML element. The `S` dictionary at the top of the file stores all inline style strings, making them easy to maintain:

```python
S = {
    "stat_card": "background:white;border-radius:8px;padding:12px 18px;flex:1;
                  min-width:140px;box-shadow:0 1px 4px rgba(0,0,0,0.08);
                  border-left:4px solid #7c3aed;",
    ...
}
```

**Chart.js loading strategy:**

A CDN `<script>` tag is included in the HTML head for localhost testing:
```html
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
```
In D365, the control script's Chart.js loading logic takes precedence (loading from AOT resource). The CDN tag serves as a fallback for localhost development. If D365 blocks external CDN requests, the AOT resource ensures the charts still render.

**Charts generated:**

| Chart | Type | Data | Colors |
|---|---|---|---|
| Top 15 Customers by Revenue | Horizontal bar | Customer revenue, sorted desc | Color-coded by tier (purple/gold/silver/bronze) |
| Top 10 Products by Revenue | Horizontal bar | Product revenue, sorted desc | Blue (#3b82f6) |
| Revenue by Category | Doughnut | Category revenue breakdown | 10-color palette |

**Label safety:**

Product names containing quotes or backslashes (e.g. `Television HDTV X590 52" White`) are escaped via `_safe_label()` before being embedded in JavaScript strings, preventing JSON/JS parse errors.

---

### 7.4 ai_engine.py

Manages all Ollama LLM integration.

**Model:** `qwen3:8b` — a reasoning model that may emit `<think>` tags in its output. These are stripped by `re.sub(r"<think>.*?</think>", "", raw, flags=re.DOTALL)`.

**Prompt engineering:** The prompt is structured as a senior sales analyst persona with specific instructions: state revenue health, name top customers with exact figures, highlight top products, and recommend 2 specific actions. `temperature=0.3` keeps the output factual and consistent.

**Retry logic:** One automatic retry with Ollama re-warm-up if the first call fails — handles cases where Ollama has unloaded the model from memory.

**Warm-up:** Called on server startup with `keep_alive: "10m"` to keep the model loaded in GPU/CPU memory and avoid cold-start delays on the first real request.

---

### 7.5 config.py

Simple environment variable loader using `python-dotenv`. All credentials and URLs are read from `.env` — nothing is hardcoded.

---

## 8. Prerequisites

**Python environment:**
- Python 3.10+
- pip packages: `fastapi`, `uvicorn`, `requests`, `httpx`, `python-dotenv`, `pydantic`

**D365 environment:**
- Microsoft Dynamics 365 Finance & Operations (OneBox VHD or cloud sandbox)
- Visual Studio 2019/2022 with D365 developer tools installed
- Access to deploy AOT customizations (USR layer)

**Azure AD:**
- App registration with client credentials (client ID + secret)
- API permission: `Dynamics CRM — user_impersonation` (or equivalent D365 scope)
- App registered as a D365 user in System Administration → Users

**AI (local):**
- [Ollama](https://ollama.ai) installed and running
- Model pulled: `ollama pull qwen3:8b`

---

## 9. Installation & Setup

**Step 1 — Clone the repository:**
```powershell
cd C:\Users\localadmin\source\repos\FO_Customizations
git clone <repo-url> D365-AI-Sales_Revenue-Intelligence
```

**Step 2 — Install Python dependencies:**
```powershell
cd D365-AI-Sales_Revenue-Intelligence\python
pip install fastapi uvicorn requests httpx python-dotenv pydantic
```

**Step 3 — Configure `.env`** (see Section 10)

**Step 4 — Open D365 AOT project in Visual Studio:**
- Open `SalesRevenueIntelligence.sln` from the `SalesRevenueIntelligence` folder
- Verify all AOT objects are present in Solution Explorer

**Step 5 — Populate SalesIntelligenceChartJS.js** (see Section 11)

**Step 6 — Build and deploy the AOT project:**
```
Visual Studio → Right-click project → Rebuild
Visual Studio → Dynamics 365 → Deploy → Deploy to LocalDB
```

**Step 7 — Start the Python server** (see Section 12)

**Step 8 — Test:**
- Open D365 → navigate to `SalesIntelligenceDashboard` (via Accounts Receivable menu)
- Click **Generate Dashboard**
- Wait 30–90 seconds for data fetch + AI narrative generation

---

## 10. Configuration — .env File

Create `python/.env` with the following fields:

```env
# D365 OData base URL — your D365 environment data endpoint
ODATA_BASE_URL=https://<your-aos-url>/data

# D365 company (legal entity) to query
COMPANY=usmf

# Azure AD app registration credentials
AAD_TENANT_ID=<your-tenant-id>
AAD_CLIENT_ID=<your-app-client-id>
AAD_CLIENT_SECRET=<your-app-client-secret>

# D365 resource URI for OAuth2 scope
AAD_RESOURCE=https://<your-aos-url>/

# Azure AD OAuth2 token endpoint base URL
LOGIN_URL=https://login.windows.net/

# Ollama local server URL (default port 11434)
OLLAMA_URL=http://localhost:11434

# Ollama model to use for AI narrative generation
OLLAMA_MODEL=qwen3:8b

# Python server host and port
HOST=0.0.0.0
PORT=8000
```

**How to find these values:**
- `ODATA_BASE_URL`: Your D365 URL + `/data` (e.g. `https://usnconeboxax1aos.cloud.onebox.dynamics.com/data`)
- `AAD_TENANT_ID`: Azure Portal → Azure Active Directory → Overview → Tenant ID
- `AAD_CLIENT_ID`: Azure Portal → App registrations → your app → Application (client) ID
- `AAD_CLIENT_SECRET`: Azure Portal → App registrations → your app → Certificates & secrets
- `AAD_RESOURCE`: Your D365 URL with trailing slash (must match the app's audience)

> ⚠️ **Never commit `.env` to source control.** Add it to `.gitignore`.

---

## 11. AOT Resource Deployment

### Populating SalesIntelligenceChartJS.js

This step must be completed once before the dashboard will render in D365. The AOT resource file must contain the full Chart.js v4.4.0 UMD library.

**Step 1 — Get the Chart.js content:**

Option A — From CDN (requires internet):
- Open: `https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js`
- Ctrl+A → Ctrl+C to copy entire content

Option B — From npm (offline):
```powershell
npm pack chart.js@4.4.0
# Extract the tarball, find dist/chart.umd.min.js
```

**Step 2 — Find the file on disk:**
- In Visual Studio Solution Explorer, click `SalesIntelligenceChartJS.js`
- Press **F4** to open Properties
- Copy the value of **Full Path**

**Step 3 — Replace file contents:**
- Open the path from Step 2 in VS Code
- Ctrl+A → Delete all existing content
- Ctrl+V → Paste the Chart.js content
- Save (Ctrl+S)

**Step 4 — Rebuild and deploy:**
```
Visual Studio → Right-click SalesRevenueIntelligence → Rebuild
Visual Studio → Dynamics 365 → Deploy → Deploy to LocalDB
```

**Step 5 — Verify:**
- Open browser, navigate to D365
- Open DevTools (F12) → Network tab
- Generate the dashboard
- Confirm a request to `/resources/scripts/SalesIntelligenceChartJS.js` returns status 200 with a large JS payload

---

## 12. Running the Python Server

**Start the server:**
```powershell
cd C:\Users\localadmin\source\repos\FO_Customizations\D365-AI-Sales_Revenue-Intelligence\python
uvicorn server:app --host 0.0.0.0 --port 8000 --reload
```

**Before making OData calls — wake the AOS:**
D365 OneBox AOS goes idle after inactivity. An idle AOS causes OData calls to time out. Before calling any endpoint, open any D365 page (e.g. Accounts Receivable → Inquiries → Open transactions) to wake the AOS.

**Verify server is running:**
```
GET http://localhost:8000/health
```

**Validate data before generating dashboard:**
```
GET http://localhost:8000/test-sales-data
```
Expected: `total_customers: 29`, `grand_total: ~99451085`, `match_revenue: true`

**Test full dashboard generation:**
```
GET http://localhost:8000/dashboard
```
Open in browser — should show the full styled dashboard with all 3 charts and AI narrative.

---

## 13. API Endpoints

### GET /health
Returns server status, model, and company.
```json
{
  "status": "ok",
  "model": "qwen3:8b",
  "company": "usmf",
  "project": "D365 AI Sales & Revenue Intelligence v1.0"
}
```

### GET /test-sales-data
Validates OData data against expected SQL ground truth. Use this to confirm data is correct before generating the full dashboard.
```json
{
  "status": "ok",
  "total_lines": 5736,
  "total_customers": 29,
  "total_orders": 708,
  "grand_total": 99451085.5,
  "top_customer": "DE-001",
  "top_product": "Projector Television",
  "top_5_customers": [...],
  "top_5_products": [...],
  "validation": {
    "match_customers": true,
    "match_revenue": true,
    "match_top_product": true
  }
}
```

### POST /ask-chart
Request body:
```json
{ "question": "Show me the sales revenue dashboard" }
```
Returns: Complete HTML string with embedded Chart.js dashboard. This is the endpoint called by X++.

### GET /dashboard
Same as `/ask-chart` but via GET. Used for direct browser testing and localhost verification.

---

## 14. Data Validation & SQL Ground Truth

The dashboard data has been validated against direct SQL queries on the D365 AXDB database.

**Correct SQL ground truth query:**
```sql
SELECT 
    SUM(l.LINEAMOUNT)             AS TotalRevenue,
    COUNT(DISTINCT h.SALESID)     AS TotalOrders,
    COUNT(DISTINCT h.CUSTACCOUNT) AS TotalCustomers
FROM [AxDB].[dbo].[SALESLINE] l
JOIN [AxDB].[dbo].[SALESTABLE] h 
    ON l.SALESID = h.SALESID AND l.DATAAREAID = h.DATAAREAID
WHERE h.DATAAREAID = 'usmf'
  AND h.SALESSTATUS = 3    -- header fully invoiced
  AND l.SALESSTATUS = 3    -- line not cancelled
```

**Validated results (USMF, March 2026):**

| Metric | Value |
|---|---|
| Total Revenue | $99,451,085.50 |
| Total Orders | 708 |
| Total Customers | 29 |

**Why the OData filter differs from SQL:**

D365 OData does not support filtering enum fields in the URL. The Python code filters in-memory:
- `SalesOrderLineStatus == 'Invoiced'` (equivalent to `l.SALESSTATUS = 3`)
- `SalesOrderStatus == 'Invoiced'` (equivalent to `h.SALESSTATUS = 3`)

**Why not filter all header statuses equally in SQL:**

SQL's `SALESSTATUS = 3` on the header includes one edge case: order `000701` (US-004) has header status Invoiced but one line (`P0001`, $1,369) with status Cancelled (4). The OData line filter correctly excludes this cancelled line. The true ground truth SQL must therefore add `AND l.SALESSTATUS = 3`.

---

## 15. Revenue Tier Classification

Customers are classified into tiers based on total invoiced revenue:

| Tier | Revenue Range | Color |
|---|---|---|
| Platinum | $10M+ | Purple `#7c3aed` |
| Gold | $5M – $10M | Gold `#d97706` |
| Silver | $1M – $5M | Silver `#6b7280` |
| Bronze | Under $1M | Bronze `#92400e` |

The tier color is used as the bar color in the Top 15 Customers chart, giving an immediate visual indication of customer value tier.

---

## 16. Technical Notes & Gotchas

| Issue | Root Cause | Solution |
|---|---|---|
| D365 strips `<style>` blocks | Control framework sanitizes injected HTML | All CSS must be inline `style=""` attributes |
| `<script>` tags don't execute after jQuery `.html()` | Browser security blocks injected scripts | Extract scripts manually, re-execute with `new Function()` |
| Chart.js OData enum filter 400 error | D365 OData enum types can't be string-compared in URL | Filter `SalesOrderLineStatus` and `SalesOrderStatus` in Python after fetch |
| Charts blank despite HTML injecting correctly | Chart.js not loaded yet when scripts execute | 300ms delay in `runCharts()` + `$dyn.internal.getResourceUrl()` for AOT loading |
| D365 blocks CDN script tags | Outbound internet blocked in OneBox/on-prem | Chart.js stored as AOT Resource, served from `/resources/scripts/` |
| AOS timeout on first OData call | D365 AOS is idle, takes time to wake | Open any D365 page before calling OData endpoints; set timeout ≥ 120s |
| Product names with quotes break chart JSON | Chart.js labels embedded in JS string literals | `_safe_label()` escapes `"`, `'`, `\` before embedding |
| `SalesIntelligenceChartJS.js` is empty | AOT resource created but never populated | Must manually paste Chart.js UMD content; rebuild and redeploy |
| Inline script double-loading Chart.js | CDN tag in HTML + AOT resource both load Chart.js | `typeof Chart !== 'undefined'` guard in control script prevents double-init |
| `LINEAMOUNT` vs `SALESQTY * SALESPRICE` difference | None — they are identical in AXDB | Use `LINEAMOUNT` (pre-calculated, more reliable) |

---

## 17. Troubleshooting

**Dashboard shows blank white area:**
- Check browser DevTools Console for JavaScript errors
- Verify `SalesIntelligenceChartJS.js` is populated (not empty)
- Check Network tab: does `/resources/scripts/SalesIntelligenceChartJS.js` return 200?

**"Error connecting to Sales Intelligence server":**
- Verify Python server is running: `http://localhost:8000/health`
- Check `SalesIntelligenceParameters` in D365 — is the URL set to `http://localhost:8000`?
- Check firewall — D365 AOS must be able to reach localhost:8000

**OData fetch returns 401:**
- Azure AD token has expired or client secret is wrong
- Verify the app registration has D365 API permission
- Verify the app is registered as a D365 user (System Administration → Users)

**OData fetch returns 400:**
- Do not add enum filters to `$filter` URL parameter
- All status filtering must be done in Python after fetch

**Ollama timeout:**
- Run `ollama list` to confirm `qwen3:8b` is pulled
- Run `ollama run qwen3:8b` manually to verify it starts
- Increase `TimeoutSeconds` in `SalesIntelligenceParameters`

**`match_revenue: false` in /test-sales-data:**
- Threshold is `>= 99_000_000`
- If revenue is below this, check that OData filters are correctly applied (both header and line status = Invoiced)

---

*D365 AI Sales & Revenue Intelligence — OHMS Model*  
*Developed by Omar Hesham Shehab | March 2026*  
*Part of the D365 AI Series*
