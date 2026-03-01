# 🏗️ D365 Finance and Operations Customizations (FO_Customization)

A curated collection of real-world customizations, tutorials, and best practices for Microsoft Dynamics 365 Finance and Operations (D365FO), developed and maintained by **Omar Hesham Mohamed Shehab** under the **OHMS** model.

---

## 📚 Table of Contents

- [🎯 Project Overview](#project-overview)
- [📁 Repository Structure](#repository-structure)
- [✨ Key Features](#key-features)
- [🚀 Getting Started](#getting-started)
- [🧩 Customization Modules](#customization-modules)
  - [🤖 D365 AI Sales Assistant](#d365-ai-sales-assistant)
  - [📊 D365 AI Sales & Revenue Intelligence](#d365-ai-sales--revenue-intelligence)
  - [🚗 ConVehicleManagement](#convehiclemanagement)
  - [📋 Reports (SSRS Custom Report)](#reports-ssrs-custom-report)
  - [🏢 Halwani](#halwani)
  - [🗂️ Metadata](#metadata)
  - [🛒 Commerce_CustomerListExtension](#commerce_customerlistextension)
  - [🔗 Chain_of_Command](#chain_of_command)
  - [📤 SalesOrderExcelUpload](#salesorderexcelupload-sales-order-upload-from-excel)
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

- 🤖 **D365_AI_Sales-Assistant** — AI-powered natural language sales assistant integrated natively into D365 F&O
- 📊 **D365-AI-Sales_Revenue-Intelligence** — AI-powered sales revenue dashboard with Chart.js visualizations embedded as a D365 Extensible Control
- 🚗 **ConVehicleManagement** — Vehicle tracking and maintenance scheduling
- 📋 **Reports** — Custom SSRS reporting solution
- 🏢 **Halwani** — Client-specific customizations
- 🗂️ **Metadata** — Data model and UI extensions
- 🛒 **Commerce_CustomerListExtension** — Customer entity extension
- 🔗 **Chain_of_Command** — CoC implementation examples
- 📤 **SalesOrderExcelUpload** — Excel-driven sales order automation
- 🔌 **OHMS Service Integration** — Custom integration service module

---

<a id="key-features"></a>
## ✨ Key Features

- 🛡️ Upgrade-safe customizations using Chain of Command
- 🏭 Real-world client implementations
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