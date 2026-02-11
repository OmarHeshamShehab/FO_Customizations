# D365 Finance and Operations Customizations (FO_Customization)

A curated collection of real-world customizations, tutorials, and best practices for Microsoft Dynamics 365 Finance and Operations (D365FO), developed and maintained by **Omar Hesham Mohamed Shehab** under the **OHMS** model.

---

## 📚 Table of Contents

* [Project Overview](#project-overview)
* [Repository Structure](#repository-structure)
* [Key Features](#key-features)
* [Getting Started](#getting-started)
* [Customization Modules](#customization-modules)

  * [ConVehicleManagement](#convehiclemanagement)
  * [Reports (SSRS Custom Report)](#reports-ssrs-custom-report)
  * [Halwani](#halwani)
  * [Metadata](#metadata)
  * [Commerce_CustomerListExtension](#commerce_customerlistextension)
  * [Chain_of_Command](#chain_of_command)
  * [OHMS Service Integration](#ohms-service-integration)
* [Development Guidelines](#development-guidelines)
* [Testing & Verification](#testing--verification)
* [Contributing](#contributing)

---

## Project Overview

This repository serves as a comprehensive resource for D365FO customizations, including:

* **Client-specific solutions** for real business requirements.
* **Tutorials and cookbooks** for learning and reference.
* **Best practices** for upgrade-safe, maintainable extensions.
* **End-to-end examples** covering data, business logic, and UI.

All solutions are designed to be **upgrade-friendly** and follow Microsoft’s extensibility guidelines, ensuring safe coexistence with standard application updates.

---

## Repository Structure

### Customization Modules

* **ConVehicleManagement**: Customizations for vehicle management, including tracking and maintenance scheduling.
* **Reports (Reports)**: Custom SSRS report solution demonstrating end-to-end creation of a DSR (Daily Sales Report) using TempDB table, Data Contract, UI builder, RDP class, report design, controller and action menu. (See detailed section below.)
* **Halwani**: Tailored solutions for the Halwani client, addressing unique business processes and integrations.
* **Metadata**: Files related to data models, form layouts, and workflows for the custom solutions.
* **Commerce_CustomerListExtension**: Extension adding a custom **RefNoExt** field to the customer entity, with real-time data synchronization across systems.
* **Chain_of_Command**: Examples demonstrating the use of the **Chain of Command (CoC)** mechanism to extend standard application logic.

---

## Key Features

* Comprehensive D365FO customizations repository.
* Real-world examples and client-specific solutions.
* Detailed tutorials and best practices.
* Focus on upgrade-safe and maintainable code.
* Coverage of data, business logic, and user interface extensions.

---

## Getting Started

To get started with the projects in this repository:

1. **Explore the customization modules** to understand the available solutions.
2. **Refer to the tutorials and cookbooks** for guidance on implementing and adapting the solutions.
3. **Follow the development guidelines** to ensure consistency and quality in customizations.
4. **Test and verify** the implementations as per the provided testing guidelines.

---

## Customization Modules

### ConVehicleManagement

Customizations for vehicle management, including tracking and maintenance scheduling.

### Reports (SSRS Custom Report)

# Reports Solution (Custom SSRS Report in D365 Finance and Operations)

## 📘 Overview

This project demonstrates how to develop a **custom SSRS report** from scratch in **Dynamics 365 Finance and Operations (D365FnO)** using the following key components:

* **Temporary Table (TmpCarInvoice)**
* **Data Contract Class**
* **UI Builder Class**
* **Report Data Provider (RDP) Class**
* **Report Design**
* **Controller Class**
* **Action Menu Item**

The report displays **Daily Sales Data** based on customer invoices with filtering options such as date range and warehouse.

---

## 🧱 Components

### 1. Temporary Table: `TmpCarInvoice`

The temporary table defines the structure of the report data.

**Fields**

| Field Name       | Description               | EDT Suggestion (if available) |
| ---------------- | ------------------------- | ----------------------------- |
| CarRegNo         | Car Registration Number   | `CarRegNum` (custom)          |
| CustAccount      | Customer Account          | `CustAccount`                 |
| CustGroupId      | Customer Group            | `CustGroupId`                 |
| CustName         | Customer Name             | `Name`                        |
| InventLocationId | Warehouse / Site          | `InventLocationId`            |
| InvoiceDate      | Invoice Date              | `TransDate`                   |
| InvoiceId        | Invoice Number            | `InvoiceId`                   |
| LineAmount       | Line Amount               | `AmountMST`                   |
| MobileNumber     | Customer Mobile Number    | `Phone` (custom)              |
| PaymMode         | Payment Mode              | `PaymMode`                    |
| SalesId          | Sales Order ID            | `SalesId`                     |
| UserId           | Created By User           | `UserId` / `SysUserId`        |
| CustomerRegion   | Customer Region / Country | `Name` or custom EDT          |

**Properties**

* `TableType` = **TempDB**

---

### 2. Data Contract Class: `DSRReportDC`

Defines parameters and filters for the report.
Implements attributes for DataContract, grouping, and validation.

**Parameters:**

* From Date
* To Date
* Warehouse

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

* `processReport()` – Queries `CustInvoiceJour` and populates temp table.
* `getTempTable()` – Returns the dataset for the report.

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

* `Label` = DSR Report
* `Object Type` = Class
* `Object` = DSRReportController

---

## 🚀 How to Build and Deploy

1. **Build the project** in Visual Studio.
2. **Deploy the report** from Solution Explorer.
3. **Add the Action Menu Item** to a menu or workspace.
4. Run the report and apply parameters (date range, warehouse).

---

## 🧾 Example Output

The report displays daily sales invoices by:

* Invoice ID
* Customer details
* Warehouse
* Amount
* Region
* Created user

---

## 🧠 Notes

* Always synchronize the table before building.
* Ensure the RDP and Report are deployed under the same model.
* Validate parameters in the Data Contract for consistent input.
* If `UserId` EDT is not found, use `SysUserId` or create a new EDT extending `Name`.

---

## 🧩 Author

Developed following best practices for SSRS report creation in **Dynamics 365 Finance and Operations**.

---

**📅 Version:** 1.0
**🧰 Environment:** D365FnO
**📗 Report Name:** DSRReport
**📄 Report Design:** Precision Layout (CarInvoiceDS)

---

✅ **End of Reports README**

---

### Halwani

Tailored solutions for the Halwani client, addressing unique business processes and integrations.

### Metadata

Files related to data models, form layouts, and workflows for the custom solutions.

### Commerce_CustomerListExtension

Extension adding a custom **RefNoExt** field to the customer entity, with real-time data synchronization across systems.

### Chain_of_Command

Examples demonstrating the use of the **Chain of Command (CoC)** mechanism to extend standard application logic.

---

### OHMS Service Integration

A **custom service module** built under the **OHMS model**, providing an example of a secure, extensible integration pattern for Dynamics 365 Finance and Operations (D365FO).

#### 📦 Components

* **ohmsRequest** — Input contract containing the `dataAreaId` (target legal entity).
* **ohmsResponse** — Output contract containing `Success`, `ErrorMessage`, and `DebugMessage` values.
* **ohmsService** — Core service logic class implementing a `Create` operation that executes within a specific company context.

#### 🧠 Key Highlights

* Implements best-practice service patterns using **[DataContract]** and **[DataMember]** attributes.
* Uses `changecompany` for context-specific execution.
* Handles both **CLR** and **X++ exceptions** safely.
* Demonstrates correct use of `InteropPermission` for .NET interop calls.
* Returns standardized response objects for integrations and API consumers.

#### 🧰 Deployment & Setup

1. Create a **service** named `ohmsService` and assign the `ohmsService` class.
2. Add the `Create` method to the service.
3. Create a **service group** named `ohmsServiceGroup` and include the service.
4. Set `Auto Deploy = Yes` and synchronize the model.

#### 🔬 Testing (Postman)

Use a `POST` request to:

```
https://usnconeboxax1aos.cloud.onebox.dynamics.com/api/services/ohmsServiceGroup/ohmsService/Create
```

**Body:**

```json
{
    "_request": {
        "dataAreaId": "usmf"
    }
}
```

**Headers:**

| Key           | Value                      |
| ------------- | -------------------------- |
| Content-Type  | application/json           |
| Authorization | Bearer <your-access-token> |

**Sample Response:**

```json
{
    "Success": "true",
    "ErrorMessage": "",
    "debugMessage": "Hello World from usmf"
}
```

---

## Development Guidelines

These guidelines ensure consistency, quality, and maintainability of customizations:

* Use the **Chain of Command (CoC)** for extending existing logic.
* Keep customizations **upgrade-safe** by avoiding overlayering and following best practices.
* Document all customizations and extensions thoroughly.

---

## Testing & Verification

To ensure the customizations work as intended:

* Follow the testing steps outlined in each module’s documentation.
* Verify data synchronization and integration points, especially for Commerce-related customizations.
* Validate that CoC implementations do not break standard functionality and are upgrade-safe.

---

## Contributing

Contributions are welcome! To contribute to this repository:

1. Fork the repository and create a new branch for your feature or fix.
2. Make your changes, following the development guidelines.
3. Test your changes thoroughly.
4. Submit a pull request with a clear description of your changes and their purpose.
