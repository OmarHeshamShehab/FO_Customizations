# Customer Account Statement Report — Extension (D365 F&O)

A working extension of the standard **Customer Account Statement** SSRS report in Dynamics 365 Finance & Operations. This project adds a new column (`MaxTxT`) to the report that displays the **customer group name** for each transaction row, demonstrating the complete pattern for extending standard SSRS reports without modifying any standard objects.

---

## Table of Contents

1. [Overview](#overview)
2. [Project Structure](#project-structure)
3. [How It Works (End-to-End Flow)](#how-it-works-end-to-end-flow)
4. [Build Steps](#build-steps)
5. [Final Class Code](#final-class-code)
6. [Issues Encountered & Resolutions](#issues-encountered--resolutions)
7. [Print Management Configuration](#print-management-configuration)
8. [Testing](#testing)
9. [Key Concepts](#key-concepts)

---

## Overview

**Goal:** Add a new field to the standard `CustAccountStatementExt` report that shows, for each transaction row, the **Name** of the customer group that the customer belongs to.

**Target object:** The new field, `MaxTxT`, is added to the temp table `CustAccountStatementExtTmp` via a table extension. The value is populated at runtime by an event handler.

**Approach:** All artifacts are created in a custom model (`USR / OHMS`) — no standard objects are modified. The extension uses:

- A **table extension** to add the new field
- A **duplicated SSRS report** to host the modified design
- An **extension controller class** to redirect execution to the custom report
- A **report handler class** to populate the new field at runtime
- A **delegate subscriber class** to redirect Print Management to the custom design
- A **menu item extension** to redirect navigation to the new controller

**Reference:** This project is based on the article ["Extend the standard reports in Dynamics 365 finance and operations"](https://automaly.io) (October 2019). Several elements of the original article required correction to work in current D365 F&O environments — those corrections are documented in [Issues Encountered & Resolutions](#issues-encountered--resolutions).

---

## Project Structure

```
CustomerAccountStamentReport (USR) [OHMS]
│
├── References
│
├── Classes
│   ├── MaxCustAccountStatementExtController_Ext   (extension controller)
│   ├── MaxCustAccountStatementExtHandler          (report handler — populates MaxTxT)
│   └── MaxPrintMgtDocTypeHandlersExt              (delegate subscriber)
│
├── Output Menu Item Extensions
│   └── CustAccountStatementExt.OHMS               (redirects to custom controller)
│
├── Reports
│   └── MaxCustAccountStatementExt                 (duplicated from standard, modified design)
│
└── Table Extensions
    └── CustAccountStatementExtTmp.OHMS            (adds MaxTxT field)
```

---

## How It Works (End-to-End Flow)

When a user runs the Customer Account Statement report:

1. The user navigates via the menu item → the menu item extension redirects execution to **`MaxCustAccountStatementExtController_Ext`**.
2. The controller calls `PrintMgmtDocType::getDefaultReportFormat()` for `PrintMgmtDocumentType::CustAccountStatement`.
3. The delegate `getDefaultReportFormatDelegate` is raised → **`MaxPrintMgtDocTypeHandlersExt`** subscribes to it and returns `MaxCustAccountStatementExt.Report`.
4. The standard data provider class `CustAccountStatementExtDP` runs and inserts rows into `CustAccountStatementExtTmp`.
5. **For each row inserted**, the `Inserting` event fires → **`MaxCustAccountStatementExtHandler.CustAccountStatementExtTmpInsertEvent`** runs and populates `MaxTxT` with the customer group's `Name`.
6. The custom report design (`MaxCustAccountStatementExt`) renders, including the new column bound to the `MaxTxT` field.

---

## Build Steps

### Step 1 — Create the Table Extension

1. In Application Explorer, locate `CustAccountStatementExtTmp` under `AOT → Tables`.
2. Right-click → **Create extension**.
3. Add a new field:
   - **Name:** `MaxTxT`
   - **Type:** String (EDT can be a generic description-style type)
4. Save.

### Step 2 — Duplicate the Standard Report

1. Locate `CustAccountStatementExt` under `AOT → Reports`.
2. Right-click → **Duplicate in project**.
3. Rename the duplicate to **`MaxCustAccountStatementExt`**.

### Step 3 — Restore the Dataset and Update the Design

1. In the duplicated report, expand `Datasets → CustAccountStatementExtDS`.
2. Right-click the dataset → **Restore**. This re-syncs the dataset from the temp table and exposes the new `MaxTxT` field in the field list.
3. Open the **Report** design (under Designs).
4. **Make room for the new column** by reducing the width of existing columns by approximately 1 inch in total. ⚠️ See ["Floating column" issue](#issue-3--maxtxt-rendered-on-its-own-page-floating-column) — adding a column without trimming others will overflow the page.
5. Drag the `MaxTxT` field into the freed-up space inside the main transaction tablix.
6. Save.

### Step 4 — Create the Extension Controller Class

Create a class named **`MaxCustAccountStatementExtController_Ext`** that extends `CustAccountStatementExtController`. (See [Final Class Code](#final-class-code) below.)

### Step 5 — Create the Report Handler Class

Create a class named **`MaxCustAccountStatementExtHandler`**. The class contains both documented patterns for populating data — Way 1 (Inserting event) and Way 2 (post-handler on `processReport`) — with Way 1 active and Way 2 commented out as an equivalent alternative. (See [Final Class Code](#final-class-code).)

### Step 6 — Create the Delegate Subscriber Class

Create a class named **`MaxPrintMgtDocTypeHandlersExt`** that subscribes to `PrintMgmtDocType.getDefaultReportFormatDelegate`. (See [Final Class Code](#final-class-code).)

### Step 7 — Extend the Menu Item

1. Locate the output menu item `CustAccountStatementExt` under `AOT → Menu Items → Output`.
2. Right-click → **Create extension**.
3. Set the extension's **Object** property to `MaxCustAccountStatementExtController_Ext`. ⚠️ Make sure there are no leading or trailing spaces in this value.
4. Save.

### Step 8 — Build, Sync, and Deploy

1. **Build the solution.**
2. Run a **database synchronization** (because of the table extension).
3. Right-click the report → **Deploy reports**. ⚠️ See ["Parameter panel layout" issue](#issue-2--parameter-panel-layout-deployment-error) — if deployment fails with a parameter panel error, see resolution.

### Step 9 — Configure Print Management

See [Print Management Configuration](#print-management-configuration) below.

### Step 10 — Test

See [Testing](#testing).

---

## Final Class Code

### `MaxCustAccountStatementExtController_Ext`

```xpp
/// <summary>
/// Extension controller class for the custom Customer Account Statement report.
/// 
/// Extends the standard CustAccountStatementExtController to redirect the report
/// execution to the custom report design (MaxCustAccountStatementExt).
/// </summary>
class MaxCustAccountStatementExtController_Ext extends CustAccountStatementExtController
{
    public static MaxCustAccountStatementExtController_Ext construct()
    {
        return new MaxCustAccountStatementExtController_Ext();
    }

    public static void main(Args _args)
    {
        SrsPrintMgmtFormLetterController controller = new MaxCustAccountStatementExtController_Ext();
        controller.parmReportName(PrintMgmtDocType::construct(PrintMgmtDocumentType::CustAccountStatement).getDefaultReportFormat());
        controller.parmArgs(_args);
        MaxCustAccountStatementExtController_Ext::startControllerOperation(controller, _args);
    }

    protected static void startControllerOperation(SrsPrintMgmtFormLetterController _controller, Args _args)
    {
        _controller.startOperation();
    }

    protected void outputReport()
    {
        SRSCatalogItemName  reportDesign;
        reportDesign = ssrsReportStr(MaxCustAccountStatementExt, Report);
        this.parmReportName(reportDesign);
        this.parmReportContract().parmReportName(reportDesign);
        formletterReport.parmReportRun().settingDetail().parmReportFormatName(reportDesign);
        super();
    }
}
```

### `MaxCustAccountStatementExtHandler`

```xpp
/// <summary>
/// Report handler class. Populates the custom field MaxTxT on the temp table
/// CustAccountStatementExtTmp with the customer group's Name.
///
/// The lookup chain (verified against current standard tables):
///   CustAccountStatementExtTmp.CustTable_AccountNum
///     -> CustTable.AccountNum
///     -> CustTable.CustGroup
///     -> CustGroup.CustGroup
///     -> CustGroup.Name  ==>  MaxTxT
///
/// Both documented ways are present in this class; WAY 1 is active, WAY 2 is
/// commented out as an equivalent alternative.
/// </summary>
class MaxCustAccountStatementExtHandler
{
    // =========================================================================
    // WAY 1 — TEMP TABLE INSERTING EVENT (ACTIVE)
    // Row-by-row: fires once per row as it is inserted into the temp table.
    // =========================================================================
    [DataEventHandlerAttribute(tableStr(CustAccountStatementExtTmp), DataEventType::Inserting)]
    public static void CustAccountStatementExtTmpInsertEvent(Common c, DataEventArgs e)
    {
        CustAccountStatementExtTmp  tempTable = c;
        CustTable                   custTable;
        CustGroup                   custGroup;

        select firstonly CustGroup from custTable
            where custTable.AccountNum == tempTable.CustTable_AccountNum
            join Name from custGroup
                where custGroup.CustGroup == custTable.CustGroup;

        tempTable.MaxTxT = custGroup.Name;
    }

    // =========================================================================
    // WAY 2 — DATA PROCESSING POST-HANDLER (COMMENTED — EQUIVALENT TO WAY 1)
    // Single pass: fires once after CustAccountStatementExtDP.processReport()
    // finishes populating the temp table.
    // =========================================================================
    /*
    [PostHandlerFor(classStr(CustAccountStatementExtDP), methodstr(CustAccountStatementExtDP, processReport))]
    public static void TmpTablePostHandler(XppPrePostArgs arguments)
    {
        CustAccountStatementExtDP   dpInstance = arguments.getThis() as CustAccountStatementExtDP;
        CustAccountStatementExtTmp  tmpTable   = dpInstance.getCustAccountStatementExtTmp();
        CustTable                   custTable;
        CustGroup                   custGroup;

        ttsbegin;
        while select forUpdate tmpTable
        {
            select firstonly CustGroup from custTable
                where custTable.AccountNum == tmpTable.CustTable_AccountNum
                join Name from custGroup
                    where custGroup.CustGroup == custTable.CustGroup;

            tmpTable.MaxTxT = custGroup.Name;
            tmpTable.update();
        }
        ttscommit;
    }
    */
}
```

### `MaxPrintMgtDocTypeHandlersExt`

```xpp
/// <summary>
/// Delegate subscriber class. Redirects the default report format for
/// PrintMgmtDocumentType::CustAccountStatement to the custom report design
/// MaxCustAccountStatementExt.Report.
/// </summary>
class MaxPrintMgtDocTypeHandlersExt
{
    [SubscribesTo(classstr(PrintMgmtDocType), delegatestr(PrintMgmtDocType, getDefaultReportFormatDelegate))]
    public static void getDefaultReportFormatDelegate(PrintMgmtDocumentType _docType, EventHandlerResult _result)
    {
        switch (_docType)
        {
            case PrintMgmtDocumentType::CustAccountStatement:
                _result.result(ssrsReportStr(MaxCustAccountStatementExt, Report));
                break;
        }
    }
}
```

---

## Issues Encountered & Resolutions

This section documents real issues that occurred during the build, exactly as they happened, with the resolutions that worked.

### Issue 1 — Field name mismatch (compile errors in the handler class)

**Symptoms (compile errors):**
- `Table 'CustAccountStatementExtTmp' does not contain a field named 'CustGroup'.`
- `Table 'CustGroup' does not contain a field named 'Description'.`
- `'tempTable' is not declared.`
- `The qualifier 'tempTable' is not valid for field 'MaxTxT'.`

**Root cause:** The original 2019 article's handler code referenced `tempTable.CustGroup` and `custGroup.Description`. Verified against the current standard table metadata:
- `CustAccountStatementExtTmp` has **no** `CustGroup` field. It has `CustTable_AccountNum` (EDT `CustAccount`) with a relation to `CustTable` via `AccountNum`.
- `CustGroup` has **no** `Description` field. The description text is stored in the `Name` field (whose EDT happens to be named `Description`, which is what the original article confused).
- The article's Way 2 also had a typo — variable declared as `tmpTable` but referenced as `tempTable`.

**Resolution:** Use the correct lookup chain via `CustTable`. The corrected query:

```xpp
select firstonly CustGroup from custTable
    where custTable.AccountNum == tempTable.CustTable_AccountNum
    join Name from custGroup
        where custGroup.CustGroup == custTable.CustGroup;

tempTable.MaxTxT = custGroup.Name;
```

### Issue 2 — Parameter panel layout (deployment error)

**Symptom (at deploy time):**
```
System.Web.Services.Protocols.SoapException: The parameter panel layout
for this report contains more parameters than total cells available.
```

**Cause:** When `MaxTxT` was dragged into the report design, Visual Studio rewrote the embedded RDL and **injected a `ReportParametersLayout` block** that defined a grid of 4 columns × 2 rows = 8 cells. But the report has 36 parameters. 36 parameters cannot fit into 8 cells, so SSRS deployment fails.

**The injected XML block looked like:**
```xml
<ReportParametersLayout>
  <GridLayoutDefinition>
    <NumberOfColumns>4</NumberOfColumns>
    <NumberOfRows>2</NumberOfRows>
  </GridLayoutDefinition>
</ReportParametersLayout>
```

This block did **not** exist in the report before the field was dragged in. With no `ReportParametersLayout` block, SSRS auto-arranges the parameters and there is no overflow check.

**Resolution that worked (community-documented fix):**

1. Close the report in any open Visual Studio tab.
2. In Solution Explorer, right-click the report → **Open With...** → choose **XML (Text) Editor**.
3. Search for `ReportParametersLayout`.
4. **Delete the entire `<ReportParametersLayout>...</ReportParametersLayout>` block** (note: in the file it appears HTML-encoded as `&lt;ReportParametersLayout&gt;...`).
5. Save.
6. Build and deploy again.

After the block is removed, deployment succeeds and the parameter dialog renders with the standard auto-layout.

> **Note:** This is the *only* edit to RDL XML done in this project. It is on the **custom** report (in the USR/OHMS model), not on any standard report. If your governance forbids RDL XML edits even for custom reports, the alternative is the "hard reset" approach: create a new design in the report, copy the visual elements into it, delete the old design, rename the new one. This avoids the embedded XML block being injected the same way.

### Issue 3 — `MaxTxT` rendered on its own page (floating column)

**Symptom:** After successful deployment, the report ran but `MaxTxT` appeared on a separate empty page (the fourth page), with the value showing alone (e.g., "Retail customers, Retail customers, Retail customers"), instead of inline as a column in the transaction grid on the main pages.

**Cause:** When `MaxTxT` was dragged in, Visual Studio added a new tablix column of `1in` width and widened the report **body** from `7.5in` to `8.43198in` to accommodate it. But the page printable area is `7.5in`, so the rightmost column overflowed onto a separate page.

**Resolution that worked:** **Reduce the width of each existing column by approximately 1 inch in total** (distributed across the wider columns such as Description) so that the new `MaxTxT` column fits within the original `7.5in` body width. After narrowing the existing columns, the report body returned to `7.5in` and `MaxTxT` rendered inline as the rightmost column on each transaction row.

### Issue 4 — Trailing space in menu item Object property

**Symptom:**
```
Path: [AxMenuItemOutputExtension/CustAccountStatementExt.OHMS/Object]:
Class 'MaxCustAccountStatementExtController_Ext ' does not exist.
```

**Cause:** A trailing space character was accidentally included when typing/pasting the class name into the menu item extension's `Object` property. The compiler was looking for a class literally named `MaxCustAccountStatementExtController_Ext ` (with the trailing space).

**Resolution:** Open the menu item extension, clear the `Object` property completely, and re-type the class name carefully: `MaxCustAccountStatementExtController_Ext` — no leading or trailing whitespace. Save and rebuild.

### Issue 5 — Report name capitalization mismatch

**Symptom (runtime error):**
```
Unable to find the report design MaxCustAccountStatementExt.Report.
```

**Cause:** The duplicated report was named `MaXCustAccountStatementExt` (capital X) but every code reference used `MaxCustAccountStatementExt` (lowercase x). SSRS resolves report names exactly, so the framework couldn't find the report.

**Resolution:** Rename the report in Solution Explorer from `MaXCustAccountStatementExt` to `MaxCustAccountStatementExt` to match the code references. Save and rebuild.

---

## Print Management Configuration

After deployment, configure Print Management to use the custom design:

1. Navigate: **Accounts receivable → Inquiries and reports → Forms → Form setup**
2. Click **Print management**.
3. In the document tree on the left, expand and find: **Customer account statement → Original**.
4. In the right pane, set the **Report format** to **`MaxCustAccountStatementExt.Report`**.
5. Save and close.

From this point on, runs of the Customer Account Statement report use the custom design.

---

## Testing

### Test setup (USMF demo data)

1. Navigate: **Accounts receivable → Inquiries and reports → Customers → Customer account statement**.
2. Fill in the parameter dialog:

| Parameter | Value |
|---|---|
| From date | `1/1/2016` |
| To date | `2/2/2016` |
| Use print management destination | No |
| Show credit limit | No |
| Date interval | (blank) |
| Show due until | (blank) |
| Include company logo | Yes |
| Show maturity distribution | No |
| Aging period definitions | (selected, definition blank) |
| Only open | No |
| Include reversed | No |
| Balance other than zero | No |
| Show payment schedule | No |
| Single currency report | No |
| Destination | Screen |

3. Optionally, expand **Records to include** and add a customer filter (e.g., `Customer account = US-004`) to scope the output to one customer.
4. Click **OK**.

### Expected result

For customer **US-004 (Cave Wholesales)** — which belongs to customer group **`10`** (`Wholesales customers`):

- Each transaction row displays as in the standard report.
- The new rightmost column (`MaxTxT`) shows **`Wholesales customers`** on every transaction row for this customer.

### Stronger test (multiple customers)

Run the report **without** the customer filter, with a wider date range (e.g., `1/1/2016` to `12/31/2016`):

- Different customers in different groups should show different `MaxTxT` values:
  - Group `10` → `Wholesales customers`
  - Group `20` → `Major customers`
  - Group `30` → `Retail customers`
  - Group `40` → `Internet customers`
  - Group `80` → `Other customers`
  - Group `90` → `Intercompany customers`
  - Group `100` → `Intercompany retail customers`

This confirms the lookup is doing per-row work correctly, not returning a constant value.

### Quick sanity check on customer groups

To verify what value should appear for any given customer:

1. Navigate: **Accounts receivable → Customers → All customers** → open the customer → note the **Customer group** field on the General tab.
2. Navigate: **Accounts receivable → Setup → Customer groups** → find the matching row → the **Description** column displayed in the form is the underlying `Name` field on `CustGroup`. That value is what `MaxTxT` should display for that customer.

---

## Key Concepts

### Delegates in X++

A **delegate** is a method declared on a class with no body of its own — it is an extension point. The base class raises (calls) the delegate at a chosen point. Any subscriber method registered with `[SubscribesTo(...)]` for that delegate is invoked at that point. The subscriber can read input parameters and, if an `EventHandlerResult` is provided, write a result back that the base class will read.

Delegates exist so that customizations can extend standard behavior without modifying or overlayering Microsoft code. They are part of the broader extension model alongside event handlers (pre/post handlers) and Chain of Command (CoC).

In this project, the delegate `PrintMgmtDocType.getDefaultReportFormatDelegate` is the hook the framework raises when asking *"for this document type, what report design should I use by default?"*. The subscriber `MaxPrintMgtDocTypeHandlersExt.getDefaultReportFormatDelegate` answers *"for `CustAccountStatement`, use `MaxCustAccountStatementExt.Report` instead of the standard design"*, by writing the answer through the `EventHandlerResult` object via `_result.result(...)`.

### Two ways to populate report data

The original article documents two patterns for populating data in a report handler class:

| Way | Trigger point | Cardinality | Active in this project |
|---|---|---|---|
| **Way 1** — `Inserting` event on the temp table | Each row, at insert time | Once per row | ✅ Yes |
| **Way 2** — Post-handler on `CustAccountStatementExtDP.processReport()` | After the data provider finishes | Once total, single update pass | Commented out (equivalent) |

Both produce the same end result for this scenario. They differ only in *when* the work happens. Pick one — typically not both.

### Why all five extension artifacts are needed

Each artifact has a distinct job; removing any one breaks the chain:

| Artifact | Job |
|---|---|
| **Table extension** | Adds the storage for `MaxTxT` on the temp table |
| **Duplicated report** | Hosts the modified design that displays `MaxTxT` |
| **Controller extension class** | Forces the controller to use the custom report design |
| **Report handler class** | Computes the value of `MaxTxT` at runtime |
| **Delegate subscriber class** | Tells Print Management the custom report is the new default |
| **Menu item extension** | Routes UI navigation to the custom controller |

---

*Built and tested on D365 F&O 10.0.47, USMF demo data, May 2026.*
