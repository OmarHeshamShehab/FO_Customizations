# 🏗️ D365 Finance and Operations Customizations (FO_Customization)

A curated collection of real-world customizations, tutorials, and best practices for Microsoft Dynamics 365 Finance and Operations (D365FO), developed and maintained by **Omar Hesham Mohamed Shehab** under the **OHMS** model.

---

## 📚 Table of Contents

- [🎯 Project Overview](#project-overview)
- [📁 Repository Structure](#repository-structure)
- [✨ Key Features](#key-features)
- [🚀 Getting Started](#getting-started)
- [🧩 Customization Modules](#customization-modules)
  - [🎙️ VoxD365 Voice Assistant](#voxd365-voice-assistant)
  - [🤖 D365 AI Sales Assistant](#d365-ai-sales-assistant)
  - [📊 D365 AI Sales & Revenue Intelligence](#d365-ai-sales--revenue-intelligence)
  - [🚗 ConVehicleManagement](#convehiclemanagement)
  - [📋 Reports (SSRS Custom Report)](#reports-ssrs-custom-report)
  - [📑 CustomerAccountStamentReport (Extended SSRS Report)](#customeraccountstamentreport-extended-ssrs-report)
  - [🏦 CustAgingWithBank (Customer Aging with Bank)](#custagingwithbank-customer-aging-with-bank)
  - [🏢 Halwani](#halwani)
  - [🗂️ Metadata](#metadata)
  - [🛒 Commerce_CustomerListExtension](#commerce_customerlistextension)
  - [🔗 Chain_of_Command](#chain_of_command)
  - [📤 SalesOrderExcelUpload](#salesorderexcelupload-sales-order-upload-from-excel)
  - [✅ SalesOrderWorkflow (Custom Approval Workflow)](#salesorderworkflow-custom-approval-workflow)
  - [🔌 OHMS Service Integration](#ohms-service-integration)
  - [🎁 LoyaltyMemberIntegration (Custom OData Entity + Action)](#loyaltymemberintegration-custom-odata-entity--action)
  - [🇷🇴 ROSaftLocalization (RO SAF-T / D406 — ER Integration)](#rosaftlocalization-ro-saf-t--d406--er-integration)
- [📐 Development Guidelines](#development-guidelines)
- [🧪 Testing & Verification](#testing--verification)
- [🤝 Contributing](#contributing)

---

<a id="project-overview"></a>
## 🎯 Project Overview

This repository serves as a comprehensive resource for D365FO customizations, including:

- 🏭 Client-specific solutions for real business requirements
- 📖 Tutorials and cookbooks for learning and reference
- 🛡️ Best practices for upgrade-safe, maintainable extensions
- 🔁 End-to-end examples covering data, business logic, and UI

All solutions follow Microsoft extensibility guidelines to ensure upgrade safety.

---

<a id="repository-structure"></a>
## 📁 Repository Structure

### 🧩 Customization Modules

- 🎙️ **D3365_AI_Voice_Assitant (VoxD365)** — Voice-enabled warehouse assistant with tap-to-talk interface embedded as a D365 Extensible Control
- 🤖 **D365_AI_Sales-Assistant** — AI-powered natural language sales assistant integrated natively into D365 F&O
- 📊 **D365-AI-Sales_Revenue-Intelligence** — AI-powered sales revenue dashboard with Chart.js visualizations embedded as a D365 Extensible Control
- 🚗 **ConVehicleManagement** — Vehicle tracking and maintenance scheduling
- 📋 **Reports** — Custom SSRS reporting solution
- 📑 **CustomerAccountStamentReport** — Extension of the standard Customer Account Statement SSRS report (adds customer group name column)
- 🏦 **CustAgingWithBank** — Customer Aging with Bank: interactive ECharts visual form plus SSRS report combining aging buckets, credit exposure, DSO, and live bank balances (SAR)
- 🏢 **Halwani** — Client-specific customizations
- 🗂️ **Metadata** — Data model and UI extensions
- 🛒 **Commerce_CustomerListExtension** — Customer entity extension
- 🔗 **Chain_of_Command** — CoC implementation examples
- 📤 **SalesOrderExcelUpload** — Excel-driven sales order automation
- ✅ **SalesOrderWorkflow** — Custom header-level approval workflow on the Sales order (`SalesTable`), surfacing a Submit button with full approval lifecycle, no over-layering
- 🔌 **OHMS Service Integration** — Custom integration service module
- 🎁 **LoyaltyMemberIntegration** — Custom public OData entity with a bound action (`addPoints`) and an unmapped computed field; full create/read/update/invoke flow tested via Postman
- 🇷🇴 **ROSaftLocalization** — Romanian SAF-T (D406) test package: custom ER format derived from Microsoft's SAF-T data model, wrapped in an X++ parameters/menu/security/SysOperation stack that invokes Electronic Reporting from code

---

<a id="key-features"></a>
## ✨ Key Features

- 🛡️ Upgrade-safe customizations using Chain of Command
- 🏭 Real-world client implementations
- 🎙️ Voice-enabled warehouse assistant with tap-to-talk interface
- 🤖 AI-powered natural language querying of live ERP data
- 📊 AI-powered embedded revenue intelligence dashboards with Chart.js
- 📋 Reporting, services, and automation examples
- 🇷🇴 Electronic Reporting (ER) localization pattern — derived formats invoked from X++
- 🏗️ Clean architecture and OHMS naming standards

---

<a id="getting-started"></a>
## 🚀 Getting Started

1. 🔨 Build the solution in Visual Studio
2. 🗄️ Synchronize database changes
3. 🚢 Deploy reports/services where applicable
4. 🧪 Test using Contoso demo data (USMF)

---

<a id="customization-modules"></a>
## 🧩 Customization Modules

---

<a id="voxd365-voice-assistant"></a>
### 🎙️ VoxD365 Voice Assistant

> 📁 `D3365_AI_Voice_Assitant/` — [📖 Full Documentation](D3365_AI_Voice_Assitant/Python/README.md)

A hybrid **tap-to-talk voice assistant** for D365 F&O warehouse workers. Workers can ask inventory questions using voice commands and receive both spoken and text responses with real-time warehouse data — all running locally with zero cloud AI dependency.

#### 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                  D365 F&O — VoxD365 Extensible Control                  │
│  ┌───────────────────────────────────────────────────────────────────┐  │
│  │  🎙️ Mic Button  │  ⌨️ Text Input  │  💬 Chat Window  │  🔊 Audio  │  │
│  └───────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼ HTTP POST (audio/text)
┌─────────────────────────────────────────────────────────────────────────┐
│                     Python FastAPI Server (Port 8000)                   │
│                                                                         │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐                 │
│  │    STT      │    │    LLM      │    │    TTS      │                 │
│  │  (Whisper)  │───▶│  (Ollama)   │───▶│  (Piper)    │                 │
│  │             │    │ qwen2.5:7b  │    │             │                 │
│  └─────────────┘    └──────┬──────┘    └─────────────┘                 │
│                            │ Tool Calls                                 │
│                            ▼                                            │
│                     ┌─────────────┐                                     │
│                     │   D365      │                                     │
│                     │   OData     │                                     │
│                     └─────────────┘                                     │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼ OData REST API
┌─────────────────────────────────────────────────────────────────────────┐
│  D365 F&O: WarehousesOnHandV2 │ ReleasedProductsV2 │ Warehouses        │
└─────────────────────────────────────────────────────────────────────────┘
```

#### 🌟 Key Highlights

- 🎙️ **Tap-to-Talk Interface** — Press and hold to record, release to send
- 🧩 **D365 Extensible Control** — Fully embedded in F&O, no external browser
- 🧠 **Local LLM** — Ollama `qwen2.5:7b` with native tool calling
- 🗣️ **Speech-to-Text** — faster-whisper (2-4x faster than OpenAI Whisper)
- 🔊 **Text-to-Speech** — Piper TTS for natural-sounding responses
- 📦 **Real-time Inventory** — Live D365 data via OData API
- 🔐 **Fully Local** — No cloud AI, no data leaves the environment
- ⚡ **Optimized Performance** — 60-second cache, connection pooling

#### 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| 🖥️ D365 UI | X++ Extensible Control (`FormTemplateControl`) |
| 🎨 Frontend | HTML5 + CSS3 + JavaScript (VoxD365VoiceUI.htm) |
| 🐍 Backend | Python 3.11+ / FastAPI / uvicorn |
| 🗣️ STT | faster-whisper (base model) |
| 🧠 LLM | Ollama `qwen2.5:7b` (local, ~4.4GB) |
| 🔊 TTS | Piper TTS (en_US-lessac-medium) |
| 🔐 Auth | Azure AD OAuth2 client credentials |
| 📡 Data | D365 OData API (`WarehousesOnHandV2`, `ReleasedProductsV2`, `Warehouses`) |

#### 🎯 Supported Voice Commands

| 📋 Command Type | 🗣️ Example Phrase | 🔧 Tool Called |
|----------------|-------------------|----------------|
| 📍 Item Location | "Where is item P0002?" | `get_item_location` |
| 📦 Quantity Check | "How much A0001 do we have?" | `get_on_hand` |
| 🏭 Warehouse Contents | "What items are in warehouse 24?" | `get_warehouse_items` |
| 📝 Item Details | "Tell me about item M0006" | `get_item_details` |
| 🗂️ Warehouse List | "What warehouses do we have?" | `list_warehouses` |

#### ✅ Validated Data — USMF

| 📦 Item | 🏭 Warehouse | 📍 Site | 📊 Quantity |
|---------|-------------|---------|-------------|
| P0002 | 11 | 1 | 212 |
| P0002 | 32 | 3 | 7,593 |
| A0001 | 24 | 2 | 245 |
| A0001 | 63 | 6 | 1,965 |
| M0006 | 11 | 1 | 1,191 |

#### ⚡ Performance Metrics

| ⚙️ Component | ⏱️ Time |
|-------------|---------|
| 🗣️ STT (Whisper) | 1-2 seconds |
| 🧠 LLM Call 1 (tool selection) | 4-8 seconds |
| 📡 D365 OData query | 0.5-2 seconds |
| 🧠 LLM Call 2 (summarize) | 4-8 seconds |
| 🔊 TTS (Piper) | 0.5 seconds |
| **📊 Total** | **10-20 seconds** |

#### 🧩 D365 AOT Components

| 📦 Component | 🗂️ Type | 📝 Purpose |
|---|---|---|
| `VoxD365Control` | X++ Class | Extensible Control — loads UI from FastAPI |
| `VoxD365ControlBuild` | X++ Class | Required design-time companion class |
| `VoxD365Form` | Form | D365 form hosting the voice control |
| `VoxD365ControlHtm` | AOT Resource | HTML template resource |
| `VoxD365ControlScript` | AOT Resource | JavaScript resource |
| `WHS.OHMS` | Menu Extension | Menu item for warehouse module |

#### 🔌 API Endpoints

| 🔌 Endpoint | Method | 📝 Purpose |
|---|---|---|
| `/health` | `GET` | ❤️ Server health check |
| `/ui` | `GET` | 🎨 Serve voice assistant UI HTML |
| `/voice` | `POST` | 🎙️ Process voice query (audio → response + audio) |
| `/text` | `POST` | ⌨️ Process text query (text → response + audio) |
| `/confirm` | `POST` | ✅ Confirm and execute write operations |
| `/reset` | `POST` | 🔄 Clear conversation history |

#### ⚠️ Key Technical Decisions

| 🔧 Decision | 💡 Rationale |
|-------------|--------------|
| `qwen2.5:7b` over `mistral:7b` | Mistral has inconsistent tool calling — sometimes describes tools instead of calling them |
| `qwen2.5:7b` over `qwen3:8b` | qwen3 has thinking mode overhead (25-40s vs 8-15s on CPU) |
| Removed `cross-company=true` | OData parameter caused 50+ second queries; direct `dataAreaId` filter is 0.5-2s |
| 60-second in-memory cache | Prevents redundant D365 calls for repeated queries |
| HTTP keep-alive pooling | Faster subsequent requests via connection reuse |

#### ⚡ Quick Start

```powershell
# 📦 Pull LLM model
ollama pull qwen2.5:7b

# 🐍 Start Python server
cd D3365_AI_Voice_Assitant/Python
conda activate myenv
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# ✅ Test health
curl http://localhost:8000/health

# 🎙️ Open voice assistant UI
# Browser: http://localhost:8000/ui
# D365: Warehouse Management → (OHMS) → VoxD365 Voice Assistant
```

#### 📁 Project Structure

```
D3365_AI_Voice_Assitant/
├── Python/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── agent.py        # Voice assistant orchestrator
│   │   ├── d365.py         # D365 OData client
│   │   ├── llm.py          # Ollama LLM client
│   │   ├── main.py         # FastAPI server
│   │   ├── stt.py          # Speech-to-text (Whisper)
│   │   ├── tools.py        # D365 inventory tools
│   │   └── tts.py          # Text-to-speech (Piper)
│   ├── config/
│   │   ├── __init__.py
│   │   └── settings.py     # Pydantic settings
│   ├── models/
│   │   ├── en_US-lessac-medium.onnx
│   │   └── en_US-lessac-medium.onnx.json
│   ├── PowerShell/
│   │   ├── 1-Setup-FFmpeg.ps1
│   │   ├── 2-Download-PiperModels.ps1
│   │   └── 3-Enable-VoxD365Firewall.ps1
│   ├── Static/
│   │   └── VoxD365VoiceUI.htm
│   ├── .env
│   ├── requirements.txt
│   └── README.md
└── X++/
    └── VoxD365 (USR) [OHMS]/
        ├── Classes/
        │   ├── VoxD365Control
        │   └── VoxD365ControlBuild
        ├── Forms/
        │   └── VoxD365Form
        ├── Menu Extensions/
        │   └── WHS.OHMS
        └── Resources/
            ├── VoxD365ControlHtm
            └── VoxD365ControlScript
```

---

<a id="d365-ai-sales-assistant"></a>
### 🤖 D365 AI Sales Assistant

> 📁 `D365_AI_Sales-Assistant/` — [📖 Full Documentation](D365_AI_Sales-Assistant/README.md)

A fully local, AI-powered natural language assistant integrated natively into Microsoft Dynamics 365 F&O. Sales representatives can ask questions about orders, customers, backorders, and credit risk in plain English and receive instant, data-driven answers — all without any cloud AI dependency or data leaving the environment.

#### 🏗️ Architecture

```
F&O Form (X++) → SalesAIAssistantService (X++) → Python FastAPI → Ollama qwen3:8b → D365 OData API
```

#### 🌟 Key Highlights

- 🖥️ Native F&O form accessible from **Accounts Receivable → Orders → AI Sales Assistant**
- 🐍 Python FastAPI backend running on `localhost:8000`
- 🧠 Local Ollama LLM (`qwen3:8b`) — no API costs, no data leaves the VHD
- 🔐 Live D365 data via Azure AD OAuth2 authenticated OData API
- 💳 Customer credit risk analysis from `CustomersV3` OData entity
- ✅ Validated against USMF demo data with ground truth verification

#### 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| 🖥️ F&O UI | X++ Form + Service Class |
| 🐍 Backend | Python 3.14+ / FastAPI / uvicorn |
| 🧠 AI Model | Ollama `qwen3:8b` (local) |
| 🔐 Auth | Azure AD client credentials |
| 📡 Data | D365 OData API (`SalesOrderHeadersV2`, `CustomersV3`) |

#### ✅ Validated Scenarios

| 📋 Scenario | ❓ Question | 🎯 Result |
|----------|----------|--------|
| 📦 Backorder Risk | Which customers have more than 2 backorders and what is their credit limit? | ✅ Pass |
| 💳 COD Analysis | Which customers have COD payment terms and do they have backorders? | ✅ Pass |
| 👤 Customer Summary | Full summary of customer US-003 — orders, backorders, credit, risk | ✅ Pass |
| 📋 Order Line Items | What items are on order 000698 and what is the total value? | ⚠️ Planned |

#### ⚡ Quick Start

```bash
# 🐍 Start Python server
cd D365_AI_Sales-Assistant/python
.venv\Scripts\activate.bat
uvicorn server:app --host 0.0.0.0 --port 8000 --reload

# 🖥️ Open AI Assistant in F&O
https://usnconeboxax1aos.cloud.onebox.dynamics.com/?mi=SalesAIAssistant
```

---

<a id="d365-ai-sales--revenue-intelligence"></a>
### 📊 D365 AI Sales & Revenue Intelligence

> 📁 `D365-AI-Sales_Revenue-Intelligence/` — [📖 Full Documentation](D365-AI-Sales_Revenue-Intelligence/README.md)

An AI-powered, fully embedded sales revenue intelligence dashboard built as a **custom Extensible Control** inside Microsoft Dynamics 365 F&O. Fetches live invoiced sales data via OData, aggregates it in Python, renders three interactive Chart.js visualizations, and generates an AI executive narrative using a locally running Ollama LLM — all rendered natively inside a D365 form with zero external browser dependencies.

#### 🏗️ Architecture

```
D365 Form (X++) → SalesIntelligenceService (X++) → Python FastAPI → D365 OData API
                                                  → Ollama qwen3:8b → AI Narrative
                                                  → Chart.js (AOT Resource) → 3 Charts
```

#### 🌟 Key Highlights

- 🧩 Built as a **custom D365 Extensible Control** — fully embedded, no iframe, no external browser tab
- 📊 Three interactive Chart.js charts: Top 15 Customers (bar), Top 10 Products (bar), Revenue by Category (doughnut)
- 🤖 AI executive narrative generated by local `qwen3:8b` via Ollama — no cloud dependency
- 📥 Live invoiced sales data filtered at line + header level for financial accuracy
- 🎨 All CSS inline — D365 strips `<style>` blocks; inline styles survive sandboxing
- 📦 Chart.js v4.4.0 bundled as a D365 AOT Resource — works even when internet is blocked
- ✅ Data validated 100% against SQL ground truth (`SALESSTATUS = 3`, header + line)

#### 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| 🖥️ D365 UI | X++ Extensible Control (`FormTemplateControl`) |
| 🧩 Control Script | `$dyn` / Knockout.js observable pattern |
| 🐍 Backend | Python 3.10+ / FastAPI / uvicorn |
| 📊 Charts | Chart.js v4.4.0 UMD (bundled as AOT Resource) |
| 🧠 AI Model | Ollama `qwen3:8b` (local) |
| 🔐 Auth | Azure AD client credentials (OAuth2) |
| 📡 Data | D365 OData API (`SalesOrderLines` + `$expand SalesOrderHeader`) |

#### 📌 Validated Data — USMF

| 📊 Metric | 🔢 Value |
|---|---|
| 💰 Total Revenue | **$99,451,085.50** |
| 👥 Total Customers | **29** |
| 📦 Total Orders | **708** |
| 🏆 Top Customer | **DE-001** ($7.66M) |
| 🥇 Top Product | **Projector Television** ($34.9M) |

#### 🥇 Revenue Tier Classification

| 🏆 Tier | 💰 Revenue Range | 🎨 Chart Colour |
|---|---|---|
| 💜 Platinum | $10M+ | `#7c3aed` |
| 🥇 Gold | $5M – $10M | `#d97706` |
| 🥈 Silver | $1M – $5M | `#6b7280` |
| 🥉 Bronze | Under $1M | `#92400e` |

#### 🧩 D365 AOT Components

| 📦 Component | 🗂️ Type | 📝 Purpose |
|---|---|---|
| `SalesIntelligenceControl` | X++ Class | Extensible Control — bridges X++ ↔ browser |
| `SalesIntelligenceControlBuild` | X++ Class | Required design-time companion class |
| `SalesIntelligenceService` | X++ Class | HTTP service — calls Python `/ask-chart` |
| `SalesIntelligenceTest` | X++ Runnable | Developer test utility — saves HTML to disk |
| `SalesIntelligenceDashboard` | Form | D365 form hosting the control |
| `SalesIntelligenceChartJS.js` | AOT Resource | Chart.js v4.4.0 UMD library |
| `SalesIntelligenceControl.htm` | AOT Resource | HTML shell template for the control |
| `SalesIntelligenceControlScript.js` | AOT Resource | Client-side control JavaScript logic |
| `SalesIntelligenceParameters` | Table | Configuration — server URL, timeout, IsEnabled |

#### 🔌 API Endpoints

| 🔌 Endpoint | Method | 📝 Purpose |
|---|---|---|
| `/health` | `GET` | ❤️ Server status check |
| `/test-sales-data` | `GET` | ✅ Data validation against SQL ground truth |
| `/ask-chart` | `POST` | 📊 Returns full dashboard HTML (called by X++) |
| `/dashboard` | `GET` | 🌐 Browser-accessible dashboard for localhost testing |

#### ⚠️ Key Technical Gotchas

- 🚫 **D365 strips `<style>` blocks** — all CSS must be inline `style=""` attributes
- 🚫 **OData enum filtering unsupported** — `SalesOrderLineStatus eq 'Invoiced'` returns HTTP 400; filter in Python post-fetch
- 🚫 **Injected `<script>` tags don't execute** — must extract and re-run via `new Function()`
- ✅ **Chart.js must be UMD format** — only format that exposes `Chart` global without a module bundler
- ✅ **Both header AND line status must be checked** — partial invoicing means line can be Invoiced while header is still Open

#### ⚡ Quick Start

```bash
# 🐍 Start Python server
cd D365-AI-Sales_Revenue-Intelligence/python
uvicorn server:app --host 0.0.0.0 --port 8000 --reload

# ✅ Validate data
GET http://localhost:8000/test-sales-data

# 🖥️ Open dashboard in D365
# Accounts Receivable → (OHMS) → Sales Intelligence Dashboard → Generate Dashboard
```

---

<a id="convehiclemanagement"></a>
### 🚗 ConVehicleManagement

Custom vehicle management module including tracking and maintenance logic.

---

<a id="reports-ssrs-custom-report"></a>
### 📋 Reports (SSRS Custom Report)

Custom SSRS Daily Sales Report using:

- 🗄️ TempDB Table (`TmpCarInvoice`)
- 📝 Data Contract
- 🖥️ UI Builder
- ⚙️ RDP Class
- 🎛️ Controller
- 🎨 Precision Design Layout

Report Name: **DSRReport**

---

<a id="customeraccountstamentreport-extended-ssrs-report"></a>
### 📑 CustomerAccountStamentReport (Extended SSRS Report)

> 📁 `CustomerAccountStamentReport/` — [📖 Full Documentation](CustomerAccountStamentReport/README.md)

Extension of the standard **Customer Account Statement** SSRS report. Adds a new column (`MaxTxT`) that displays the **customer group name** for each transaction row, demonstrating the complete pattern for extending standard SSRS reports without modifying any standard objects.

#### 🧩 D365 AOT Components

| 📦 Component | 🗂️ Type | 📝 Purpose |
|---|---|---|
| `CustAccountStatementExtTmp.OHMS` | Table Extension | Adds `MaxTxT` field (EDT: `Description`) to the standard temp table |
| `MaxCustAccountStatementExt` | SSRS Report | Duplicate of standard report with modified design |
| `MaxCustAccountStatementExtController_Ext` | X++ Class | Extension controller redirecting execution to the custom report |
| `MaxCustAccountStatementExtHandler` | X++ Class | Report handler — populates `MaxTxT` via `Inserting` event on the temp table |
| `MaxPrintMgtDocTypeHandlersExt` | X++ Class | Delegate subscriber redirecting Print Management to the custom design |
| `CustAccountStatementExt.OHMS` | Menu Item Extension | Routes UI navigation to the custom controller |

#### 🌟 Key Highlights

- 🛡️ **100% extension-based** — no standard objects modified
- 🔗 **Lookup chain** — `CustAccountStatementExtTmp.CustTable_AccountNum` → `CustTable.CustGroup` → `CustGroup.Name` → `MaxTxT`
- 🔁 **Two population patterns documented** — `Inserting` event (row-by-row, active) and `processReport` post-handler (single-pass, commented as equivalent)
- 🧠 **Demonstrates X++ delegates** — `PrintMgmtDocType.getDefaultReportFormatDelegate` subscriber pattern
- 🧪 **Validated on USMF** — customer `US-004` (group `10`) → `MaxTxT` = "Wholesales customers"

#### ⚡ Quick Start

1. 🔨 Build the solution
2. 🗄️ Synchronize database (table extension)
3. 🚢 Deploy reports
4. 🖨️ Configure Print Management → Customer account statement → Original → set Report format to `MaxCustAccountStatementExt.Report`
5. 🧪 Run from **Accounts receivable → Inquiries and reports → Customers → Customer account statement** (test dates `1/1/2016` to `2/2/2016` on USMF)

---

<a id="custagingwithbank-customer-aging-with-bank"></a>
### 🏦 CustAgingWithBank (Customer Aging with Bank)

> 📁 `CustAgingWithBank/` — [📖 Full Documentation](CustAgingWithBank/README.md)

A custom **Accounts Receivable** solution that combines **customer aging analysis**, **credit exposure**, and **live bank balances** on a single screen. The same pre-processed dataset is surfaced two ways: an interactive **ECharts visual form** (collapsible aging tree, bank donut/bars, management overview) and a classic **SSRS precision report** for printing and distribution.

#### 🧩 D365 AOT Components

| 📦 Component | 🗂️ Type | 📝 Purpose |
|---|---|---|
| `BCRCustAgingVisualForm` | Form | Interactive visual form — parameters: Date, DSO Number of Days, Select Customers |
| `BCRCustAgingVisualEngine` | X++ Class | Server-side engine — fills the temp table (`populate`) and serializes it to JSON (`getDataJson`) |
| `BCRCustAgingVisualControl` | X++ Class | `FormTemplateControl` hosting the HTML/JS visual; exposes the dataset as a JSON property |
| `BCRCustAgingVisualControlBuild` | X++ Class | Design-time companion class for the control |
| `BCRCustomerAgingwithBankDP` | X++ Class | SSRS Report Data Provider (`SRSReportDataProviderPreProcessTempDB`) — builds aging buckets, credit figures, bank balances |
| `BCRCustomerAgingwithBankContract` | X++ Class | Data contract — carries the as-of `FromDate` |
| `BCRCustomerAgingwithBankTmp` | Table (TempDB) | Shared pre-processed dataset (32 fields: aging, credit, bank, dimensions, DSO) |
| `BCRCustomerAgingwithBankQuery` | Query | `CustTable` with an `AccountNum` range (customer selection) |
| `BCRCustomerAgingwithBankReport` | SSRS Report | Precision design (`DataSet1`) |
| `CustTable.Report_Finance` | Table Extension | Adds `BCRCreditInsuranceValue`, `BCRPromissoryNoteValue`, `BCRPromissoryNoteType_Custom` |
| `BCRCustAgingVisual` / `…JS` / `…CSS` / `BCRCustAgingEcharts` | AOT Resources | HTML host, control JavaScript, stylesheet, and bundled Apache ECharts library |
| `BCRCustAgingVisualForm` | Display Menu Item | Opens the visual form |
| `BCRCustomerAgingwithBank` | Output Menu Item | Runs the SSRS report (`PrecisionDesign1`) |
| `AccountsReceivable.Report_Finance` | Menu Extension | Adds the form under *Inquiries and reports* |
| `OHMSCustAgingVisualView` / `Maintain` / `Inquirer` | Security Privilege / Duty / Role | Grants access to the form and the SSRS report |

#### 🌟 Key Highlights

- 🖥️ **Two delivery paths, one dataset** — the visual engine and the SSRS RDP fill the same temp-table structure (`BCRCustomerAgingwithBankTmp`)
- 🌳 **Collapsible aging tree** — Classification → Country → Channel → Invoice Account → customer rows, bucketed Not Due / 30 / 60 / 90 / 180+
- 🏦 **Live bank balances in SAR** — converted with `ExchangeRateHelper` at the as-of date, with per-bank bars and a currency-distribution donut
- 📉 **DSO indicator** — `DSO = Total / (InvSum × dsoNumber)`, divide-by-zero guarded, displayed to 7 decimals so small fractions stay visible
- 🛡️ **Credit exposure** — credit limit / utilised / available, open sales orders, credit-insurance and promissory-note cover
- 🎨 **Inline styling by design** — F&O namespaces external CSS at runtime, so the control renders with inline styles (charts via bundled ECharts)
- 🔐 **Ships with security** — role → duty → privilege chain (`OHMSCustAgingVisualInquirer`) covering both entry points

#### ⚡ Quick Start

1. 🔨 Build the **OHMS** model
2. 🗄️ Synchronize database (TempDB temp table + `CustTable` extension fields)
3. 🚢 Deploy the SSRS report `BCRCustomerAgingwithBankReport`
4. 🔐 Assign the `OHMSCustAgingVisualInquirer` role
5. 🧪 Open from **Accounts receivable → Inquiries and reports → Customer Aging with Bank**, set the Date / DSO, optionally **Select Customers**, then **Apply**

---

<a id="halwani"></a>
### 🏢 Halwani

Tailored solutions addressing unique client business processes.

---

<a id="metadata"></a>
### 🗂️ Metadata

Contains extended tables, forms, and workflows.

---

<a id="commerce_customerlistextension"></a>
### 🛒 Commerce_CustomerListExtension

Adds custom **RefNoExt** field to the customer entity with synchronization support.

---

<a id="chain_of_command"></a>
### 🔗 Chain_of_Command

Demonstrates Microsoft-recommended extension pattern using:

- 🔗 Class CoC
- 🖥️ Form CoC
- 🗄️ Data Source CoC

Ensures upgrade-safe logic extension without overlayering.

---

<a id="salesorderexcelupload-sales-order-upload-from-excel"></a>
### 📤 SalesOrderExcelUpload (Sales Order Upload from Excel)

Custom automation allowing upload of Excel (`.xlsx`) file to create:

- 📋 `SalesTable` records
- 📋 `SalesLine` records
- 💼 Financial Dimensions (`DefaultDimension`)

#### 📊 Excel Template (USMF)

| CustomerAccount | BusinessUnit | CostCenter | ItemId | Department | Qty | Project |
|----------------|-------------|------------|--------|------------|-----|---------|
| US-001 | 2 | 14 | D0001 | 22 | 5 | |
| US-001 | 3 | 14 | 1000 | 22 | 2 | |
| US-002 | 4 | 14 | D0003 | 22 | 3 | |

#### ✅ Success Message Example

```
Upload successful. Created 2 sales order(s): SO-000123, SO-000124. Total line(s): 5.
```

---

<a id="salesorderworkflow-custom-approval-workflow"></a>
### ✅ SalesOrderWorkflow (Custom Approval Workflow on SalesTable)

> 📁 `OHMS_SalesWF/` — Custom **header-level approval workflow** for the standard Sales order (`SalesTable`)

Adds a **Submit** button to the *Sales order details* form, routes the order for approval, and tracks its lifecycle through a custom workflow-status field — implemented **entirely through extensions and event handlers**, with **zero over-layering** of standard objects.

#### 🏗️ Architecture

```
User (Sales order, Draft)
        │ Submit
        ▼
OHMSSalesWFTypeSubmitManager ──► Workflow::activateFromWorkflowType(OHMSSalesWFType)
        │
        ▼
OHMSSalesWFType (Workflow Type) ──► OHMSSalesWFApproval (Approval element)
        │                                   │
        │ type events                       │ outcome events
        ▼                                   ▼
OHMSSalesWFTypeEventHandler        OHMSSalesWFApprovalEventHandler
        │                                   │
        └────────────► OHMSSalesWFStatusHelper ◄────────────┘
                              │
                              ▼
                 SalesTable.OHMSSalesWFStatus (Draft → Submit → Started → Complete/Denied/…)
```

#### 🌟 Key Highlights

- 🛡️ **100% extension-based** — no standard object (table, form, class) is over-layered
- 🔘 **Submit button on standard form** — surfaced at runtime via `FormDataUtil` / `SalesTableInteraction` post-handlers (no form metadata change)
- 🔁 **Full approval lifecycle** — Approve / Reject / Request change / Delegate / Resubmit
- 🧠 **Centralized status updates** — single helper writes the status for every event
- 🏷️ **Custom status enum** — independent of standard `VersioningDocumentState`

#### 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| 🧩 Workflow framework | D365 Workflow Type + Approval element |
| 🗄️ Data | `SalesTable` (header-level), table extension + custom enum |
| 🔘 Form enablement | X++ post-event handlers (`FormDataUtil`, `SalesTableInteraction`, `SalesTable` form) |
| 🏷️ Module | Accounts receivable (`ModuleAxapta::Customer`) |

#### 🧩 D365 AOT Components

| 📦 Component | 🗂️ Type | 📝 Purpose |
|---|---|---|
| `OHMSSalesWFStatus` | Base Enum | Workflow status values (Draft, Submit, Started, …) |
| `SalesTable.OHMS` | Table Extension | Adds the `OHMSSalesWFStatus` field to SalesTable |
| `OHMSSalesWFQuery` | Query | Document query over SalesTable (Dynamic Fields = Yes) |
| `OHMSSalesWFCategory` | Workflow Category | Links workflow to module (`Customer`) |
| `OHMSSalesWFType` | Workflow Type | The workflow template |
| `OHMSSalesWFApproval` | Workflow Approval | Approval element referenced by the type |
| `OHMSSalesWFTypeDocument` | X++ Class | Returns the workflow query |
| `OHMSSalesWFTypeSubmitManager` | X++ Class | Activates the workflow on Submit |
| `OHMSSalesWFTypeEventHandler` | X++ Class | Type-level events (started/canceled/completed) |
| `OHMSSalesWFApprovalEventHandler` | X++ Class | Approval outcome events (denied/changeReq/returned) |
| `OHMSSalesWFStatusHelper` | X++ Class | Centralized status-update helper |
| `OHMSSalesTableWorkflowEventHandler` | X++ Class | Enables the workflow button on the standard form |

#### 💻 Component Snippets

**Status enum — `OHMSSalesWFStatus`**
```xpp
// Draft at index 0 → every order defaults to Draft (the only submittable state)
Draft, Submit, Started, Cancelled, Complete, Denied, ChangeRequested, Returned
```

**Document class — `OHMSSalesWFTypeDocument`**
```xpp
public queryName getQueryName()
{
    return querystr(OHMSSalesWFQuery);
}
```

**Submit manager — `OHMSSalesWFTypeSubmitManager`**
```xpp
workflowSubmitDialog = WorkflowSubmitDialog::construct(args.caller().getActiveWorkflowConfiguration());
workflowSubmitDialog.run();
if (workflowSubmitDialog.parmIsClosedOK())
{
    Workflow::activateFromWorkflowType(workflowTypeStr(OHMSSalesWFType),
        salesTable.RecId, workflowSubmitDialog.parmWorkflowComment(), NoYes::No);
    salesTable.OHMSSalesWFStatus = OHMSSalesWFStatus::Submit;
    salesTable.update();
}
args.caller().updateWorkflowControls();
```

**Type event handler — `OHMSSalesWFTypeEventHandler`**
```xpp
public void started(WorkflowEventArgs _args)
{
    OHMSSalesWFStatusHelper::updateWorkflowStatus(
        _args.parmWorkflowContext().parmRecId(), OHMSSalesWFStatus::Started);
}   // canceled → Cancelled, completed → Complete
```

**Approval event handler — `OHMSSalesWFApprovalEventHandler`**
```xpp
public void denied(WorkflowElementEventArgs _args)
{
    OHMSSalesWFStatusHelper::updateWorkflowStatus(
        _args.parmWorkflowContext().parmRecId(), OHMSSalesWFStatus::Denied);
}   // changeRequested → ChangeRequested, returned → Returned, completed → Complete
```

**Status helper — `OHMSSalesWFStatusHelper`**
```xpp
public static void updateWorkflowStatus(RefRecId _recId, OHMSSalesWFStatus _status)
{
    SalesTable salesTable;
    ttsbegin;
    select forupdate salesTable where salesTable.RecId == _recId;
    if (salesTable.RecId != 0)
    {
        salesTable.OHMSSalesWFStatus = _status;
        salesTable.update();
    }
    ttscommit;
}
```

**Form enablement — `OHMSSalesTableWorkflowEventHandler`** (surfaces the button, no over-layering)
```xpp
// 1) Make the record submittable while in Draft
[PostHandlerFor(classStr(FormDataUtil), staticMethodStr(FormDataUtil, canSubmitToWorkflow))]
// 2) Point the running form at OHMSSalesWFType + updateWorkflowControls()
[PostHandlerFor(classStr(SalesTableInteraction), methodStr(SalesTableInteraction, enableHeaderActions))]
// 3) Force the button group visible
[PostHandlerFor(formStr(SalesTable), formMethodStr(SalesTable, canSubmitToWorkflow))]
salesTableDetails.design().controlName('WorkflowActionBarButtonGroup').visible(true);
```
> 📖 Technique reference: [Extend `canSubmitToWorkflow` without over-layering](https://axraja.blogspot.com/2020/03/d365ax7-extend-cansubmittoworkflow-in.html)

#### ⚠️ Key Technical Gotchas

- 🪤 **`Customer` vs `AccountsReceivable`** — the *Accounts receivable workflows* page filters on `ModuleAxapta::Customer`, **not** `AccountsReceivable`. Set the category module to `Customer` (the value standard customer workflows use), or the type registers but never appears.
- 🔄 **Reset usage data** — the workflow type lookup is cached **per user**; after changing the category module run **System administration → Users → Reset usage data**. A server restart does **not** clear it.
- 🔀 **Runtime override** — the standard form is bound to `SalesLine` / `RetailSalesLineWFType`; handler #2 overrides this to the header-level `OHMSSalesWFType` at runtime.
- 🔘 **Button needs an active config** — the Submit button only renders once a workflow configuration is **activated** for the type.

#### ⚡ Quick Start

1. 🔨 Build the **OHMS** model with **Synchronize Database** (0 errors)
2. 🗄️ **Accounts receivable → Setup → Accounts receivable workflows → New → Sales order workflow**
3. 🎨 In the editor (use **Edge**): drag **OHMSSalesWFApproval** between Start & End, set assignment (User), subject & instructions, then **Activate**
4. 🔄 **Reset usage data** + hard-refresh
5. 🧪 Open a Sales order in **Draft** → **Submit** button appears → submit and watch `OHMSSalesWFStatus` advance

---

<a id="ohms-service-integration"></a>
### 🔌 OHMS Service Integration

Secure service pattern including:

- 📝 DataContract classes
- 🏢 `changecompany` usage
- 🛡️ Exception handling (CLR + X++)
- 🌐 API endpoint exposure

Example endpoint:

```
/api/services/ohmsServiceGroup/ohmsService/Create
```

---

<a id="loyaltymemberintegration-custom-odata-entity--action"></a>
### 🎁 LoyaltyMemberIntegration (Custom OData Entity + Action)

> 📁 `LoyaltyMemberIntegration/` — [📖 Full Documentation](LoyaltyMemberIntegration/README.md)

A from-scratch **custom OData integration surface** that lets an external system (e-commerce site, CRM, loyalty engine) create, read, and update loyalty members **and invoke a business operation** — `addPoints` adds points and recalculates the member's tier server-side. Demonstrates the full anatomy of an F&O integration endpoint: custom table → public data entity → **unmapped (computed) field** → **bound OData action** → secured CRUD, all driven and verified from Postman.

#### 🏗️ Architecture

```
External system (storefront / CRM / loyalty engine)
        │  OAuth2 client-credentials  ·  reports activity ("add 600 points")
        ▼ OData REST  /data/OHM_LoyaltyMembers
┌─────────────────────────────────────────────────────────────┐
│         OHM_LoyaltyMemberEntity  (public OData entity)        │
│   GET / POST / PATCH  +  bound action: …/…addPoints           │
│   postLoad() ──► computes unmapped field PointsToNextTier     │
└───────────────┬───────────────────────────────┬─────────────┘
                │ delegates                       │ reads/writes
                ▼                                 ▼
      OHM_LoyaltyMemberHelper            OHM_LoyaltyMember (table)
   resolveTier · nextTierThreshold ────► PointsBalance, Tier, …
   addPoints (ttsbegin + row lock)       (D365 owns the tier rule)
                                                  │
                                                  ▼
                                    OHM_LoyaltyMemberForm (Simple List)
```

#### 🌟 Key Highlights

- 🚪 **Custom public OData entity** — `OHM_LoyaltyMember` exposed at `/data/OHM_LoyaltyMembers`, no DMF staging (live OData)
- ⚙️ **Bound OData action** — `[SysODataActionAttribute('addPoints', true)]` lets the caller *invoke logic*, not just edit columns; D365 owns the tier rule
- 🧮 **Unmapped (computed) field** — `PointsToNextTier` filled in `postLoad`, surfaced only on the API (not stored, not on the form)
- 🔒 **Concurrency-safe writes** — `addPoints` runs in `ttsbegin/ttscommit` with `selectForUpdate` to prevent lost updates
- 🪪 **Idempotent by design** — `MemberId` is a unique alternate key owned by the source system; duplicate POST is rejected ("record already exists")
- 🔗 **Validated customer link** — optional `CustAccount` relation to `CustTable` (member can exist before becoming a customer)
- 🧪 **End-to-end verified in Postman** — GET / POST / PATCH / action, plus tier promotion, redemption/demotion, and guard-rail tests

#### 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| 🗄️ Data | Table `OHM_LoyaltyMember` (Main, per-company), EDTs, base enum |
| 🚪 OData | Public Data Entity `OHM_LoyaltyMemberEntity` → `OHM_LoyaltyMembers` |
| 🧠 Logic | X++ class `OHM_LoyaltyMemberHelper` (tier rules + transactional point updates) |
| 🖥️ UI | Form `OHM_LoyaltyMemberForm` (Simple List) + display menu item + menu extension |
| 🔐 Auth | Azure AD OAuth2 client credentials (bearer token) |
| 📡 Client | Postman (GET / POST / PATCH / bound action) |

#### 🧩 D365 AOT Components

| 📦 Component | 🗂️ Type | 📝 Purpose |
|---|---|---|
| `OHM_LoyaltyTier` | Base Enum | Tier values: None, Bronze, Silver, Gold, Platinum |
| `OHM_LoyaltyMemberId` | EDT (String) | Member key, owned by the external system |
| `OHM_LoyaltyPoints` | EDT (Int) | Points balance |
| `OHM_LoyaltyMember` | Table | Member master data (unique key `MemberIdIdx`, `CustTable` relation) |
| `OHM_LoyaltyMemberEntity` | Data Entity | Public OData contract; hosts `postLoad` + `addPoints` action |
| `OHM_LoyaltyMemberHelper` | X++ Class | Tier resolution, next-tier threshold, transactional `addPoints` |
| `OHM_LoyaltyMemberForm` | Form | Simple List view inside F&O |
| `OHM_LoyaltyMember` | Display Menu Item | Opens the form |
| `<Module>.OHMS` | Menu Extension | Places the menu item under the module |

#### 💻 Component Snippets

**Tier rules (single source of truth) — `OHM_LoyaltyMemberHelper`**
```xpp
#define.SilverThreshold(500)
#define.GoldThreshold(1500)
#define.PlatinumThreshold(5000)

public static OHM_LoyaltyTier resolveTier(OHM_LoyaltyPoints _points)
{   // highest tier first
    if (_points >= #PlatinumThreshold) return OHM_LoyaltyTier::Platinum;
    if (_points >= #GoldThreshold)     return OHM_LoyaltyTier::Gold;
    if (_points >= #SilverThreshold)   return OHM_LoyaltyTier::Silver;
    return OHM_LoyaltyTier::Bronze;
}
```

**Transactional point update — `OHM_LoyaltyMemberHelper::addPoints`**
```xpp
ttsbegin;
member = OHM_LoyaltyMember::find(_memberId, true); // row lock
if (!member.RecId)                       { ttsabort; throw error("Member not found."); }
if (member.PointsBalance + _points < 0)  { ttsabort; throw error("Balance cannot be negative."); }
member.PointsBalance += _points;
member.Tier = OHM_LoyaltyMemberHelper::resolveTier(member.PointsBalance);
member.update();
ttscommit;
```

**Computed field + bound action — `OHM_LoyaltyMemberEntity`**
```xpp
public void postLoad()
{   // unmapped field, computed on every read
    super();
    this.PointsToNextTier =
        OHM_LoyaltyMemberHelper::nextTierThreshold(this.PointsBalance) - this.PointsBalance;
}

[SysODataActionAttribute('addPoints', true)] // bound to one member ("this")
public int addPoints(int pointsToAdd)
{
    return OHM_LoyaltyMemberHelper::addPoints(this.MemberId, pointsToAdd).PointsBalance;
}
```

**Postman — create, then invoke the action**
```
POST /data/OHM_LoyaltyMembers
{ "dataAreaId":"USMF", "MemberId":"LM-0001", "MemberName":"Test Member", "PointsBalance":0 }

POST /data/OHM_LoyaltyMembers(dataAreaId='USMF',MemberId='LM-0001')/Microsoft.Dynamics.DataEntities.addPoints
{ "pointsToAdd": 600 }      // → 200, returns new balance; Tier flips to Silver
```

#### ⚠️ Key Technical Gotchas

- 🚫 **Reserved field names** — `CreatedBy/CreatedDateTime/ModifiedBy/ModifiedDateTime` cannot be exposed on an entity under those names; remove them or rename (e.g. `CreatedOn`) keeping the `Data Field` mapping.
- 🧮 **Unmapped ≠ computed** — `PointsToNextTier` is an *unmapped* field filled in `postLoad` (X++), not a SQL *computed* field; `Is Computed Field = No`.
- 🔗 **Action URL hygiene** — a stray `}` / space between the base variable and the collection name yields `404 "No route data was found"`. Suffix must be exactly `/Microsoft.Dynamics.DataEntities.addPoints`.
- 🪪 **Idempotency** — re-POSTing an existing `MemberId` returns "The record already exists"; middleware should treat this as success on retry.
- 🔁 **DB sync required** — the OData endpoint and action don't register until **Synchronize database** completes (calls 404 before that).
- 🧾 **CustAccount validation** — the `CustTable` relation rejects a `CustAccount` that doesn't exist in the company; link only real accounts (e.g. `US-001` on USMF).

#### ⚡ Quick Start

1. 🔨 Build the **OHMS** model and **Synchronize database** (0 errors)
2. 🔑 In Postman, set the OAuth2 bearer token and a base URL variable ending in `/data/`
3. 📨 **POST** `OHM_LoyaltyMembers` to create `LM-0001`
4. ➕ Call the **addPoints** action with `{ "pointsToAdd": 600 }` → tier becomes **Silver**; `{ "pointsToAdd": 900 }` → **Gold**
5. 🔍 **GET** the single member and confirm `PointsToNextTier` recalculates on each read
6. 🖥️ Open **Loyalty members** in F&O to see the row, customer link, and tier

---

<a id="rosaftlocalization-ro-saf-t--d406--er-integration"></a>
### 🇷🇴 ROSaftLocalization (RO SAF-T / D406 — ER Integration)

> 📁 `ROSaftLocalization/` — [📖 Full Documentation](ROSaftLocalization/README.md)

A miniature **Romanian SAF-T (D406) localization package** built to replicate — and troubleshoot — how country localizations sit on top of the standard **Electronic Reporting (ER)** engine. A custom ER format (`SAF-T Format (RO test)`) is derived from Microsoft's Standard Audit File (SAF-T) data model, designed, mapped, and completed; a small X++ package then invokes it from code via `ERObjectsFactory` — the same architecture behind a real "Generate declaration" menu item. Built while diagnosing a production SAF-T failure after a Microsoft platform upgrade, and doubles as a hands-on ER troubleshooting playbook.

#### 🏗️ Architecture

```
GL menu (RO SAF-T) ──► ROSaftGenerate ──► SAFTRoGenerateController ──► SAFTRoGenerateService
                                                       │ reads mapping RecId
                                                       ▼
                                         ROSaftParameters (singleton table + form)
                                                       │
                                                       ▼ ERObjectsFactory::createFormatMappingRunByFormatMappingId
                                    ER engine ──► SAF-T model mapping (Microsoft, base)
                                              ──► SAF-T Format (RO test) [derived, Completed]
                                                       │
                                                       ▼
                                                  SAFT_RO.xml
```

#### 🌟 Key Highlights

- 🇷🇴 **Derived ER format** — `SAF-T Format (RO test)` created under an own configuration provider from Microsoft's SAF-T data model (root: Audit File), the exact technique used by real country localizations (Microsoft ships no native RO SAF-T format)
- 🧾 **Parameter System Design Pattern** — singleton `ROSaftParameters` table (Key/KeyIdx, Found cache, find/update/delete overrides) storing the ER format mapping RecId
- 🔍 **Custom `SysTableLookup`** on `ERFormatMappingTable` plus **display methods** showing mapping name/description next to the raw RecId
- ⚙️ **SysOperation stack** — contract (From/To dates) → service → controller invoking ER via `ERObjectsFactory::createFormatMappingRunByFormatMappingId`
- 🗂️ **Full ISV-style packaging** — own EDT (extends `RefRecId`), label file, GL submenu, privileges → duty → role, zero BP warnings
- 🚨 **Three production-class ER failures hit and resolved** — ambiguous default model mapping, country/region mismatch on the legal entity, and Draft-vs-Completed runtime resolution
- ✅ **End-to-end verified** — generates `SAFT_RO.xml` on 10.0.48 / USMF through the complete menu → code → ER pipeline

#### 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| 📄 Reporting engine | Electronic Reporting (ER) — derived format on Microsoft's SAF-T model |
| 🗄️ Data | `ROSaftParameters` (Parameter pattern), EDT `ROSaftERFormatMappingRecId` (extends `RefRecId`) |
| 🧠 Logic | SysOperation (contract / service / controller), `ERObjectsFactory` API (`Microsoft.Dynamics365.LocalizationFramework`) |
| 🖥️ UI | Form (Simple List) + custom lookup + display methods, GL submenu **RO SAF-T** |
| 🔐 Security | Privileges → `ROSaftMaintainDuty` → `ROSaftClerk` role |

#### 🧩 D365 AOT Components

| 📦 Component | 🗂️ Type | 📝 Purpose |
|---|---|---|
| `ROSaftParameters` | Table | Singleton parameters (Parameter pattern) — stores the ER format mapping RecId; display methods for mapping name/description |
| `ROSaftERFormatMappingRecId` | EDT (Int64) | Extends `RefRecId`, ReferenceTable = `ERFormatMappingTable` |
| `ROSaftParameters` | Form | Simple List — setup form with custom `SysTableLookup` on ER format mappings |
| `SAFTRoGenerateContract` | X++ Class | SysOperation data contract (reporting period) |
| `SAFTRoGenerateService` | X++ Class | Reads parameters, invokes ER via `ERObjectsFactory::createFormatMappingRunByFormatMappingId` |
| `SAFTRoGenerateController` | X++ Class | SysOperation controller — entry point of the action menu item |
| `ROSaftParameters` / `ROSaftGenerate` | Display / Action Menu Items | Open setup form / run generation |
| `GeneralLedger.OHMS` | Menu Extension | Submenu **RO SAF-T** hosting both menu items |
| `ROSaftParametersMaintain` / `ROSaftGenerateProcess` | Security Privileges | Cover the two menu items |
| `ROSaftMaintainDuty` / `ROSaftClerk` | Security Duty / Role | Duty → role chain |
| `ROSaft` | Label File | All labels (en-US) |

#### ⚠️ Key Technical Gotchas

- 🚫 **Never author under the Microsoft provider** — register an own configuration provider and set it active before deriving; authoring as Microsoft collides with future Microsoft config updates
- 🔀 **"More than one model mapping exists…"** — the default-mapping flag is **per data-model root**; set `Default for model mapping = Yes` on the config **named in the error**, not a look-alike
- 🌍 **"Configuration doesn't support the country/region…"** — the selected config's ISO country codes exclude the legal entity's country; verify the right mapping is selected (display methods make this visible at a glance)
- 📝 **"Expected format mapping has not been found"** — the runtime API resolves only **Completed** versions; the designer's Run works on Drafts and masks this. `Change status > Complete` before invoking from code
- 🧩 **`RefRecId` EDT must be Int64** — creating the EDT from the *EDT Int* template throws "Data type mismatch" on Extends
- 🔇 **Silent batch failures** — check **Org admin → ER → Electronic reporting jobs** and batch retry counts; re-run **interactively (Batch = No)** to surface the real error

#### ⚡ Quick Start

1. 📥 Download **GER Configurations – All** from LCS Shared asset library → extract flat to `C:\ERConfigs`
2. 🗂️ Register a **File system** repository on the Microsoft provider tile → Open → import **SAF-T Financial data model mapping** (latest, pulls the model recursively)
3. 🏷️ Create an own configuration provider → **Set active** → derive `SAF-T Format (RO test)` from the SAF-T model (root: Audit File) → design → bind → **Complete**
4. 🔨 Build the **OHMS** model + **Synchronize database** (security is data — sync required)
5. ⚙️ **General ledger → RO SAF-T → RO SAF-T parameters** → pick the mapping via lookup → Save
6. 🧪 **General ledger → RO SAF-T → Generate SAF-T declaration (RO)** → OK → ER prompt → OK → `SAFT_RO.xml` downloads

---

<a id="development-guidelines"></a>
## 📐 Development Guidelines

- 🔗 Use Chain of Command
- 🚫 Avoid overlayering
- ✅ Validate before insert
- 🔄 Use proper transaction handling
- 📛 Follow OHMS naming standards

---

<a id="testing--verification"></a>
## 🧪 Testing & Verification

- 🏭 Use Contoso demo data (USMF)
- 💼 Validate financial dimensions
- ✅ Confirm `SalesTable` & `SalesLine` creation
- 🛡️ Ensure no standard logic is broken

---

<a id="contributing"></a>
## 🤝 Contributing

1. 🍴 Fork repository
2. 🌿 Create feature branch
3. 📐 Follow coding standards
4. 🧪 Test thoroughly
5. 📬 Submit pull request

---

© OHMS – Omar Hesham Mohamed Shehab  
🏗️ D365 Finance & Operations Customization Repository