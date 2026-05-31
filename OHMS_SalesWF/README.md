# OHMS_SalesWF — Custom Approval Workflow on the Sales Order (SalesTable)

A Dynamics 365 Finance & Operations (X++) solution that adds a **custom, header‑level approval workflow** to the standard **Sales order** document (`SalesTable`). It surfaces a **Submit** button on the *Sales order details* form, routes the order for approval, and tracks the order's progress through a custom workflow‑status field — all implemented through **extensions and event handlers only**, without over‑layering any standard object.

---

## 1. Overview

| | |
|---|---|
| **Solution / project** | `OHMS_SalesWF` |
| **Model** | `OHMS` (Layer: USR) |
| **Target document** | `SalesTable` (Sales order) |
| **Target form** | `SalesTable` / *Sales order details* (`SalesTableDetails`) |
| **Workflow scope** | Header‑level (one workflow instance per sales order) |
| **Configuration module** | Accounts receivable (`ModuleAxapta::Customer`) |
| **Over‑layering** | None — all standard‑object behavior is achieved via Chain‑of‑Command / event handlers |

The workflow lets a user submit a sales order for approval. On submission the order moves to a *Submit/Started* state; an approver can **Approve, Reject, Request change, Delegate, or Resubmit**; and each outcome is written back to a custom status field on the order.

---

## 2. Solution architecture

```
OHMS_SalesWF
├── Base Enums
│   └── OHMSSalesWFStatus ............ Workflow status values (Draft, Submit, Started, …)
├── Table Extensions
│   └── SalesTable.OHMS .............. Adds the OHMSSalesWFStatus field to SalesTable
├── Simple Queries
│   └── OHMSSalesWFQuery ............. Document query over SalesTable (Dynamic Fields = Yes)
├── Workflow Categories
│   └── OHMSSalesWFCategory .......... Links the workflow to the module (Customer)
├── Workflow Types
│   └── OHMSSalesWFType .............. The workflow type/template
├── Workflow Approvals
│   └── OHMSSalesWFApproval .......... The approval element referenced by the type
├── Action Menu Items
│   ├── OHMSSalesWFTypeSubmitMenuItem ............ Submit
│   ├── OHMSSalesWFTypeCancelMenuItem ............ Cancel
│   ├── OHMSSalesWFApprovalApprove ............... Approve
│   ├── OHMSSalesWFApprovalReject ................ Reject
│   ├── OHMSSalesWFApprovalRequestChange ......... Request change
│   ├── OHMSSalesWFApprovalDelegateMenuItem ...... Delegate
│   └── OHMSSalesWFApprovalResubmitMenuItem ...... Resubmit
└── Classes
    ├── OHMSSalesWFTypeDocument ................. Workflow document class
    ├── OHMSSalesWFTypeSubmitManager ............ Activates the workflow on Submit
    ├── OHMSSalesWFTypeEventHandler ............. Type‑level events (started/canceled/completed)
    ├── OHMSSalesWFApprovalEventHandler ......... Approval‑element outcome events
    ├── OHMSSalesWFApprovalResubmitActionMgr .... Resubmit action manager (wizard‑generated)
    ├── OHMSSalesWFStatusHelper ................. Centralized status‑update helper
    └── OHMSSalesTableWorkflowEventHandler ...... Enables the button on the standard form
```

---

## 3. Components in detail

### 3.1 Status enum — `OHMSSalesWFStatus`
A base enum representing the order's position in the workflow:

`Draft` (index 0), `Submit`, `Started`, `Cancelled`, `Complete`, `Denied`, `ChangeRequested`, `Returned`.

`Draft` is intentionally placed at index 0 so that every existing and newly created sales order defaults to **Draft** — which is the only state from which the workflow may be submitted.

### 3.2 Table extension — `SalesTable.OHMS`
Adds the field **`OHMSSalesWFStatus`** (of the enum above) to `SalesTable`. The field is set to **AllowEdit = No** / **AllowEditOnCreate = No** because it is maintained exclusively by workflow code, never by the user.

### 3.3 Query — `OHMSSalesWFQuery`
A query with a single `SalesTable` data source and **Dynamic Fields = Yes**. It exposes the document's fields to the workflow framework for conditions and the document class.

### 3.4 Workflow category — `OHMSSalesWFCategory`
Links the workflow type to the module in which it can be configured. **Module = `Customer`** (see §6 for why this matters).

### 3.5 Workflow type — `OHMSSalesWFType`
The workflow template. Key properties:

* **Category:** `OHMSSalesWFCategory`
* **Query:** `OHMSSalesWFQuery`
* **Document:** `OHMSSalesWFTypeDocument`
* **Document menu item:** `SalesTableDetails`
* **Started / Canceled / Completed event handler:** `OHMSSalesWFTypeEventHandler`
* **Submit / Cancel menu items:** the corresponding action menu items
* **Supported Elements:** references `OHMSSalesWFApproval`

### 3.6 Workflow document — `OHMSSalesWFTypeDocument`
Extends `WorkflowDocument` and returns the query name:

```xpp
public queryName getQueryName()
{
    return querystr(OHMSSalesWFQuery);
}
```

### 3.7 Submit manager — `OHMSSalesWFTypeSubmitManager`
Invoked by the **Submit** action menu item. It opens the submission dialog, activates the workflow for the active record via `Workflow::activateFromWorkflowType(...)`, stamps the order to `Submit`, and refreshes the form's workflow controls.

### 3.8 Type‑level event handler — `OHMSSalesWFTypeEventHandler`
Implements `WorkflowStartedEventHandler`, `WorkflowCanceledEventHandler`, `WorkflowCompletedEventHandler`. On each event it calls the status helper to set `Started`, `Cancelled`, or `Complete`.

### 3.9 Approval element — `OHMSSalesWFApproval`
The approval that users configure between **Start** and **End** in the workflow editor. It defines the **Approve / Reject / Request change / Delegate / Resubmit** outcomes and a document‑preview field group (`OHMSWorkflow`, defined on the `SalesTable` extension).

### 3.10 Approval event handler — `OHMSSalesWFApprovalEventHandler`
Implements the element‑level outcome interfaces and writes the matching status for each event: `started → Started`, `canceled → Cancelled`, `completed → Complete`, `denied → Denied`, `changeRequested → ChangeRequested`, `returned → Returned`. The `created` event performs no status change.

### 3.11 Status helper — `OHMSSalesWFStatusHelper`
A single static method `updateWorkflowStatus(RefRecId, OHMSSalesWFStatus)` that locks the target `SalesTable` record by `RecId` and writes the status inside a transaction. Centralizing this keeps every caller (submit manager, both event handlers) consistent and makes the status logic easy to maintain.

### 3.12 Form enablement handler — `OHMSSalesTableWorkflowEventHandler`
This is the class that makes the **Submit** button appear on the standard *Sales order details* form **without over‑layering it**. It contains three post‑event handlers:

1. **`FormDataUtil.canSubmitToWorkflow`** — marks a `SalesTable` record as submittable only while its status is `Draft`. (`canSubmitToWorkflow` on the table is reached through `FormDataUtil`, which can be extended cleanly.)
2. **`SalesTableInteraction.enableHeaderActions`** — at runtime, points the form's workflow design (both build and runtime design) at `OHMSSalesWFType` with datasource `SalesTable`, then calls `updateWorkflowControls()`.
3. **`SalesTable` form `canSubmitToWorkflow`** — sets the submittable return value and forces the `WorkflowActionBarButtonGroup` control visible.

> **Technique reference:** *Extend `canSubmitToWorkflow` in standard & base tables without over‑layering* — https://axraja.blogspot.com/2020/03/d365ax7-extend-cansubmittoworkflow-in.html

> **Note on the standard form:** the *Sales order details* form is bound by Microsoft to a line‑level Retail workflow (`SalesLine` / `RetailSalesLineWFType`). Handler #2 overrides this binding **at runtime** to the header‑level `OHMSSalesWFType`. This is an intentional override (not coexistence) — both target the same workflow button group, and at runtime this solution's type wins. No standard form metadata is modified.

---

## 4. Process flow

```
User opens Sales order (status = Draft)
        │
        ▼
Clicks Submit ──► OHMSSalesWFTypeSubmitManager.main()
        │            • opens submit dialog
        │            • Workflow::activateFromWorkflowType(OHMSSalesWFType, RecId)
        │            • status → Submit
        ▼
Workflow starts ──► OHMSSalesWFTypeEventHandler.started()  → status = Started
        │
        ▼
Approval step (OHMSSalesWFApproval) assigned to approver
        │
        ├─ Approve  ──► completed()        → status = Complete
        ├─ Reject   ──► denied()           → status = Denied
        ├─ Request  ──► changeRequested()  → status = ChangeRequested
        └─ Return   ──► returned()         → status = Returned
```

---

## 5. Deployment & configuration

### Build
1. Build the **OHMS** model with **Synchronize Database** enabled.
2. Confirm the build completes with **0 errors**.

### Configure the workflow (one‑time, per environment)
1. Go to **Accounts receivable → Setup → Accounts receivable workflows**.
2. Select **New**, choose **Sales order workflow** (`OHMSSalesWFType`), and open the editor (use **Microsoft Edge**).
3. Drag the **OHMSSalesWFApproval** element between **Start** and **End** and connect **Start → Approval → End**.
4. Configure the approval **Step 1**: set **Assignment type = User** (assign a user), and provide a **work‑item subject** and **work‑item instructions**.
5. Provide the workflow's **submission instructions** at the top level.
6. **Save and close → enter version notes → Activate** the version.
7. Confirm the workflow shows an **Active version** in the list.

### Result
A **Submit** button appears on the *Sales order details* form for any order in **Draft** status. Submitting routes the order to the configured approver and drives the `OHMSSalesWFStatus` field through its lifecycle.

---

## 6. Key lesson learned — `Customer` vs `AccountsReceivable`

The single most important gotcha in this build:

> A workflow type only appears in a module's **workflow configuration** list when its **category's `ModuleAxapta` value** exactly matches the value that module's workflow list page filters on.

The `ModuleAxapta` enum contains both an `AccountsReceivable` element **and** a `Customer` element. Although the UI page is labelled *“Accounts receivable workflows,”* the page actually filters on **`Customer`** — this is the value the standard customer document workflows (e.g. `CustFreeTextInvoiceTemplate` → category `CustCategory`) use. Setting the category module to the intuitively‑named `AccountsReceivable` registers the type correctly but it **never surfaces**, because no list page is bound to that enum value.

**Rule of thumb:** don't pick the `ModuleAxapta` element by its friendly name — pick the value a *working standard workflow in the same module* uses. Here that value is **`Customer`**.

A second, related operational note: D365 caches the workflow type lookup **per user**. After assigning/changing a category's module, run **System administration → Users → (your user) → Reset usage data** and hard‑refresh; a server restart alone does **not** clear this cache.

---

## 7. Design decisions

* **No over‑layering.** Every interaction with standard objects (`SalesTable`, the form, `FormDataUtil`, `SalesTableInteraction`) is done through extensions / post‑event handlers, keeping the solution upgrade‑safe.
* **Custom status field rather than `VersioningDocumentState`.** A dedicated `OHMSSalesWFStatus` enum makes the workflow's states explicit and independent of standard change‑management states.
* **Centralized status updates.** All status writes go through `OHMSSalesWFStatusHelper`, so behavior is consistent and changes are made in one place.
* **Header‑level workflow.** The query and document use `SalesTable` only (no `SalesLine`), matching a one‑instance‑per‑order design.

---

## 8. Naming reference

| Element | Name |
|---|---|
| Solution / project | `OHMS_SalesWF` |
| Status enum | `OHMSSalesWFStatus` |
| Table extension | `SalesTable.OHMS` |
| Query | `OHMSSalesWFQuery` |
| Category | `OHMSSalesWFCategory` |
| Workflow type | `OHMSSalesWFType` |
| Workflow approval | `OHMSSalesWFApproval` |
| Document class | `OHMSSalesWFTypeDocument` |
| Submit manager | `OHMSSalesWFTypeSubmitManager` |
| Type event handler | `OHMSSalesWFTypeEventHandler` |
| Approval event handler | `OHMSSalesWFApprovalEventHandler` |
| Status helper | `OHMSSalesWFStatusHelper` |
| Form enablement handler | `OHMSSalesTableWorkflowEventHandler` |

---

*Solution authored in the `OHMS` model (USR layer) for Dynamics 365 Finance & Operations.*
