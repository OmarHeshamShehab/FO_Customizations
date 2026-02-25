# D365 Sales AI Assistant

> An AI-powered sales order assistant embedded natively inside Microsoft Dynamics 365 Finance & Operations. Ask natural language questions about sales orders, customers, and backorders — and get instant, accurate answers from live D365 data.

---

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [How It Works](#how-it-works)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
  - [Step 1 — Python Environment](#step-1--python-environment)
  - [Step 2 — Ollama and LLM Model](#step-2--ollama-and-llm-model)
  - [Step 3 — Configuration](#step-3--configuration)
  - [Step 4 — X++ Deployment](#step-4--x-deployment)
- [Configuration Reference](#configuration-reference)
- [Running the Server](#running-the-server)
- [API Endpoints](#api-endpoints)
- [X++ Components](#x-components)
- [Usage Guide](#usage-guide)
- [Validation Results](#validation-results)
- [Known Limitations](#known-limitations)
- [Troubleshooting](#troubleshooting)
- [Comparison with Microsoft Copilot](#comparison-with-microsoft-copilot)
- [Roadmap](#roadmap)

---

## Overview

The D365 Sales AI Assistant is a proof-of-concept that demonstrates AI-powered natural language querying of Microsoft Dynamics 365 Finance & Operations sales data. It is built entirely inside the D365 VHD environment with no external cloud AI dependencies.

### What It Does

- Answers natural language questions about sales orders in plain English
- Fetches live data directly from D365 OData — no CSV exports or data copies
- Detects intent automatically — extracts order numbers and customer IDs from free text
- Runs 100% locally on the VHD using the Ollama LLM engine
- Appears as a native F&O form accessible from the Accounts Receivable menu

### Example Questions

```
"What is the status of order 000697?"
"Show me all orders for customer US-001"
"How many backorders are there in the system?"
"Order 000697 is stuck, what can you tell me about it?"
"What are the most recent orders in the system?"
```

### Key Design Decisions

| Decision | Choice | Reason |
|----------|--------|--------|
| AI Model | qwen3:8b via Ollama | Runs locally, no API costs, no data leaves the VHD |
| Data Source | Live OData API | Always current, no stale CSV exports |
| Auth Method | Azure AD client credentials | Same as Postman, secure, no user credentials stored |
| X++ Integration | System.Net.Http direct HTTP | No custom service needed, simple and reliable |
| Response Format | Plain text /ask-text endpoint | Avoids X++ str 256-char JSON parsing limitation |

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    D365 VHD Environment                      │
│                                                             │
│  ┌──────────────────┐        ┌────────────────────────────┐ │
│  │   F&O Browser    │        │    Python FastAPI Server   │ │
│  │                  │        │    localhost:8000           │ │
│  │  SalesAIAssistant│        │                            │ │
│  │  Form (X++)      │──HTTP──│  server.py    (routing)    │ │
│  │                  │  POST  │  ai_engine.py (AI logic)   │ │
│  │  SalesAIAssistant│ /ask   │  odata.py     (D365 data)  │ │
│  │  Service (X++)   │ -text  │  config.py    (settings)   │ │
│  └──────────────────┘        └──────────┬─────────────────┘ │
│                                         │                   │
│                              ┌──────────▼─────────────────┐ │
│                              │   Ollama LLM Engine        │ │
│                              │   localhost:11434          │ │
│                              │   Model: qwen3:8b          │ │
│                              └────────────────────────────┘ │
│                                         │                   │
│                              ┌──────────▼─────────────────┐ │
│                              │   D365 F&O OData API       │ │
│                              │   usnconeboxax1aos...       │ │
│                              │   /data/SalesOrderHeadersV2│ │
│                              └────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### Data Flow

```
User types question in F&O form
        │
        ▼
X++ SalesAIAssistantService.askQuestion()
        │  POST /ask-text
        ▼
Python server.py — routes request
        │
        ▼
ai_engine.detect_intent()
  → Extracts order numbers via regex (\b0+\d{3,6}\b)
  → Extracts customer IDs via regex (\b(us-\d{3}|de-\d{3})\b)
  → Detects question type (order/customer/backorder/recent)
        │
        ▼
ai_engine.fetch_context()
  → Calls odata.fetch_odata() for each required entity
  → odata.get_token() acquires Azure AD Bearer token
  → D365 OData returns live JSON data
  → Backorders filtered in Python (OData enum limitation)
        │
        ▼
ai_engine.build_prompt()
  → Formats D365 data into structured text
  → Combines with system instructions and user question
        │
        ▼
ai_engine.call_ollama()
  → POST to localhost:11434/api/chat
  → qwen3:8b generates plain English answer
  → think=False for faster responses
        │
        ▼
Plain text answer returned to X++ form
        │
        ▼
AnswerDisplay control shows answer to user
```

---

## How It Works

### Intent Detection

The system extracts context from natural language using regex patterns:

| Pattern | Example Match | Purpose |
|---------|---------------|---------|
| `\b0+\d{3,6}\b` | `000697` | Sales order number |
| `\b(us-\d{3}\|de-\d{3})\b` | `US-001`, `DE-013` | Customer account |
| Keywords | `backorder`, `stuck`, `delayed` | Backorder query |
| Keywords | `recent`, `latest`, `how many` | Summary query |

### OData Enum Limitation

D365 F&O OData does not support filtering by `SalesOrderStatus` enum values directly in the URL. This is a known platform limitation. The workaround:

```python
# Cannot do this in OData URL:
# $filter=SalesOrderStatus eq 'Backorder'  ← Does not work

# Must do this instead:
all_orders = fetch_odata("SalesOrderHeadersV2", top=5000)
backorders = [o for o in all_orders if o.get("SalesOrderStatus") == "Backorder"]
```

### X++ String Limitation

X++ `str` type has a 256-character limit which causes JSON truncation. Solution: a dedicated `/ask-text` endpoint that returns plain text instead of JSON, bypassing the need for JSON parsing in X++ entirely.

---

## Project Structure

```
D365AI/
├── .env                          # Environment variables (credentials, URLs)
├── .venv/                        # Python virtual environment
│
└── python/
    ├── config.py                 # Loads .env settings into Python variables
    ├── server.py                 # FastAPI app, endpoints, request/response models
    ├── ai_engine.py              # Intent detection, context fetching, Ollama calls
    ├── odata.py                  # Azure AD auth, OData fetch logic
    └── debug.py                  # Debug/test script (development only)

X++ Objects (in Visual Studio — Model: OHMS):
    ├── SalesAIAssistantParameters    (Table)        — API config storage
    ├── SalesAIAssistantService       (Class)        — HTTP client to Python API
    ├── SalesAIAssistant              (Form)         — Chat interface in F&O
    ├── SalesAIAssistant              (Display Menu Item) — Navigation item
    └── AccountsReceivable.Extension  (Menu Extension)   — AR menu integration
```

---

## Prerequisites

### VHD Requirements

| Component | Version | Purpose |
|-----------|---------|---------|
| Windows Server | 2019 (20348+) | VHD operating system |
| D365 F&O | Any recent release | Target ERP system |
| Python | 3.14+ | Backend server runtime |
| Ollama | 0.17.0+ | Local LLM engine |
| Visual Studio | 2019+ with F&O tools | X++ development |

### Azure AD App Registration

An Azure AD app registration is required with:
- Grant type: `client_credentials`
- Permission: Access to D365 F&O as the application
- Resource: `https://usnconeboxax1aos.cloud.onebox.dynamics.com/`

### Python Packages

```
fastapi
uvicorn
httpx
requests
pydantic
python-dotenv
python-multipart
```

> **Note:** Do not pin package versions when using Python 3.14 — pip will select compatible versions automatically.

---

## Installation

### Step 1 — Python Environment

Open Command Prompt on the VHD and run:

```cmd
cd C:\Users\localadmin\Desktop\D365AI

:: Create virtual environment
python -m venv .venv

:: Activate virtual environment
.venv\Scripts\activate.bat

:: Install dependencies
cd python
pip install fastapi uvicorn httpx requests pydantic python-dotenv python-multipart --break-system-packages
```

Verify installation:

```cmd
python -c "import fastapi; print('FastAPI OK')"
python -c "import requests; print('Requests OK')"
```

### Step 2 — Ollama and LLM Model

```cmd
:: Pull the qwen3:8b model (5.2 GB download — do once)
ollama pull qwen3:8b

:: Verify model is available
ollama list

:: Test model responds
ollama run qwen3:8b "What is a sales backorder?"
```

### Step 3 — Configuration

Create `.env` file at `C:\Users\localadmin\Desktop\D365AI\python\.env`:

```env
# D365 F&O OData Configuration
ODATA_BASE_URL=https://usnconeboxax1aos.cloud.onebox.dynamics.com/data
COMPANY=usmf

# Azure AD App Registration Credentials
AAD_TENANT_ID=your-tenant-id-here
AAD_CLIENT_ID=your-client-id-here
AAD_CLIENT_SECRET=your-client-secret-here
AAD_RESOURCE=https://usnconeboxax1aos.cloud.onebox.dynamics.com/
LOGIN_URL=https://login.windows.net/

# Ollama Configuration
OLLAMA_URL=http://localhost:11434
OLLAMA_MODEL=qwen3:8b

# FastAPI Server Configuration
HOST=0.0.0.0
PORT=8000
```

> **Security:** Never commit `.env` to source control. Add it to `.gitignore`.

### Step 4 — X++ Deployment

1. Open Visual Studio on the VHD
2. Open or create a solution targeting your custom model
3. Add the following objects to your project:

**Table: SalesAIAssistantParameters**
- Fields: `APIEndpoint` (String 255), `TimeoutSeconds` (Integer), `IsEnabled` (Enum)
- Properties: `TableType = Regular`, `SaveDataPerCompany = No`, `CacheLookup = Found`
- Methods: `find()` static method with default record creation

**Class: SalesAIAssistantService**
- Paste complete class code (see [X++ Components](#x-components))

**Form: SalesAIAssistant**
- Design with InputGroup, QuestionGroup, ButtonGroup, AnswerGroup
- Lookups on CustomerIdInput and SalesOrderIdInput
- Code references service class

**Display Menu Item: SalesAIAssistant**
- Object: `SalesAIAssistant`, ObjectType: `Form`

**Menu Extension: AccountsReceivable.Extension**
- Adds menu item to Accounts Receivable → Orders

4. Build the project (`Ctrl+Shift+B`)
5. Synchronize the database (right-click project → Synchronize)

---

## Configuration Reference

### SalesAIAssistantParameters Table

The parameters table stores runtime configuration and is accessible via:

```
Accounts Receivable → Setup → AI Assistant Parameters
```

| Field | Default | Description |
|-------|---------|-------------|
| APIEndpoint | `http://localhost:8000` | Python FastAPI server URL |
| TimeoutSeconds | `90` | HTTP request timeout in seconds |
| IsEnabled | `Yes` | Enable/disable the assistant |

The `find()` method auto-creates a default record on first access:

```xpp
SalesAIAssistantParameters params = SalesAIAssistantParameters::find();
str endpoint = params.APIEndpoint; // http://localhost:8000
```

### .env File Reference

| Variable | Example | Description |
|----------|---------|-------------|
| `ODATA_BASE_URL` | `https://...dynamics.com/data` | F&O OData base URL |
| `COMPANY` | `usmf` | D365 company/legal entity code |
| `AAD_TENANT_ID` | `864324a0-...` | Azure AD tenant ID |
| `AAD_CLIENT_ID` | `0ad32f81-...` | App registration client ID |
| `AAD_CLIENT_SECRET` | `_xf8Q~...` | App registration client secret |
| `AAD_RESOURCE` | `https://...dynamics.com/` | F&O resource URL (trailing slash required) |
| `LOGIN_URL` | `https://login.windows.net/` | Azure AD token endpoint base |
| `OLLAMA_URL` | `http://localhost:11434` | Ollama server URL |
| `OLLAMA_MODEL` | `qwen3:8b` | Ollama model name |

---

## Running the Server

### Start the Server

```cmd
:: Navigate to python folder
cd C:\Users\localadmin\Desktop\D365AI\python

:: Activate virtual environment
c:\Users\localadmin\Desktop\D365AI\.venv\Scripts\activate.bat

:: Start FastAPI server with auto-reload
uvicorn server:app --host 0.0.0.0 --port 8000 --reload
```

Expected output:

```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete.
```

### Verify Server is Running

Open browser and navigate to:

```
http://localhost:8000/health
```

Expected response:

```json
{
  "status": "ok",
  "model": "qwen3:8b",
  "company": "usmf"
}
```

### Keep Server Running

The server must stay running while using the F&O form. Do not close the CMD window. For production deployments consider running as a Windows Service.

---

## API Endpoints

### GET /health

Health check endpoint. Returns server status and configuration.

**Response:**
```json
{
  "status": "ok",
  "model": "qwen3:8b",
  "company": "usmf"
}
```

---

### GET /test-odata

Tests D365 OData connectivity. Returns 3 sample sales orders.

**Response (connected):**
```json
{
  "connected": true,
  "sample": [
    {
      "SalesOrderNumber": "000697",
      "SalesOrderStatus": "Backorder",
      "OrderingCustomerAccountNumber": "DE-001"
    }
  ]
}
```

**Response (not connected):**
```json
{
  "connected": false,
  "sample": []
}
```

> If not connected: open F&O browser and navigate to All Sales Orders to wake the AOS, then retry.

---

### POST /ask

Main AI endpoint. Returns full JSON response with answer and metadata.

**Request body:**
```json
{
  "question": "What is the status of order 000697?",
  "sales_order_id": "000697",
  "customer_id": ""
}
```

**Response:**
```json
{
  "answer": "The status of order 000697 is Backorder.",
  "question": "What is the status of order 000697?",
  "data_used": {
    "intent": {
      "sales_order_id": "000697",
      "customer_id": "",
      "fetch_order": true,
      "fetch_customer": false,
      "fetch_backorders": false,
      "fetch_recent": false
    },
    "order_found": true,
    "backorders": 0,
    "customer_orders": 0
  }
}
```

---

### POST /ask-text

Same as `/ask` but returns plain text only. Used by X++ to avoid JSON parsing.

**Request body:** Same as `/ask`

**Response:** `text/plain`
```
The status of order 000697 is Backorder.
```

---

## X++ Components

### SalesAIAssistantParameters (Table)

Stores API configuration. Auto-initializes with defaults on first access.

```xpp
// Retrieve parameters
SalesAIAssistantParameters params = SalesAIAssistantParameters::find();
str endpoint = params.APIEndpoint;      // http://localhost:8000
int timeout  = params.TimeoutSeconds;   // 90
```

---

### SalesAIAssistantService (Class)

Bridge between F&O X++ and the Python FastAPI backend.

**Public Methods:**

```xpp
// Initialize service (loads parameters)
SalesAIAssistantService aiService = new SalesAIAssistantService();

// Check if Python server is running
boolean available = aiService.isServiceAvailable();

// Ask a question — returns plain text answer
str answer = aiService.askQuestion(
    "What is the status of order 000697?",  // question
    "000697",                                // optional order ID
    ""                                       // optional customer ID
);
```

---

### SalesAIAssistant (Form)

Native F&O chat interface for the AI assistant.

**Controls:**

| Control | Type | Purpose |
|---------|------|---------|
| CustomerIdInput | String with lookup | Customer account picker (CustTable lookup) |
| SalesOrderIdInput | String with lookup | Sales order picker (SalesTable lookup, filtered by customer) |
| QuestionInput | String (multiline) | Natural language question input |
| AskButton | Button | Submits question to AI assistant |
| AnswerDisplay | String (multiline, readonly) | Displays AI-generated answer |

**Lookup Behavior:**
- CustomerIdInput shows all customers from CustTable sorted by AccountNum
- SalesOrderIdInput shows orders from SalesTable sorted newest first
- If a customer is selected, SalesOrderIdInput automatically filters to show only that customer's orders

**Access the form:**
```
Accounts Receivable → Orders → AI Sales Assistant
```

Or directly via URL:
```
https://usnconeboxax1aos.cloud.onebox.dynamics.com/?mi=SalesAIAssistant
```

---

## Usage Guide

### Daily Startup Procedure

Every time you start a new session:

1. **Start Ollama** (if not already running as a service):
   ```cmd
   ollama serve
   ```

2. **Start the Python server:**
   ```cmd
   cd C:\Users\localadmin\Desktop\D365AI\python
   .venv\Scripts\activate.bat
   uvicorn server:app --host 0.0.0.0 --port 8000 --reload
   ```

3. **Wake up the AOS** — open F&O browser and navigate to:
   ```
   Accounts Receivable → Orders → All Sales Orders
   ```
   Wait for the page to fully load before using the assistant.

4. **Open the AI Assistant:**
   ```
   Accounts Receivable → Orders → AI Sales Assistant
   ```

### Asking Questions

**Method 1 — Natural language only (no context fields)**

Leave Customer Account and Sales Order ID empty. Type your question naturally:

```
Order 000697 is stuck, what can you tell me about it?
What are all the backorders in the system?
What are the most recent orders?
```

The system will automatically extract order numbers and customer IDs from your question.

**Method 2 — With context fields**

Select a customer from the Customer Account lookup, optionally select a specific order from the Sales Order ID lookup, then type your question:

```
Customer Account: US-001
Question: What is the payment terms for this customer and how many orders do they have?
```

**Method 3 — Order-specific with context**

```
Customer Account: DE-001
Sales Order ID:   000697
Question:         Why is this order stuck?
```

### Question Types and Examples

| Question Type | Example | Data Fetched |
|--------------|---------|--------------|
| Specific order | "What is the status of order 000697?" | Single order record |
| Customer history | "Show all orders for US-001" | Up to 50 customer orders |
| Backorder inquiry | "How many backorders are there?" | All orders filtered to Backorder status |
| Natural language | "Order 000697 is stuck" | Order + backorder context |
| Recent summary | "What are the most recent orders?" | 20 newest orders |

---

## Validation Results

The following tests were performed against USMF demo data and all passed:

| # | Question | Expected | Result |
|---|----------|----------|--------|
| 1 | "What is the status of order 000697?" | Backorder — DE-001 | ✓ Pass |
| 2 | "Show me all orders for customer US-001" | 28 orders, full breakdown | ✓ Pass |
| 3 | "How many backorders are there in the system?" | 37 backorders | ✓ Pass |
| 4 | "Order 000697 is stuck, what can you tell me about it?" | Full order details extracted from natural language | ✓ Pass |
| 5 | "What are the most recent orders in the system?" | Orders 000936 and 000935 — February 2026 | ✓ Pass |

**Pass rate: 5/5 — 100%**

### Sample Answer Quality

**Test 4 — Natural language with cross-context reasoning:**
> *"Order 000697 is a backordered sales order for customer DE-001 - Contoso Europe. It was created on December 7 2016, and the requested and confirmed ship date is December 30 2016. The order is currently in a backorder status, and the processing is confirmed. The currency is USD, and the payment terms are Net10. The delivery mode is 40, and the delivery terms are FOB. The order was originated from a phone call and is shipped to Contoso Europe. This order is one of two backorders for customer DE-001."*

---

## Known Limitations

### AOS Sleep Issue

The D365 VHD AOS service goes to sleep after inactivity. When the AOS is sleeping, OData calls time out causing the assistant to return "order not found" answers.

**Workaround:** Always open All Sales Orders in the F&O browser before using the assistant. This wakes the AOS and keeps it active.

**Detection:** Check the Python server CMD window. If you see:
```
OData error: HTTPSConnectionPool: Read timed out.
```
The AOS needs to be woken up.

---

### Backorder Fetch Performance

Backorder queries fetch up to 5,000 records from OData and filter in Python. This is necessary because D365 OData does not support enum value filtering for `SalesOrderStatus` in the URL.

**Impact:** Backorder queries take 30-60 seconds on a cold AOS. After the AOS warms up subsequent queries are faster.

---

### Customer/Order Regex Coverage

The intent detection regex currently covers:
- Customer accounts in format `US-XXX` and `DE-XXX`
- Order numbers in format `000XXX` (leading zeros)

Customer accounts in other formats (e.g. `CUST-001`, `10001`) will not be auto-extracted from natural language. Users should use the Customer Account lookup field instead.

---

### Single Company Scope

The current implementation only queries the company configured in `.env` (`COMPANY=usmf`). Multi-company support would require extending the intent detection and OData fetch logic.

---

### X++ String Display

Long AI responses may be truncated in the AnswerDisplay field if they exceed the control's visible area. Use the scrollbar to see the full answer. The underlying `str` type in X++ handles long strings correctly — only the visible display area is limited by the control height.

---

## Troubleshooting

### Server Will Not Start

**Symptom:** `uvicorn server:app` fails immediately

**Check:**
```cmd
python -c "from server import app; print(len(app.routes))"
```
Should print `7`. If it prints `4`, there is an import error.

**Fix:**
```cmd
python -c "import traceback; exec(open('server.py').read())"
```
This will show the exact import error.

---

### OData Returns Empty

**Symptom:** `/test-odata` returns `{"connected": false, "sample": []}`

**Causes and fixes:**

| Cause | Fix |
|-------|-----|
| AOS is sleeping | Open All Sales Orders in F&O browser and wait for full load |
| Wrong credentials | Verify `AAD_CLIENT_ID` and `AAD_CLIENT_SECRET` in `.env` |
| Token error | Check Python CMD for `Token error 400` messages |
| Network timeout | Increase `timeout` in `fetch_odata()` from 120 to 180 |

---

### AI Returns "Order Not Found"

**Symptom:** You ask about a known order but get "not found"

**Causes:**
1. AOS timed out during the OData call — wake AOS and retry
2. Order number format mismatch — try entering the order in the Sales Order ID field directly instead of typing it in the question

---

### Form Shows "AI Service Not Reachable"

**Symptom:** AnswerDisplay shows service unreachable message on form load

**Fix:**
1. Make sure Python server is running (`uvicorn server:app --port 8000 --reload`)
2. Check `http://localhost:8000/health` in browser
3. Verify `APIEndpoint` in SalesAIAssistantParameters table is `http://localhost:8000`

---

### Ollama Not Responding

**Symptom:** Python server logs show `Cannot reach Ollama`

**Fix:**
```cmd
:: Check if Ollama is running
ollama list

:: If not running, start it
ollama serve

:: Verify model is available
ollama run qwen3:8b "test"
```

---

### Build Errors in Visual Studio

**`client` is an invalid variable name**
Rename all `client` variables to `httpClient` — `client` is a reserved X++ keyword.

**`Variable not found in scope`**
Form controls must be retrieved via `element.design().controlName()` — they cannot be referenced directly by name in form-level code.

**`Table does not contain field`**
Use the correct field name. For CustTable customer account the field is `AccountNum` not `Name` or `CustName`.

---

## Comparison with Microsoft Copilot

| Feature | D365 Sales AI Assistant | Microsoft Copilot for F&O |
|---------|------------------------|--------------------------|
| Natural language queries | ✓ | ✓ |
| Live D365 data | ✓ | ✓ |
| Cross-record reasoning | ✓ Advanced | ✗ Limited |
| Custom field support | ✓ Fully extensible | ✗ Standard fields only |
| Cost per user/month | $0 (local Ollama) | ~$30 USD |
| Custom terminology | ✓ Prompt configurable | ✗ Fixed |
| Data stays on-premise | ✓ 100% local | ✗ Sent to Microsoft cloud |
| Setup complexity | Medium | Low |
| Polish and UI | Basic (POC) | Enterprise grade |
| Multi-module context | Roadmap | ✓ |

**Bottom line:** Copilot is a general-purpose assistant for average Microsoft users. This assistant is a specialized sales operations tool that can be trained to know your specific business, data, and terminology — things Copilot will never do because Microsoft builds for everyone, not for your specific business.

---

## Roadmap

### Phase 2 — Richer Context
- [ ] Add sales order line items (SalesLineV2 entity)
- [ ] Add inventory availability (InventOnhandV2 entity)
- [ ] Add customer credit and payment history
- [ ] Extend customer regex to cover more account number formats

### Phase 3 — Better UX
- [ ] Add "Ask about this order" button directly on the Sales Order form
- [ ] Token caching to avoid re-authentication on every OData call
- [ ] Conversation history — remember previous questions in the same session
- [ ] Export answer to email or note

### Phase 4 — Production Readiness
- [ ] Run Python server as Windows Service (auto-start on VHD boot)
- [ ] Replace local Ollama with Azure OpenAI for better answer quality
- [ ] Multi-company support
- [ ] Role-based access control — restrict to sales users only
- [ ] Answer logging table in D365 for audit trail
- [ ] Unit tests for intent detection and context fetching

### Phase 5 — Cross-Module Intelligence
- [ ] Purchase order context for supply chain questions
- [ ] Accounts receivable aging for credit questions
- [ ] Warehouse management for shipment status
- [ ] True "why is this order stuck" cross-module reasoning

---

## Technology Stack

| Layer | Technology | Version |
|-------|-----------|---------|
| ERP Platform | Microsoft Dynamics 365 F&O | Cloud/VHD |
| X++ Runtime | AOS (Application Object Server) | D365 |
| Backend Language | Python | 3.14+ |
| Web Framework | FastAPI | Latest |
| ASGI Server | Uvicorn | Latest |
| HTTP Client (Python) | requests + httpx | Latest |
| HTTP Client (X++) | System.Net.Http | .NET |
| LLM Engine | Ollama | 0.17.0+ |
| LLM Model | qwen3:8b | 5.2 GB |
| Auth Protocol | OAuth2 client credentials | Azure AD |
| Data Protocol | OData v4 | D365 standard |
| Config Management | python-dotenv | Latest |
| Data Validation | Pydantic v2 | Latest |

---

## License

This project is a proof of concept developed for educational and demonstration purposes.

---

## Author

Built as a D365 F&O AI integration POC — demonstrating that enterprise-grade AI assistance can be embedded natively inside Microsoft Dynamics 365 without cloud AI dependencies or per-user licensing costs.

---

*Last updated: February 2026*
*Environment: D365 F&O VHD — USMF demo data*
*Model: OHMS*
