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
  - [🏢 Halwani](#halwani)
  - [🗂️ Metadata](#metadata)
  - [🛒 Commerce_CustomerListExtension](#commerce_customerlistextension)
  - [🔗 Chain_of_Command](#chain_of_command)
  - [📤 SalesOrderExcelUpload](#salesorderexcelupload-sales-order-upload-from-excel)
  - [✅ SalesOrderWorkflow (Custom Approval Workflow)](#salesorderworkflow-custom-approval-workflow)
  - [🔌 OHMS Service Integration](#ohms-service-integration)
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
- 🏢 **Halwani** — Client-specific customizations
- 🗂️ **Metadata** — Data model and UI extensions
- 🛒 **Commerce_CustomerListExtension** — Customer entity extension
- 🔗 **Chain_of_Command** — CoC implementation examples
- 📤 **SalesOrderExcelUpload** — Excel-driven sales order automation
- ✅ **SalesOrderWorkflow** — Custom header-level approval workflow on the Sales order (`SalesTable`), surfacing a Submit button with full approval lifecycle, no over-layering
- 🔌 **OHMS Service Integration** — Custom integration service module

---

<a id="key-features"></a>
## ✨ Key Features

- 🛡️ Upgrade-safe customizations using Chain of Command
- 🏭 Real-world client implementations
- 🎙️ Voice-enabled warehouse assistant with tap-to-talk interface
- 🤖 AI-powered natural language querying of live ERP data
- 📊 AI-powered embedded revenue intelligence dashboards with Chart.js
- 📋 Reporting, services, and automation examples
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
