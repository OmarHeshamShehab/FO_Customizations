# DSR Report (Custom SSRS Report in D365 Finance and Operations)

## 📘 Overview
This project demonstrates how to develop a **custom SSRS report** from scratch in **Dynamics 365 Finance and Operations (D365FnO)** using the following key components:
- **Temporary Table (TmpCarInvoice)**
- **Data Contract Class**
- **UI Builder Class**
- **Report Data Provider (RDP) Class**
- **Report Design**
- **Controller Class**
- **Action Menu Item**

The report displays **Daily Sales Data** based on customer invoices with filtering options such as date range and warehouse.

---

## 🧱 Components

### 1. Temporary Table: `TmpCarInvoice`
The temporary table defines the structure of the report data.

**Fields**
| Field Name       | Description                      | EDT Suggestion (if available)      |
|------------------|----------------------------------|------------------------------------|
| CarRegNo         | Car Registration Number          | `CarRegNum` (custom)               |
| CustAccount      | Customer Account                 | `CustAccount`                      |
| CustGroupId      | Customer Group                   | `CustGroupId`                      |
| CustName         | Customer Name                    | `Name`                             |
| InventLocationId | Warehouse / Site                 | `InventLocationId`                 |
| InvoiceDate      | Invoice Date                     | `TransDate`                        |
| InvoiceId        | Invoice Number                   | `InvoiceId`                        |
| LineAmount       | Line Amount                      | `AmountMST`                        |
| MobileNumber     | Customer Mobile Number           | `Phone` (custom)                   |
| PaymMode         | Payment Mode                     | `PaymMode`                         |
| SalesId          | Sales Order ID                   | `SalesId`                          |
| UserId           | Created By User                  | `UserId` / `SysUserId`             |
| CustomerRegion   | Customer Region / Country        | `Name` or custom EDT               |

**Properties**
- `TableType` = **TempDB**

---

### 2. Data Contract Class: `DSRReportDC`
Defines parameters and filters for the report.  
Implements attributes for DataContract, grouping, and validation.

**Parameters:**
- From Date
- To Date
- Warehouse

Includes a validation method to ensure proper date selection.

---

### 3. UI Builder Class: `DSRReportUIBuilder`
Customizes the dialog box UI for the report.  
Adds and binds dialog fields for user input, including a warehouse lookup.

---

### 4. Report Data Provider (RDP): `DSRReportDP`
Handles the business logic and data fetching from **CustInvoiceJour**.  
Processes the data, applies filters (date, warehouse), and inserts it into the `TmpCarInvoice` table.

**Key methods:**
- `processReport()` – Queries `CustInvoiceJour` and populates temp table.
- `getTempTable()` – Returns the dataset for the report.

---

### 5. Report Design
Created in Visual Studio under **Reports > New Report**.

**DataSet:** `CarInvoiceDS`  
**Data Source:** `TmpCarInvoice`  
**Design Layout:** Precision Design displaying customer, invoice, and warehouse data.

Steps:
1. Add dataset based on `TmpCarInvoice`.
2. Configure layout with required fields.
3. Deploy and verify output in SSRS.

---

### 6. Controller Class: `DSRReportController`
Controls report execution and runtime behavior.

**Key Logic:**
```x++
class DSRReportController extends SrsReportRunController
{
    public static void main(Args args)
    {
        DSRReportController controller = new DSRReportController();
        controller.parmReportName(ssrsreportstr(DSRReport, Report));
        controller.parmDialogCaption("DSR Report");
        controller.startOperation();
    }
}
```

---

### 7. Action Menu Item
Used to launch the report from the user interface.

**Properties:**
- `Label` = DSR Report  
- `Object Type` = Class  
- `Object` = DSRReportController  

---

## 🚀 How to Build and Deploy
1. **Build the project** in Visual Studio.
2. **Deploy the report** from Solution Explorer.
3. **Add the Action Menu Item** to a menu or workspace.
4. Run the report and apply parameters (date range, warehouse).

---

## 🧾 Example Output
The report displays daily sales invoices by:
- Invoice ID
- Customer details
- Warehouse
- Amount
- Region
- Created user

---

## 🧠 Notes
- Always synchronize the table before building.
- Ensure the RDP and Report are deployed under the same model.
- Validate parameters in the Data Contract for consistent input.
- If `UserId` EDT is not found, use `SysUserId` or create a new EDT extending `Name`.

---

## 🧩 Author
Developed following best practices for SSRS report creation in **Dynamics 365 Finance and Operations**.

---

**📅 Version:** 1.0  
**🧰 Environment:** D365FnO  
**📗 Report Name:** DSRReport  
**📄 Report Design:** Precision Layout (CarInvoiceDS)

---

✅ **End of README**
