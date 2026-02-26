# D365 Sales AI Assistant

A fully local, AI-powered natural language assistant for Microsoft Dynamics 365 Finance & Operations. Ask questions about sales orders, customers, backorders, and credit risk in plain English — and get instant, data-driven answers — all without any cloud AI dependency or data leaving your environment.

---

## 📋 Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Repository Structure](#repository-structure)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Starting the System](#starting-the-system)
- [Usage](#usage)
- [Live Demo — Validated Scenarios](#live-demo--validated-scenarios)
- [API Reference](#api-reference)
- [Known Limitations](#known-limitations)
- [Roadmap](#roadmap)

---

## Overview

The D365 Sales AI Assistant is a proof-of-concept integration between Microsoft Dynamics 365 F&O and a locally-hosted Large Language Model (LLM). It enables sales representatives to query live ERP data using natural language directly from within the F&O interface — no exports, no stale spreadsheets, no external cloud services.

**Key highlights:**

- Native F&O form (`SalesAIAssistant`) accessible from Accounts Receivable → Orders → AI Sales Assistant
- Python FastAPI backend running on `localhost:8000`
- Local Ollama LLM using `qwen3:8b` — no API costs, no data leaves the VHD
- Live D365 data via Azure AD OAuth2 authenticated OData API
- Natural language intent detection with regex-based entity extraction
- Customer credit risk analysis from `CustomersV3` OData entity
- Validated against USMF demo data with ground truth verification

---

## Architecture

```
User types question in F&O form
        │
        ▼
SalesAIAssistant (X++ Form)
        │
        ▼
SalesAIAssistantService (X++ Class)
  HTTP POST → localhost:8000/ask-text
        │
        ▼
server.py (FastAPI)
        │
        ▼
ai_engine.py
  ├── detect_intent()     — extracts order/customer from question
  ├── fetch_context()     — determines what D365 data is needed
  ├── build_prompt()      — formats data for the LLM
  └── call_ollama()       — sends prompt to qwen3:8b
        │
        ▼
odata.py
  └── fetch_odata()       — Azure AD token + OData API call
        │
        ▼
D365 OData API (live data)
        │
        ▼
Ollama qwen3:8b (localhost:11434)
        │
        ▼
Plain text answer → X++ form → Sales rep
```

### Component Map

| Layer | Component | Location | Purpose |
|-------|-----------|----------|---------|
| F&O Form | `SalesAIAssistant` | Visual Studio — Model: OHMS | Chat UI for sales reps |
| X++ Service | `SalesAIAssistantService` | Visual Studio — Model: OHMS | HTTP bridge to Python |
| X++ Table | `SalesAIAssistantParameters` | Visual Studio — Model: OHMS | API config storage |
| X++ Menu | `AccountsReceivable.Extension` | Visual Studio — Model: OHMS | AR menu integration |
| X++ Job | `AIAssistantDataDump` | Visual Studio — Model: OHMS | Ground truth data export |
| API Server | `server.py` | `python/` | FastAPI routing layer |
| AI Engine | `ai_engine.py` | `python/` | Intent, context, Ollama |
| OData Layer | `odata.py` | `python/` | D365 auth + data fetch |
| Config | `config.py` + `.env` | `python/` | Credentials and settings |
| LLM | Ollama `qwen3:8b` | `localhost:11434` | Local AI inference |
| Data | D365 OData API | `usnconeboxax1aos/data` | Live F&O data |

---

## Repository Structure

```
D365_AI_Sales-Assistant/
│
├── python/                          # Python FastAPI backend
│   ├── server.py                    # FastAPI endpoints + startup warm-up
│   ├── ai_engine.py                 # Intent detection, prompt building, Ollama
│   ├── odata.py                     # Azure AD auth + OData data fetching
│   ├── config.py                    # Environment variable loader
│   └── .env                         # Credentials (never commit this file)
│
├── X++/                             # D365 F&O X++ objects
│   ├── SalesAIAssistant.xpp         # Form — chat UI
│   ├── SalesAIAssistantService.xpp  # Service class — HTTP bridge
│   ├── SalesAIAssistantParameters.xpp # Parameters table
│   └── AIAssistantDataDump.xpp      # Ground truth data export job
│
├── D365_AI_Data.txt                 # Generated ground truth data (git-ignored)
└── README.md                        # This file
```

---

## Prerequisites

| Requirement | Version | Notes |
|-------------|---------|-------|
| Python | 3.14+ | |
| Ollama | Latest | Must be running before starting server |
| qwen3:8b model | — | `ollama pull qwen3:8b` |
| D365 F&O VHD | USMF demo data | `usnconeboxax1aos` |
| Visual Studio | 2019/2022 | With D365 dev tools |
| Azure AD App Registration | — | Client credentials flow |

---

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/OmarHeshamShehab/FO_Customizations.git
cd FO_Customizations/D365_AI_Sales-Assistant
```

### 2. Set up Python virtual environment

```bash
cd python
python -m venv .venv
.venv\Scripts\activate.bat
pip install fastapi uvicorn httpx python-dotenv requests
```

### 3. Pull the Ollama model

```bash
ollama pull qwen3:8b
```

### 4. Create the `.env` file

```env
TENANT_ID=your_tenant_id_here
CLIENT_ID=your_client_id_here
CLIENT_SECRET=your_client_secret_here
ODATA_BASE_URL=https://your_f&o_instance.dynamics.com/data
COMPANY=usmf
OLLAMA_URL=http://localhost:11434
OLLAMA_MODEL=qwen3:8b
HOST=0.0.0.0
PORT=8000
```

### 5. Deploy X++ objects

- Open Visual Studio with D365 developer tools
- Import all X++ files into the **OHMS** model
- Build the model (Ctrl+Shift+B)
- Sync the database

### 6. Update the parameters table

After first build and sync, run this SQL to set the correct timeout:

```sql
UPDATE [AxDB].[dbo].[SALESAIASSISTANTPARAMETERS]
SET TIMEOUTSECONDS = 300
WHERE RECID = (SELECT TOP 1 RECID FROM [AxDB].[dbo].[SALESAIASSISTANTPARAMETERS])
```

---

## Configuration

### Azure AD App Registration

| Setting | Value |
|---------|-------|
| Tenant ID | `your_tenant_id_here` |
| Client ID | `your_client_id_here` |
| Resource URL | `https://your_f&o_instance.dynamics.com/` |
| Grant Type | `client_credentials` |

### Key Technical Decisions

| Decision | Choice | Reason |
|----------|--------|--------|
| AI Model | `qwen3:8b` via Ollama | Runs locally, no API costs, no data leaves VHD |
| Data Source | Live OData API | Always current, no stale CSV exports |
| Auth Method | Azure AD client credentials | Secure, no user credentials stored |
| X++ Integration | `System.Net.Http` direct HTTP | No custom service needed |
| Response Format | Plain text `/ask-text` endpoint | Avoids X++ `str` 256-char JSON parsing limit |
| Backorder Filter | Python-side filtering | D365 OData does not support enum filtering in URL |

---

## Starting the System

Run these steps in order every session:

### Step 1 — Start Ollama

```bash
ollama serve
```

### Step 2 — Start Python Server

```bash
cd python
.venv\Scripts\activate.bat
uvicorn server:app --host 0.0.0.0 --port 8000 --reload
```

Expected startup output:
```
Server starting — warming up Ollama model...
Ollama warm-up complete — model loaded into memory
Startup complete — server ready.
```

### Step 3 — Wake the AOS

> ⚠️ **Critical:** The D365 VHD AOS hibernates after inactivity. Open the F&O browser and navigate to **Accounts Receivable → Orders → All Sales Orders**. Wait for the full page load before using the assistant. Skipping this step will cause OData timeouts.

### Step 4 — Open the AI Assistant

```
https://usnconeboxax1aos.cloud.onebox.dynamics.com/?mi=SalesAIAssistant
```

Or navigate via: **Accounts Receivable → Orders → AI Sales Assistant**

### Step 5 — Verify Health

```
http://localhost:8000/health
```

Expected: `{"status": "ok", "model": "qwen3:8b", "company": "usmf"}`

---

## Usage

The form provides three input fields:

| Field | Purpose | Required |
|-------|---------|----------|
| Customer ID | Filter by customer account (e.g. `US-003`) | Optional |
| Sales Order ID | Filter by order number (e.g. `000698`) | Optional |
| Question | Natural language question | Required |

**Tips:**
- Leave Customer ID and Sales Order ID blank for broad questions (backorders, COD analysis)
- Fill in Customer ID for customer-specific questions
- Fill in both for order-specific questions
- Click **Clear** to reset all fields after each inquiry

---

## Live Demo — Validated Scenarios

All scenarios validated against USMF demo data ground truth.

---

### Scenario 1 — Backorder Risk Analysis

**Question:** Which customers have more than 2 backorders and what is their credit limit? Are any of them at risk?

**Answer:**

The customers with more than 2 backorders are:

- **US-003** (7 backorders) – Credit Limit: $400,000.00
- **US-027** (5 backorders) – Credit Limit: $100,000.00
- **US-001** (3 backorders) – Credit Limit: $500,000.00

**Risk Analysis:**
- **US-027** has 5 backorders and a credit limit of $100,000.00. While the credit limit is sufficient, the high number of backorders may indicate potential supply chain or fulfillment issues, which could impact customer satisfaction and order delivery.
- **US-003** has 7 backorders and a credit limit of $400,000.00. This is a significant number of backorders, which could affect customer trust and order fulfillment.
- **US-001** has 3 backorders and a credit limit of $500,000.00. The credit limit is adequate, but the backorders should be monitored to ensure timely resolution.

No customers are currently on hold, and all have open credit status. However, the number of backorders for US-003 and US-027 warrants closer attention to mitigate risk.

> ✅ **Validation note:** Return orders (SalesType = ReturnItem) are correctly excluded from backorder counts. The system matches OData's 37 true backorders vs the raw X++ count of 42 which incorrectly included 5 return orders.

---

### Scenario 2 — Order Status Inquiry

**Question:** Order 000698 is stuck. What items are on it and what is the total value?
*(Sales Order ID field: `000698`)*

**Answer:**

The order **000698** is currently in a **Backorder** status. However, the specific items on the order and their total value are not available in the current data context.

> ⚠️ **Known gap:** Order line items require `SalesLineV2` OData entity integration which is planned for the next iteration. See [Roadmap](#roadmap).

---

### Scenario 3 — COD Payment Terms Analysis

**Question:** Which customers have COD payment terms and do they have backorders? Compare their credit limits.

**Answer:**

The customer with COD payment terms is **US-021 - Otter Wholesales**. They have a credit limit of **$250,000.00** and **no backorders**.

No other customers have COD payment terms.

> ✅ **Validated:** US-021 is the only COD customer in USMF demo data.

---

### Scenario 4 — Full Customer Summary

**Question:** Give me a full summary of this customer. How many orders do they have, how many are backorders, what is their credit limit and payment terms, and are they at risk?
*(Customer ID field: `US-003`)*

**Answer:**

**Customer:** Forest Wholesales (US-003)
**Total Orders:** 31
**Backorders:** 7
**Credit Limit:** $400,000.00
**Payment Terms:** Net 45
**Risk Status:** Low risk. The customer has a credit limit of $400,000.00, which is sufficient for their order history. They have 7 backorders, but no indication of payment issues or on-hold status. Their payment terms are standard, and there are no signs of financial risk.

> ✅ **Validated:** All figures match ground truth from USMF data.

---

## API Reference

| Method | Endpoint | Purpose | Used By |
|--------|----------|---------|---------|
| GET | `/health` | Server health check | Form init, monitoring |
| GET | `/test-odata` | OData connectivity test | Debugging |
| POST | `/ask` | Full JSON response with metadata | Postman / testing |
| POST | `/ask-text` | Plain text answer only | X++ form (production) |

### Request Body (`/ask-text`)

```json
{
  "question": "What is the status of order 000697?",
  "sales_order_id": "000697",
  "customer_id": ""
}
```

### Interactive API Docs

```
http://localhost:8000/docs
```

---

## Known Limitations

| Limitation | Root Cause | Status |
|------------|------------|--------|
| No order line items | `SalesLineV2` not yet integrated | Planned |
| 2-3 minute response time | `qwen3:8b` on VHD CPU | By design for local POC |
| Form freezes during call | X++ `HttpClient` blocks AOS thread | By design — no threading in X++ forms |
| AOS hibernation | VHD AOS sleeps after inactivity | Workaround: wake AOS before each session |
| Regex covers US-XXX/DE-XXX only | Limited customer format patterns | Planned extension |
| No Azure AD token caching | New token fetched per OData call | Planned optimization |

---

## Roadmap

### Short Term
- [ ] Add `SalesLineV2` OData entity for order line item queries
- [ ] Cache Azure AD token to reduce latency per call
- [ ] Extend customer regex to cover more account number formats
- [ ] Add retry logic for AOS timeout scenarios

### Phase 2
- [ ] Add **Ask about this order** button on the Sales Order list form
- [ ] Add inventory availability context (`InventOnhandV2` entity)
- [ ] Conversation history — remember questions within the same session
- [ ] Export AI answer to email or D365 note
- [ ] Run Python server as Windows Service for auto-start
- [ ] Replace `qwen3:8b` with faster model or GPU-backed inference for production

---

## Quick Reference Commands

| Action | Command |
|--------|---------|
| Start Python server | `cd python && .venv\Scripts\activate.bat && uvicorn server:app --host 0.0.0.0 --port 8000 --reload` |
| Check server health | `http://localhost:8000/health` |
| Test OData connection | `http://localhost:8000/test-odata` |
| Open AI Assistant form | `https://usnconeboxax1aos.cloud.onebox.dynamics.com/?mi=SalesAIAssistant` |
| Check Ollama running | `ollama list` |
| Run data export job | Set `AIAssistantDataDump` as Startup Object in VS → Ctrl+F5 |
| View exported data | Open `D365_AI_Data.txt` in Notepad |
| API documentation | `http://localhost:8000/docs` |

---

## Author

**Omar Hesham Shehab**
GitHub: [@OmarHeshamShehab](https://github.com/OmarHeshamShehab)

---

*D365 Sales AI Assistant — Proof of Concept — February 2026*
