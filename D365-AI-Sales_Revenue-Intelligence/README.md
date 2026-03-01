# 🧠 D365 AI Sales & Revenue Intelligence Dashboard

> 👤 **OHMS Model — Omar Hesham Shehab**  
> 🏢 Part of the D365 AI Series | Microsoft Dynamics 365 Finance & Operations

An AI-powered, fully embedded sales revenue intelligence dashboard built as a **custom Extensible Control** inside Microsoft Dynamics 365 F&O. The dashboard fetches live invoiced sales data from D365 via OData, aggregates it in Python, renders three interactive Chart.js charts, and generates an executive AI narrative using a locally running Ollama LLM — all rendered natively inside a D365 form with zero external browser dependencies.

---

## 📚 Table of Contents

1. [🎯 Project Overview](#1--project-overview)
2. [🏗️ System Architecture](#2-️-system-architecture)
3. [🔄 Data Flow — End to End](#3--data-flow--end-to-end)
4. [📁 Repository Structure](#4--repository-structure)
5. [🧩 D365 AOT Project Structure](#5--d365-aot-project-structure)
6. [🔬 Component Deep Dive](#6--component-deep-dive)
   - [📄 SalesIntelligenceControl.htm](#61--salesintelligencecontrolhtm)
   - [⚙️ SalesIntelligenceControlScript.js](#62-️-salesintelligencecontrolscriptjs)
   - [📊 SalesIntelligenceChartJS.js](#63--salesintelligencechartjsjs)
   - [🖥️ SalesIntelligenceDashboard Form](#64-️-salesintelligencedashboard-form)
   - [🔧 SalesIntelligenceControl X++ Class](#65--salesintelligencecontrol-x-class)
   - [🔩 SalesIntelligenceControlBuild X++ Class](#66--salesintelligencecontrolbuild-x-class)
   - [🌐 SalesIntelligenceService X++ Class](#67--salesintelligenceservice-x-class)
   - [🧪 SalesIntelligenceTest X++ Runnable Class](#68--salesintelligencetest-x-runnable-class)
7. [🐍 Python Service Layer](#7--python-service-layer)
   - [🚀 server.py](#71--serverpy)
   - [📡 odata.py](#72--odatapy)
   - [🎨 chart_engine.py](#73--chart_enginepy)
   - [🤖 ai_engine.py](#74--ai_enginepy)
   - [⚙️ config.py](#75-️-configpy)
8. [📋 Prerequisites](#8--prerequisites)
9. [🛠️ Installation & Setup](#9-️-installation--setup)
10. [🔑 Configuration — .env File](#10--configuration--env-file)
11. [🚢 AOT Resource Deployment](#11--aot-resource-deployment)
12. [▶️ Running the Python Server](#12-️-running-the-python-server)
13. [🔌 API Endpoints](#13--api-endpoints)
14. [✅ Data Validation & SQL Ground Truth](#14--data-validation--sql-ground-truth)
15. [🥇 Revenue Tier Classification](#15--revenue-tier-classification)
16. [⚠️ Technical Notes & Gotchas](#16-️-technical-notes--gotchas)
17. [🆘 Troubleshooting](#17--troubleshooting)

---

## 1. 🎯 Project Overview

This project solves a real problem: **D365 F&O has no native AI-powered sales analytics dashboard**. The standard D365 reporting tools (SSRS, Power BI embedded) require separate licensing, infrastructure, and configuration. This solution delivers a fully self-contained AI dashboard that:

- 📥 Reads **live invoiced sales data** directly from D365 via OData — no data exports, no ETL pipelines
- 🔍 Filters to **fully invoiced orders only** (header status = Invoiced AND line status = Invoiced) for financial accuracy
- 🧮 Aggregates revenue by customer, product, and category in Python
- 📈 Renders **three interactive Chart.js charts** natively inside a D365 form
- 🤖 Generates an **AI executive narrative** using a locally running `qwen3:8b` model via Ollama
- 🔒 Is **entirely embedded** in D365 as a custom Extensible Control — no iframe, no popup, no external browser tab

**📌 Validated data (USMF company):**

| Metric | Value |
|---|---|
| 💰 Total Revenue | **$99,451,085.50** |
| 👥 Total Customers | **29** |
| 📦 Total Orders | **708** |
| 🏆 Top Customer | **DE-001** ($7.66M) |
| 🥇 Top Product | **Projector Television** ($34.9M) |

---

## 2. 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                 🖥️  D365 F&O (AOS / Browser)                    │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │        📋 SalesIntelligenceDashboard (Form)              │   │
│  │                                                          │   │
│  │   [🔘 Generate Dashboard Button]                         │   │
│  │        │                                                 │   │
│  │        ▼ DashboardControl.loadDashboard()                │   │
│  │   ┌──────────────────────────────────────────────┐       │   │
│  │   │  🧩 SalesIntelligenceControl (Extensible)    │       │   │
│  │   │                                              │       │   │
│  │   │  📄 SalesIntelligenceControl.htm             │       │   │
│  │   │   └── #SalesIntelligenceDashboardContainer   │       │   │
│  │   │                                              │       │   │
│  │   │  ⚙️  SalesIntelligenceControlScript.js       │       │   │
│  │   │   └── Observes HtmlContent observable        │       │   │
│  │   │   └── Injects HTML into container div        │       │   │
│  │   │   └── Extracts & re-executes <script> tags   │       │   │
│  │   │   └── Loads Chart.js from AOT resource       │       │   │
│  │   │                                              │       │   │
│  │   │  📊 SalesIntelligenceChartJS.js (AOT)        │       │   │
│  │   │   └── Chart.js v4.4.0 UMD build              │       │   │
│  │   └──────────────────────────────────────────────┘       │   │
│  └──────────────────────────────────────────────────────────┘   │
│                        │                                        │
│           🔗 X++ HTTP call (SalesIntelligenceService)           │
└────────────────────────┼────────────────────────────────────────┘
                         │
                         ▼ POST /ask-chart
┌─────────────────────────────────────────────────────────────────┐
│               🐍 Python FastAPI Server (:8000)                   │
│                                                                 │
│  🚀 server.py ──► 📡 odata.py ──► D365 OData API               │
│                        │                                        │
│                        ▼ (filtered, aggregated records)         │
│              🎨 chart_engine.py ──► HTML + Chart.js config      │
│                        │                                        │
│                        ▼                                        │
│              🤖 ai_engine.py ──► Ollama (qwen3:8b) ──► Text    │
│                        │                                        │
│                        ▼                                        │
│         📤 Complete HTML string returned to X++                │
└─────────────────────────────────────────────────────────────────┘
                         │
                         ▼ OAuth2 client_credentials
┌─────────────────────────────────────────────────────────────────┐
│               🔐 Azure Active Directory                          │
│          Token issued for D365 OData access                     │
└─────────────────────────────────────────────────────────────────┘
```

---

## 3. 🔄 Data Flow — End to End

```
👆 Step  1 — User clicks "Generate Dashboard" button in D365 form
        │
        ▼
🖱️  Step  2 — GenerateButton.clicked() calls DashboardControl.loadDashboard()
        │
        ▼
🔧  Step  3 — SalesIntelligenceControl.loadDashboard() calls
              SalesIntelligenceService::getDashboardHtml()
        │
        ▼
📡  Step  4 — X++ makes HTTP POST to http://localhost:8000/ask-chart
        │
        ▼
🔐  Step  5 — Python server: odata.py acquires Azure AD token
        │
        ▼
📥  Step  6 — odata.py fetches SalesOrderLines from D365 OData
              Filter : dataAreaId eq 'usmf'
              Expand : SalesOrderHeader (OrderingCustomerAccountNumber, SalesOrderStatus)
              Select : SalesOrderNumber, SalesOrderLineStatus, ItemNumber,
                       LineDescription, OrderedSalesQuantity, SalesPrice,
                       LineAmount, CurrencyCode, RequestedReceiptDate,
                       SalesProductCategoryName
        │
        ▼
🔍  Step  7 — Python-side filtering (OData enum filtering not supported in URL):
              ❌ Skip if SalesOrderLineStatus    != 'Invoiced'
              ❌ Skip if SalesOrderHeader.Status != 'Invoiced'
              ❌ Skip if LineAmount              <= 0
        │
        ▼
🧮  Step  8 — summarise_sales_performance() aggregates:
              👥 Revenue, orders, unique products per customer
              📦 Revenue, quantity, customer count per product
              🗂️  Revenue per category
              📊 Grand total, top customer, top product
        │
        ▼
🤖  Step  9 — ai_engine.py builds prompt → Ollama qwen3:8b → narrative text
        │
        ▼
🎨  Step 10 — chart_engine.py builds complete HTML with:
              💳 KPI cards (revenue, top customer, top product, avg order value)
              📊 Chart 1: Top 15 customers horizontal bar (tier colour-coded)
              📦 Chart 2: Top 10 products horizontal bar
              🍩 Chart 3: Revenue by category doughnut
              🤖 AI narrative section
              ✏️  All styles INLINE — D365 strips <style> blocks
              🌐 CDN fallback for Chart.js (localhost testing only)
        │
        ▼
📤  Step 11 — HTML string returned to X++ via HTTP response
        │
        ▼
🔗  Step 12 — SalesIntelligenceControl.parmHtmlContent(html) sets observable
        │
        ▼
⚙️  Step 13 — SalesIntelligenceControlScript.js observes HtmlContent change:
              ➕ Injects HTML into #SalesIntelligenceDashboardContainer
              ✂️  Extracts all <script> tags, removes them from DOM
              🔎 Checks if Chart global already exists
              📥 If not: loads Chart.js from AOT resource via $dyn.internal.getResourceUrl
              ⏱️  Executes chart scripts after 300ms delay (DOM settle time)
        │
        ▼
✅  Step 14 — Chart.js renders all 3 charts on HTML5 canvas elements 🎉
```

---

## 4. 📁 Repository Structure

```
📂 D365-AI-Sales_Revenue-Intelligence/
│
├── 🐍 python/                            # Python FastAPI service layer
│   ├── 🔑 .env                           # Secrets & config (never commit!)
│   ├── 🚀 server.py                      # FastAPI app — 4 endpoints
│   ├── 📡 odata.py                       # D365 OData fetch + data aggregation
│   ├── 🎨 chart_engine.py                # HTML/Chart.js dashboard builder
│   ├── 🤖 ai_engine.py                   # Ollama LLM integration
│   └── ⚙️  config.py                     # Environment variable loader
│
├── 🧩 SalesRevenueIntelligence/          # D365 Visual Studio AOT project
│   └── (AOT metadata — managed by VS)
│
└── 📄 SalesIntelligence_Output.html      # Test output (generated by SalesIntelligenceTest)
```

---

## 5. 🧩 D365 AOT Project Structure

```
🏗️ SalesRevenueIntelligence (USR) [OHMS]
│
├── 📐 Base Enums
│   └── ✅ IsEnabled                      # Yes/No — enable or disable the feature
│
├── 💻 Classes
│   ├── 🔧 SalesIntelligenceControl       # Extensible control — core X++ bridge
│   ├── 🔩 SalesIntelligenceControlBuild  # Build class — required by control framework
│   ├── 🌐 SalesIntelligenceService       # HTTP service — calls Python server
│   └── 🧪 SalesIntelligenceTest          # Runnable test — outputs HTML to disk
│
├── 🧭 Display Menu Items
│   └── 📌 SalesIntelligenceDashboard     # Makes the form accessible from D365 nav
│
├── 📋 Forms
│   └── 🖥️  SalesIntelligenceDashboard    # The D365 form that hosts the dashboard
│
├── 🗂️ Menu Extensions
│   └── 📎 AccountsReceivable.OHMS        # Adds dashboard to Accounts Receivable menu
│
├── 📦 Resources
│   ├── 📊 SalesIntelligenceChartJS
│   │   └── SalesIntelligenceChartJS.js   # Chart.js v4.4.0 UMD — full library
│   ├── 📄 SalesIntelligenceControlHTM
│   │   └── SalesIntelligenceControl.htm  # HTML shell template for the control
│   └── ⚙️  SalesIntelligenceControlScript
│       └── SalesIntelligenceControlScript.js  # Control JavaScript logic
│
└── 🗃️ Tables
    └── ⚙️  SalesIntelligenceParameters   # Config table: server URL, timeout, IsEnabled
```

---

## 6. 🔬 Component Deep Dive

### 6.1 📄 SalesIntelligenceControl.htm

**📍 File:** `SalesRevenueIntelligence/Resources/SalesIntelligenceControlHTM/SalesIntelligenceControl.htm`  
**🏷️ AOT Resource name:** `SalesIntelligenceControlHTM`  
**🌐 Served at:** `/resources/html/SalesIntelligenceControl`

```html
<script src="/resources/scripts/SalesIntelligenceControl.js"></script>
<div id="SalesIntelligenceControl"
     data-dyn-bind="sizing: $dyn.layout.sizing($data), visible: $data.Visible">
    <div id="SalesIntelligenceDashboardContainer"></div>
</div>
```

**🧠 Purpose and explanation:**

This is the **HTML shell template** for the Extensible Control. It defines the DOM structure that D365 renders when the control is placed on a form. It has two critical roles:

- 📥 **Loads the control's JavaScript** — the `<script src="/resources/scripts/SalesIntelligenceControl.js">` tag tells D365 to load `SalesIntelligenceControlScript.js` from its AOT resource server. The URL pattern `/resources/scripts/{ResourceName}.js` is D365's internal resource serving convention.

- 🎯 **Provides the injection target** — the inner `<div id="SalesIntelligenceDashboardContainer">` is the empty container that `SalesIntelligenceControlScript.js` will later fill with the complete dashboard HTML received from Python.

The `data-dyn-bind` attribute on the outer div is D365's **Knockout.js binding syntax**. It wires the control's sizing and visibility to D365's layout engine so the control respects the form's sizing rules.

**🔧 How to create this for a new project:**
- ➕ In Visual Studio AOT, add a new Resource of type HTML
- 🏷️ Name it `{YourControl}HTM` (the HTM suffix is convention)
- ✏️ The file must contain the outer control div with `data-dyn-bind`, the script tag pointing to your JS resource, and an inner container div with a unique ID
- 🔗 The resource name in the `FormControlAttribute` on your X++ class must match: `/resources/html/{ResourceName}`

---

### 6.2 ⚙️ SalesIntelligenceControlScript.js

**📍 File:** `SalesRevenueIntelligence/Resources/SalesIntelligenceControlScript/SalesIntelligenceControlScript.js`  
**🏷️ AOT Resource name:** `SalesIntelligenceControlScript`  
**🌐 Served at:** `/resources/scripts/SalesIntelligenceControl.js`

**🧠 Purpose and explanation:**

This is the **JavaScript brain of the Extensible Control**. It implements D365's client-side control framework using the `$dyn` API — D365's internal JavaScript framework built on Knockout.js. When D365 loads the HTM template, this script runs and wires the control to the server-side X++ properties.

**🔑 Key sections explained:**

```javascript
// 📌 Register the control with D365's control registry
$dyn.ui.defaults.SalesIntelligenceControl = {};
$dyn.controls.SalesIntelligenceControl = function (data, element) {
```
> `data` contains the observable properties from X++ (including `HtmlContent`). `element` is the DOM node rendered from the HTM template.

```javascript
// 👁️ Reactive observer — fires automatically every time X++ sets HtmlContent
$dyn.observe(self.HtmlContent, function (htmlValue) {
```
> Every time X++ calls `parmHtmlContent(html)`, this callback fires — this is the live bridge between X++ server-side and browser client-side.

```javascript
// ✂️ Extract scripts BEFORE injection — browser blocks injected <script> tags
container.html(htmlValue);
var scripts = [];
container.find('script').each(function () {
    scripts.push($(this).text());
    $(this).remove();          // 🗑️ Remove from DOM before injecting
});
```
> ⚠️ **Critical technique:** When you inject HTML containing `<script>` tags via jQuery's `.html()`, browsers block their execution for security. This code extracts all script content first, then removes the tags.

```javascript
// ⏱️ 300ms delay — waits for DOM to settle, then re-executes scripts
function runCharts() {
    setTimeout(function () {
        for (var i = 0; i < scripts.length; i++) {
            try { new Function(scripts[i])(); } catch (e) {}
        }
    }, 300);
}
```
> Re-executes the extracted scripts using `new Function()` — bypasses the browser's script injection block. The **300ms delay** allows the DOM to settle after HTML injection before Chart.js attempts to find canvas elements.

```javascript
// 📊 Chart.js loading — check AOT resource or already loaded
if (typeof Chart !== 'undefined') {
    runCharts();    // ✅ Already loaded — run immediately
} else {
    // 📥 Load Chart.js from AOT resource via D365's internal URL resolver
    var chartUrl = $dyn.internal.getResourceUrl('ChartJS');
    var script = document.createElement('script');
    script.src = chartUrl;
    script.onload = runCharts;
    document.head.appendChild(script);
}
```
> 💡 `$dyn.internal.getResourceUrl('ChartJS')` resolves to `/resources/scripts/SalesIntelligenceChartJS.js` — served directly from D365, no CDN needed.

**🔧 How to create this for a new project:**
- ➕ Create a new JavaScript AOT Resource
- 📌 Register with `$dyn.ui.defaults.{ControlName}` and `$dyn.controls.{ControlName}`
- 👁️ Always observe properties with `$dyn.observe` — never read them directly
- ✂️ Always extract and re-execute scripts manually — never rely on jQuery `.html()` to run them
- 🔎 Always check `typeof Chart !== 'undefined'` before loading Chart.js again

---

### 6.3 📊 SalesIntelligenceChartJS.js

**📍 File:** `SalesRevenueIntelligence/Resources/SalesIntelligenceChartJS/SalesIntelligenceChartJS.js`  
**🏷️ AOT Resource name:** `SalesIntelligenceChartJS`  
**🌐 Served at:** `/resources/scripts/SalesIntelligenceChartJS.js`

**🧠 Purpose and explanation:**

This file **contains the entire Chart.js v4.4.0 library** in UMD (Universal Module Definition) minified format. It is not written by hand — it is a verbatim copy of the official Chart.js distribution file, stored as a D365 AOT Resource so D365 can serve it to the browser internally without any external network dependency.

**❓ Why this approach is necessary:**

> 🚫 D365 F&O OneBox and on-premise environments often **block all outbound internet requests** from the browser. A `<script src="https://cdn.jsdelivr.net/...">` tag would silently fail with no error shown to the user.

By storing Chart.js as an AOT Resource, D365 serves it from its own resource server at `/resources/scripts/SalesIntelligenceChartJS.js` — always available regardless of network access.

**📥 How to get Chart.js UMD content:**

Option A — 🌐 From CDN (requires internet):
1. Open: `https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js`
2. ⌨️ Ctrl+A → Ctrl+C to copy the entire file content

Option B — 📦 From npm (offline):
```powershell
npm pack chart.js@4.4.0
# Extract the tarball → find package/dist/chart.umd.min.js
```

**🛠️ How to populate it in the AOT Resource:**

1. 🖱️ In Visual Studio Solution Explorer, click `SalesIntelligenceChartJS.js`
2. ⌨️ Press **F4** to open the Properties panel
3. 📋 Copy the **Full Path** value — this is the physical file on disk
4. 📂 Open that file in VS Code
5. ⌨️ Ctrl+A → Delete → Ctrl+V to paste the Chart.js content → Save
6. 🔨 Rebuild the AOT project → Deploy to LocalDB

**✅ How to verify it worked:**
- 🌐 Open D365 in browser → F12 DevTools → Network tab
- 🔘 Click Generate Dashboard
- 🔍 Find the request to `/resources/scripts/SalesIntelligenceChartJS.js`
- ✅ It must return HTTP **200** with a large JS payload (not empty, not 404)

**❓ Why UMD format specifically:**

> 💡 D365's control script runs in a plain browser context with **no module bundler** (no webpack, no require.js). UMD format is the only Chart.js distribution that works as a plain `<script>` tag and exposes the `Chart` global variable — which is what the control script checks with `typeof Chart !== 'undefined'`.

**🆕 For a new project using a different Chart.js version:**
Simply replace the file content with the new version's `chart.umd.min.js`. The AOT resource name, URL, and all references remain identical — no metadata changes needed.

---

### 6.4 🖥️ SalesIntelligenceDashboard (Form)

**📍 File:** `SalesRevenueIntelligence/Forms/SalesIntelligenceDashboard.xml`

The D365 form is intentionally minimal — it contains only two controls:

```xml
<Controls>
  <!-- 🔘 Button that triggers dashboard generation -->
  <AxFormButtonControl>
    <n>GenerateButton</n>
    <Text>Generate Dashboard</Text>
    <!-- clicked() → DashboardControl.loadDashboard() -->
  </AxFormButtonControl>

  <!-- 🧩 The custom extensible control container -->
  <AxFormControl>
    <n>DashboardControl</n>
    <AutoDeclaration>Yes</AutoDeclaration>   <!-- ✅ Typed var available in X++ form code -->
    <Height>700</Height>                     <!-- 📏 Fixed height — increase if needed -->
    <HeightMode>Manual</HeightMode>
    <WidthMode>SizeToAvailable</WidthMode>   <!-- ↔️ Fills available form width -->
    <FormControlExtension>
      <n>SalesIntelligenceControl</n>        <!-- 🔗 Links to the Extensible Control -->
    </FormControlExtension>
  </AxFormControl>
</Controls>
```

**📌 Key design notes:**
- 🏷️ `AutoDeclaration=Yes` — allows `DashboardControl.loadDashboard()` to be called directly from the button's `clicked()` event method
- 📏 `Height=700` with `HeightMode=Manual` — fixed height. If the dashboard content overflows, increase this value
- ↔️ `WidthMode=SizeToAvailable` — control fills the full form width automatically
- 🔗 `FormControlExtension` with `SalesIntelligenceControl` — tells D365 this is a custom Extensible Control, not a built-in form control

---

### 6.5 🔧 SalesIntelligenceControl (X++ Class)

This is the **server-side half of the Extensible Control**. It bridges X++ properties to the browser-side JavaScript observer.

```xpp
// 🔗 Three-parameter decorator — registers this as an Extensible Control
[FormControlAttribute(
    'SalesIntelligenceControl',                  // Control name — must match JS $dyn.controls registration
    '/resources/html/SalesIntelligenceControl',  // HTM template AOT resource path
    classStr(SalesIntelligenceControlBuild))]    // Companion build class
public class SalesIntelligenceControl extends FormTemplateControl
```

```xpp
// 📡 Two-way observable property — browser is notified automatically on change
[FormPropertyAttribute(FormPropertyKind::Value, 'HtmlContent', true)]
public str parmHtmlContent(str _value = htmlContentProperty.parmValue())
```
> 💡 When X++ sets this property, D365's framework automatically triggers the browser-side `$dyn.observe(self.HtmlContent, ...)` callback — no manual signalling required.

```xpp
// 🎯 Form command — declared here, called from the form's button clicked() event
[FormCommandAttribute('LoadDashboard')]
public void loadDashboard()
{
    str html = SalesIntelligenceService::getDashboardHtml();  // 🌐 Fetch from Python
    this.parmHtmlContent(html);                               // 📤 Push to browser
}
```

---

### 6.6 🔩 SalesIntelligenceControlBuild (X++ Class)

```xpp
// 🏗️ Required companion — used by D365 form designer to recognise the control
[FormDesignControlAttribute('SalesIntelligenceControl')]
public class SalesIntelligenceControlBuild extends FormBuildControl
{
    // ℹ️ Intentionally empty — must exist, decorator is all that's needed
}
```

> ⚠️ This class is **mandatory** for every Extensible Control. Without it, the form designer cannot place the control on a form at design time. The body is always empty.

---

### 6.7 🌐 SalesIntelligenceService (X++ Class)

The HTTP service layer. Makes a synchronous `System.Net.HttpWebRequest` call to the Python FastAPI server and returns the dashboard HTML to X++.

**🔑 Key design decisions:**
- 📋 Reads server URL and timeout from `SalesIntelligenceParameters` table — configurable without code changes or redeployment
- 📮 Calls `/ask-chart` (POST) with a JSON body — backward compatible with direct API testing
- 🛡️ Returns an HTML error page string on any failure — the control always has something to render
- ⏱️ Timeout is in `SalesIntelligenceParameters.TimeoutSeconds` — **set to ≥ 120 seconds** on first use, as an idle AOS needs time to wake

---

### 6.8 🧪 SalesIntelligenceTest (X++ Runnable Class)

A **developer-only utility** for testing the entire pipeline without opening the D365 form.

**▶️ How to run:** Visual Studio → Right-click the class → **Run**

**🔄 What it does:**
1. 📞 Calls `SalesIntelligenceService::getDashboardHtml()`
2. 💾 Saves the returned HTML to disk at the repo root as `SalesIntelligence_Output.html`
3. 📊 Logs the HTML character length to the infolog

**💡 Why this is invaluable during development:**
> It completely bypasses the D365 form and Extensible Control layer, letting you verify the Python server is alive and returning correct HTML — before spending time debugging the D365 client side.

---

## 7. 🐍 Python Service Layer

### 7.1 🚀 server.py

FastAPI application exposing four endpoints. Warms up Ollama automatically on startup.

| 🔌 Endpoint | Method | 📝 Purpose |
|---|---|---|
| `/health` | `GET` | ❤️ Confirm server is running — returns model, company, project name |
| `/test-sales-data` | `GET` | ✅ Validate OData data — totals, top customers, top products, match flags |
| `/ask-chart` | `POST` | 📊 Primary endpoint called by X++ — returns full dashboard HTML |
| `/dashboard` | `GET` | 🌐 Browser-accessible version of `/ask-chart` — for localhost testing |

**📌 Important notes:**
- 🗑️ `StaticFiles` mount has been removed — Chart.js is now served from D365 AOT resource only
- 🌍 CORS is fully open (`allow_origins=["*"]`) — appropriate for local VHD development
- 🔥 Ollama is warmed up on server startup to prevent cold-start timeout on the first dashboard request

---

### 7.2 📡 odata.py

Handles all D365 OData communication, pagination, filtering, and data aggregation.

**🔐 Authentication:** Azure AD client credentials flow (OAuth2). A fresh token is acquired before each fetch call.

**📦 OData entity:** `SalesOrderLines` — chosen because it provides line-level detail (item, quantity, price, category) needed for product and category analytics, while the order header is accessed via `$expand`.

**⚠️ Critical — Why Python-side filtering is required:**

> 🚫 D365 F&O OData does **not** support filtering enum fields in the URL `$filter` parameter. Attempting this returns HTTP 400:
> ```
> "A binary operator with incompatible types was detected. Found operand types
>  'Microsoft.Dynamics.DataEntities.SalesStatus' and 'Edm.String'"
> ```

✅ Solution — fetch all, filter in Python:
```python
if line_status != "Invoiced":    # 📋 Line-level: skip non-invoiced lines
    continue
if header_status != "Invoiced":  # 📋 Header-level: skip open/delivered orders
    continue
if line_amount <= 0:             # 💰 Skip zero and negative lines
    continue
```

**❓ Why BOTH header AND line status must be checked:**

> 🔍 D365 supports partial invoicing — an order header can remain "Open" while some individual lines have been invoiced. Filtering on line status alone would include revenue from still-open orders. Filtering on header status alone would include cancelled lines within fully invoiced orders. **Both checks together exactly replicate SQL `SALESSTATUS = 3` on both `SALESTABLE` and `SALESLINE`.**

**📊 Aggregation outputs from `summarise_sales_performance`:**

| 📦 Field | 📝 Description |
|---|---|
| `customer_stats` | 👥 Customers sorted by revenue desc — includes tier, order count, product diversity |
| `product_stats` | 📦 Products sorted by revenue desc — includes customer reach count |
| `category_stats` | 🗂️ Dict of categories with revenue, quantity, and unique order counts |
| `grand_total` | 💰 Sum of all filtered invoiced line amounts |
| `total_customers` | 👥 Count of unique customer account numbers |
| `total_orders` | 📦 Count of unique sales order numbers |
| `total_lines` | 📋 Raw record count after all filters applied |

---

### 7.3 🎨 chart_engine.py

Builds the complete, self-contained HTML dashboard string returned to X++.

**⚠️ Critical design decision — all CSS must be INLINE:**

> 🚫 D365's Extensible Control framework **silently strips `<style>` block content** when injecting HTML into the control container. Any CSS inside a `<style>` tag will simply be ignored with no error.

✅ Solution — every element uses inline `style=""` via the `S` dictionary:
```python
S = {
    "stat_card": "background:white;border-radius:8px;padding:12px 18px;"
                 "flex:1;min-width:140px;box-shadow:0 1px 4px rgba(0,0,0,0.08);"
                 "border-left:4px solid #7c3aed;",
    ...  # 25+ style constants
}
```

**📊 Charts generated:**

| # | 📊 Chart | Type | 🎨 Colour scheme |
|---|---|---|---|
| 1 | 💰 Top 15 Customers by Revenue | Horizontal bar | Tier colour-coded (💜 Platinum / 🥇 Gold / 🥈 Silver / 🥉 Bronze) |
| 2 | 📦 Top 10 Products by Revenue | Horizontal bar | Uniform blue `#3b82f6` |
| 3 | 🍩 Revenue by Category | Doughnut | 10-colour rotating palette |

**🌐 Dual-environment Chart.js loading:**
```html
<!-- Included in HTML head — works on localhost via CDN -->
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
```
- 🏠 **Localhost:** CDN loads Chart.js ✅
- 🏢 **D365:** AOT resource loads Chart.js via `$dyn.internal.getResourceUrl` ✅ (CDN tag is harmless even if blocked)

**🔒 Label safety:** Product and customer names containing `"`, `'`, or `\` (e.g. `Television HDTV X590 52" White`) are escaped via `_safe_label()` before embedding in JavaScript string literals.

---

### 7.4 🤖 ai_engine.py

Manages all Ollama LLM communication.

**🧠 Model:** `qwen3:8b` — a reasoning model that may emit `<think>` tags, which are stripped via regex before the narrative is returned. `temperature=0.3` keeps output factual and consistent.

**🔄 Retry logic:** One automatic retry with Ollama re-warm-up if the first call fails — handles cases where Ollama has unloaded the model from memory between requests.

**🔥 Warm-up:** Called on server startup with `keep_alive: "10m"` to keep the model resident in GPU/CPU memory and prevent cold-start timeouts on the first real dashboard request.

**✂️ Think-tag stripping:**
```python
clean = re.sub(r"<think>.*?</think>", "", raw, flags=re.DOTALL).strip()
```
> `qwen3:8b` is a reasoning model that shows its internal chain-of-thought inside `<think>` tags. These are stripped before the narrative is passed to `chart_engine.py`.

---

### 7.5 ⚙️ config.py

Simple environment variable loader using `python-dotenv`. All credentials and server URLs are read from `.env` at startup — nothing is hardcoded in any Python file.

```python
ODATA_BASE_URL = os.getenv("ODATA_BASE_URL")   # 🌐 D365 OData base URL
COMPANY        = os.getenv("COMPANY")            # 🏢 Legal entity (e.g. usmf)
AAD_TENANT_ID  = os.getenv("AAD_TENANT_ID")     # 🔑 Azure AD tenant
AAD_CLIENT_ID  = os.getenv("AAD_CLIENT_ID")     # 🔑 App registration client ID
AAD_CLIENT_SECRET = os.getenv("AAD_CLIENT_SECRET") # 🔒 Client secret
AAD_RESOURCE   = os.getenv("AAD_RESOURCE")      # 🎯 OAuth2 audience/resource
LOGIN_URL      = os.getenv("LOGIN_URL")          # 🔐 Azure AD token endpoint base
OLLAMA_URL     = os.getenv("OLLAMA_URL")         # 🤖 Ollama server URL
OLLAMA_MODEL   = os.getenv("OLLAMA_MODEL")       # 🧠 Model name (e.g. qwen3:8b)
HOST           = os.getenv("HOST", "0.0.0.0")   # 🌍 FastAPI bind host
PORT           = int(os.getenv("PORT", 8000))    # 🔌 FastAPI bind port
```

---

## 8. 📋 Prerequisites

**🐍 Python environment:**
- ✅ Python 3.10+
- ✅ pip packages: `fastapi`, `uvicorn`, `requests`, `httpx`, `python-dotenv`, `pydantic`

**🏢 D365 environment:**
- ✅ Microsoft Dynamics 365 Finance & Operations (OneBox VHD or cloud sandbox)
- ✅ Visual Studio 2019/2022 with D365 developer tools installed
- ✅ Access to deploy AOT customizations (USR layer)

**🔐 Azure Active Directory:**
- ✅ App registration with client credentials (client ID + secret)
- ✅ API permission: `Dynamics CRM — user_impersonation` (or equivalent D365 scope)
- ✅ App registered as a D365 user: **System Administration → Users**

**🤖 AI (local):**
- ✅ [Ollama](https://ollama.ai) installed and running locally
- ✅ Model pulled: `ollama pull qwen3:8b`

---

## 9. 🛠️ Installation & Setup

**📥 Step 1 — Clone the repository:**
```powershell
cd C:\Users\localadmin\source\repos\FO_Customizations
git clone <repo-url> D365-AI-Sales_Revenue-Intelligence
```

**🐍 Step 2 — Install Python dependencies:**
```powershell
cd D365-AI-Sales_Revenue-Intelligence\python
pip install fastapi uvicorn requests httpx python-dotenv pydantic
```

**🔑 Step 3 — Configure `.env`**
See [Section 10](#10--configuration--env-file) for all fields and where to find the values.

**🏗️ Step 4 — Open D365 AOT project in Visual Studio:**
- Open `SalesRevenueIntelligence.sln` from the `SalesRevenueIntelligence` folder
- Verify all AOT objects are visible in Solution Explorer

**📊 Step 5 — Populate SalesIntelligenceChartJS.js**
See [Section 11](#11--aot-resource-deployment) for the full step-by-step process.

**🔨 Step 6 — Build and deploy the AOT project:**
```
Visual Studio → Right-click project → Rebuild
Visual Studio → Dynamics 365 → Deploy → Deploy to LocalDB
```

**▶️ Step 7 — Start the Python server**
See [Section 12](#12-️-running-the-python-server).

**🧪 Step 8 — Test with SalesIntelligenceTest (optional but recommended):**
- Visual Studio → Right-click `SalesIntelligenceTest` → Run
- Open `SalesIntelligence_Output.html` from the repo root in a browser
- Verify charts and AI narrative render correctly before testing in D365

**🖥️ Step 9 — Open the D365 Dashboard:**
- D365 → Accounts Receivable → (OHMS menu extension) → Sales Intelligence Dashboard
- Click **Generate Dashboard**
- ⏳ Wait 30–90 seconds for data fetch + AI narrative generation on first load

---

## 10. 🔑 Configuration — .env File

Create `python/.env` with the following fields:

```env
# 🌐 D365 OData base URL — your D365 environment data endpoint
ODATA_BASE_URL=https://<your-aos-url>/data

# 🏢 D365 company (legal entity) to query
COMPANY=usmf

# 🔑 Azure AD app registration credentials
AAD_TENANT_ID=<your-tenant-id>
AAD_CLIENT_ID=<your-app-client-id>
AAD_CLIENT_SECRET=<your-app-client-secret>

# 🎯 D365 resource URI — must match the app's configured audience
AAD_RESOURCE=https://<your-aos-url>/

# 🔐 Azure AD OAuth2 token endpoint base URL
LOGIN_URL=https://login.windows.net/

# 🤖 Ollama local server URL (default port 11434)
OLLAMA_URL=http://localhost:11434

# 🧠 Ollama model for AI narrative generation
OLLAMA_MODEL=qwen3:8b

# 🌍 Python server bind settings
HOST=0.0.0.0
PORT=8000
```

**📍 Where to find each value:**

| 🔑 Field | 📍 Where to find it |
|---|---|
| `ODATA_BASE_URL` | Your D365 URL + `/data` |
| `AAD_TENANT_ID` | Azure Portal → Azure Active Directory → Overview → Tenant ID |
| `AAD_CLIENT_ID` | Azure Portal → App registrations → your app → Application (client) ID |
| `AAD_CLIENT_SECRET` | Azure Portal → App registrations → your app → Certificates & secrets |
| `AAD_RESOURCE` | Your D365 base URL with trailing slash |
| `LOGIN_URL` | Always `https://login.windows.net/` for Azure AD v1 endpoint |

> ⚠️ **Never commit `.env` to source control.** Add `python/.env` to your `.gitignore` immediately.

---

## 11. 🚢 AOT Resource Deployment

### 📊 Populating SalesIntelligenceChartJS.js

This step is **mandatory** and must be completed once before the dashboard will render charts in D365. The AOT resource file must contain the full Chart.js v4.4.0 UMD minified library.

**📥 Step 1 — Get the Chart.js UMD content:**

> 🌐 Option A — From CDN (requires internet):
> Open `https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js` → Ctrl+A → Ctrl+C

> 📦 Option B — From npm (offline-friendly):
> ```powershell
> npm pack chart.js@4.4.0
> # Extract tarball → find dist/chart.umd.min.js inside
> ```

**🗂️ Step 2 — Find the file on disk:**
- In Visual Studio Solution Explorer, click `SalesIntelligenceChartJS.js`
- Press **F4** to open the Properties panel
- Copy the **Full Path** value

**✏️ Step 3 — Replace file contents:**
- Open the path from Step 2 in VS Code or Notepad++
- `Ctrl+A` → Delete all existing content
- `Ctrl+V` → Paste the Chart.js UMD content
- `Ctrl+S` → Save

**🔨 Step 4 — Rebuild and deploy:**
```
Visual Studio → Right-click SalesRevenueIntelligence → Rebuild
Visual Studio → Dynamics 365 → Deploy → Deploy to LocalDB
```

**✅ Step 5 — Verify deployment:**
- Open D365 in browser → F12 DevTools → Network tab
- Generate the dashboard
- Confirm a request to `/resources/scripts/SalesIntelligenceChartJS.js` returns **HTTP 200** with a large JavaScript payload (~200KB+)

> 💡 **Why UMD format specifically?** D365's control runtime has no module bundler (no webpack, no require.js). UMD is the only Chart.js distribution that works as a plain `<script>` tag and exposes the `Chart` global — which `SalesIntelligenceControlScript.js` checks with `typeof Chart !== 'undefined'`.

---

## 12. ▶️ Running the Python Server

**🚀 Start the server:**
```powershell
cd C:\Users\localadmin\source\repos\FO_Customizations\D365-AI-Sales_Revenue-Intelligence\python
uvicorn server:app --host 0.0.0.0 --port 8000 --reload
```

**😴 Before making OData calls — wake the AOS:**
> D365 OneBox AOS goes idle after inactivity. An idle AOS causes OData calls to silently time out. Before calling any endpoint, open **any D365 page** (e.g. Accounts Receivable → Inquiries → Open transactions) to wake the AOS first.

**❤️ Verify server is running:**
```
GET http://localhost:8000/health
```

**✅ Validate data before generating dashboard:**
```
GET http://localhost:8000/test-sales-data
```
> Expected: `total_customers: 29`, `grand_total: ~99451085`, `match_revenue: true`

**🌐 Test full dashboard in browser:**
```
GET http://localhost:8000/dashboard
```
> Should render the complete styled dashboard with all 3 charts and the AI narrative.

---

## 13. 🔌 API Endpoints

### ❤️ GET /health
```json
{
  "status":  "ok",
  "model":   "qwen3:8b",
  "company": "usmf",
  "project": "D365 AI Sales & Revenue Intelligence v1.0"
}
```

### ✅ GET /test-sales-data
```json
{
  "status":          "ok",
  "total_lines":     5736,
  "total_customers": 29,
  "total_orders":    708,
  "grand_total":     99451085.5,
  "top_customer":    "DE-001",
  "top_product":     "Projector Television",
  "top_5_customers": [...],
  "top_5_products":  [...],
  "validation": {
    "match_customers":   true,
    "match_revenue":     true,
    "match_top_product": true
  }
}
```

### 📊 POST /ask-chart
**Request body:**
```json
{ "question": "Show me the sales revenue dashboard" }
```
**Returns:** Complete self-contained HTML string — KPI cards, 3 Chart.js charts, AI narrative, all inline-styled.

### 🌐 GET /dashboard
Same output as `/ask-chart` but accessible via GET. Use this for browser testing and localhost verification without needing a REST client.

---

## 14. ✅ Data Validation & SQL Ground Truth

The dashboard data has been validated against direct SQL queries on the D365 AXDB database.

**🎯 Correct SQL ground truth query:**
```sql
SELECT
    SUM(l.LINEAMOUNT)             AS TotalRevenue,
    COUNT(DISTINCT h.SALESID)     AS TotalOrders,
    COUNT(DISTINCT h.CUSTACCOUNT) AS TotalCustomers
FROM [AxDB].[dbo].[SALESLINE]  l
JOIN [AxDB].[dbo].[SALESTABLE] h
    ON l.SALESID = h.SALESID AND l.DATAAREAID = h.DATAAREAID
WHERE h.DATAAREAID = 'usmf'
  AND h.SALESSTATUS = 3   -- ✅ header fully invoiced
  AND l.SALESSTATUS = 3   -- ✅ line not cancelled
```

**📊 Validated results — USMF, March 2026:**

| 📊 Metric | 🔢 SQL | 🐍 OData (Python) | ✅ Match? |
|---|---|---|---|
| 💰 Total Revenue | $99,451,085.50 | $99,451,085.50 | ✅ Exact |
| 📦 Total Orders | 708 | 708 | ✅ Exact |
| 👥 Customers | 29 | 29 | ✅ Exact |
| 🏆 Top Customer | DE-001 | DE-001 | ✅ Exact |
| 🥇 Top Product | Projector Television | Projector Television | ✅ Exact |

**🔍 The $1,369 edge case discovered during validation:**

> Order `000701` (customer US-004) has header status **Invoiced** but contains one line (`P0001`, $1,369) with status **Cancelled (4)**. The original SQL filtering on header status only included this line, inflating the SQL total by $1,369. Adding `AND l.SALESSTATUS = 3` to the SQL query corrects it to exactly match the OData result — confirming that **OData's line-level filter is actually more accurate than a simple header-only SQL filter**.

---

## 15. 🥇 Revenue Tier Classification

Customers are automatically classified into tiers based on their total invoiced revenue. The tier drives the bar colour in the Top 15 Customers chart.

| 🏆 Tier | 💰 Revenue Range | 🎨 Chart Colour | 🖼️ Hex |
|---|---|---|---|
| 💜 Platinum | $10M+ | Purple | `#7c3aed` |
| 🥇 Gold | $5M – $10M | Gold | `#d97706` |
| 🥈 Silver | $1M – $5M | Grey | `#6b7280` |
| 🥉 Bronze | Under $1M | Brown | `#92400e` |

> 📌 In the current USMF dataset, all 29 customers fall into the **Gold** tier ($5M–$10M), meaning all bars in Chart 1 are gold-coloured. As new customers are added or revenue shifts, bars will automatically recolour.

---

## 16. ⚠️ Technical Notes & Gotchas

| ⚠️ Issue | 🔍 Root Cause | ✅ Solution |
|---|---|---|
| 🚫 D365 strips `<style>` blocks | Control framework sanitizes injected HTML | All CSS must be inline `style=""` attributes — use the `S{}` dict in `chart_engine.py` |
| 🚫 `<script>` tags don't execute after jQuery `.html()` | Browser security policy blocks injected scripts | Extract scripts manually into array, re-execute with `new Function()` |
| 🚫 OData enum filter returns HTTP 400 | D365 OData enum types can't be string-compared in URL | Filter `SalesOrderLineStatus` and `SalesOrderStatus` in Python after fetch |
| 🚫 Charts blank despite correct HTML | Chart.js not yet loaded when scripts execute | 300ms delay in `runCharts()` + load Chart.js via `$dyn.internal.getResourceUrl()` |
| 🚫 D365 blocks CDN `<script>` tags | Outbound internet blocked in OneBox/on-prem | Chart.js stored as AOT Resource — served from `/resources/scripts/` internally |
| 😴 AOS timeout on first OData call | D365 AOS idle — cold start takes 30–60 seconds | Open any D365 page before calling OData; set `TimeoutSeconds` ≥ 120 |
| 🚫 Product names with quotes break charts | Label content embedded inside JS string literals | `_safe_label()` escapes `"`, `'`, `\` before embedding |
| 📭 `SalesIntelligenceChartJS.js` is empty | AOT resource created but content never pasted | Paste Chart.js UMD content manually; rebuild and redeploy |
| 🔄 Chart.js double-loaded | CDN `<script>` in HTML + AOT resource both trigger | `typeof Chart !== 'undefined'` guard in control script prevents double-init |
| 💰 $1,369 SQL vs OData gap | SQL header-only filter included a cancelled line | Add `AND l.SALESSTATUS = 3` to SQL; OData line filter was already correct |

---

## 17. 🆘 Troubleshooting

**🚫 Dashboard shows blank white area in D365:**
- 🔍 Open browser DevTools (F12) → Console tab — look for JavaScript errors
- 📭 Verify `SalesIntelligenceChartJS.js` is populated (not an empty file)
- 🌐 Network tab: does `/resources/scripts/SalesIntelligenceChartJS.js` return HTTP 200 with large payload?
- 🔨 If the file was just populated, did you **Rebuild + Deploy** the AOT project?

**🚫 "Error connecting to Sales Intelligence server" shown in D365:**
- ❤️ Verify Python server is running: `GET http://localhost:8000/health`
- 📋 Check `SalesIntelligenceParameters` table in D365 — is URL set to `http://localhost:8000`?
- 🔌 Check Windows Firewall — D365 AOS (running as a service) must be able to reach `localhost:8000`

**🚫 OData returns HTTP 401 Unauthorized:**
- 🔑 Azure AD token has expired or client secret is wrong/rotated
- ✅ Verify app registration has D365 API permission (`user_impersonation`)
- 👤 Verify the Azure AD app is registered as a D365 user: **System Administration → Users → New**

**🚫 OData returns HTTP 400 Bad Request:**
- ⚠️ You added an enum filter to the `$filter` URL parameter — this is not supported
- ✅ All `SalesOrderLineStatus` / `SalesOrderStatus` filtering must happen in Python after fetch

**🚫 Ollama times out or returns empty narrative:**
- 🧠 Run `ollama list` — confirm `qwen3:8b` is downloaded
- 🔥 Run `ollama run qwen3:8b` manually to verify the model starts
- ⏱️ Increase `TimeoutSeconds` in `SalesIntelligenceParameters` — first run with a cold model can take 60+ seconds

**🚫 `match_revenue: false` in /test-sales-data:**
- 🔍 Threshold is `grand_total >= 99_000_000`
- ✅ Confirm both header AND line Invoiced filters are applied in `odata.py`
- 🔍 Log `len(all_recs)` before filtering — if it's 0, AOS is still waking up

**🚫 Charts render on localhost but not in D365:**
- 🎨 Verify all CSS is inline (no `<style>` blocks) — D365 strips them silently
- 🧩 Verify `SalesIntelligenceControlScript.js` is extracting and re-executing scripts via `new Function()`
- ⏱️ Increase the `setTimeout` delay from 300ms to 500ms if canvas elements aren't ready in time

---

*📊 D365 AI Sales & Revenue Intelligence — OHMS Model*  
*👤 Developed by Omar Hesham Shehab | March 2026*  
*🏢 Part of the D365 AI Series*
