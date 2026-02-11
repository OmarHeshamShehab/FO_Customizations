
# D365 Finance and Operations Customizations (FO_Customization)

A curated collection of real-world customizations, tutorials, and best practices for Microsoft Dynamics 365 Finance and Operations (D365FO), developed and maintained by **Omar Hesham Mohamed Shehab** under the **OHMS** model.

---

## 📚 Table of Contents

- [Project Overview](#project-overview)
- [Repository Structure](#repository-structure)
- [Key Features](#key-features)
- [Getting Started](#getting-started)
- [Customization Modules](#customization-modules)
  - [ConVehicleManagement](#convehiclemanagement)
  - [Reports (SSRS Custom Report)](#reports-ssrs-custom-report)
  - [Halwani](#halwani)
  - [Metadata](#metadata)
  - [Commerce_CustomerListExtension](#commerce_customerlistextension)
  - [Chain_of_Command](#chain_of_command)
  - [SalesOrderExcelUpload (Sales Order Upload from Excel)](#salesorderexcelupload-sales-order-upload-from-excel)
  - [OHMS Service Integration](#ohms-service-integration)
- [Development Guidelines](#development-guidelines)
- [Testing & Verification](#testing--verification)
- [Contributing](#contributing)

---

<a id="project-overview"></a>
## Project Overview

This repository serves as a comprehensive resource for D365FO customizations, including:

- Client-specific solutions for real business requirements.
- Tutorials and cookbooks for learning and reference.
- Best practices for upgrade-safe, maintainable extensions.
- End-to-end examples covering data, business logic, and UI.

All solutions follow Microsoft extensibility guidelines to ensure upgrade safety.

---

<a id="repository-structure"></a>
## Repository Structure

### Customization Modules

- **ConVehicleManagement** – Vehicle tracking and maintenance scheduling.
- **Reports** – Custom SSRS reporting solution.
- **Halwani** – Client-specific customizations.
- **Metadata** – Data model and UI extensions.
- **Commerce_CustomerListExtension** – Customer entity extension.
- **Chain_of_Command** – CoC implementation examples.
- **SalesOrderExcelUpload** – Excel-driven sales order automation.
- **OHMS Service Integration** – Custom integration service module.

---

<a id="key-features"></a>
## Key Features

- Upgrade-safe customizations
- Real-world client implementations
- Reporting, services, automation examples
- Clean architecture and best practices

---

<a id="getting-started"></a>
## Getting Started

1. Build the solution in Visual Studio.
2. Synchronize database changes.
3. Deploy reports/services where applicable.
4. Test using Contoso demo data (USMF).

---

<a id="customization-modules"></a>
## Customization Modules

<a id="convehiclemanagement"></a>
### ConVehicleManagement

Custom vehicle management module including tracking and maintenance logic.

---

<a id="reports-ssrs-custom-report"></a>
### Reports (SSRS Custom Report)

Custom SSRS Daily Sales Report using:

- TempDB Table (TmpCarInvoice)
- Data Contract
- UI Builder
- RDP Class
- Controller
- Precision Design Layout

Report Name: **DSRReport**

---

<a id="halwani"></a>
### Halwani

Tailored solutions addressing unique client business processes.

---

<a id="metadata"></a>
### Metadata

Contains extended tables, forms, and workflows.

---

<a id="commerce_customerlistextension"></a>
### Commerce_CustomerListExtension

Adds custom **RefNoExt** field to the customer entity with synchronization support.

---

<a id="chain_of_command"></a>
### Chain_of_Command

Demonstrates Microsoft-recommended extension pattern using:

- Class CoC
- Form CoC
- Data Source CoC

Ensures upgrade-safe logic extension.

---

<a id="salesorderexcelupload-sales-order-upload-from-excel"></a>
### SalesOrderExcelUpload (Sales Order Upload from Excel)

Custom automation allowing upload of Excel (.xlsx) file to create:

- SalesTable records
- SalesLine records
- Financial Dimensions (DefaultDimension)

#### Excel Template (USMF)

| CustomerAccount | BusinessUnit | CostCenter | ItemId | Department | Qty | Project |
|----------------|-------------|------------|--------|------------|-----|---------|
| US-001 | 2 | 14 | D0001 | 22 | 5 | |
| US-001 | 3 | 14 | 1000 | 22 | 2 | |
| US-002 | 4 | 14 | D0003 | 22 | 3 | |

#### Success Message Example

Upload successful. Created 2 sales order(s): SO-000123, SO-000124. Total line(s): 5.

---

<a id="ohms-service-integration"></a>
### OHMS Service Integration

Secure service pattern including:

- DataContract classes
- changecompany usage
- Exception handling (CLR + X++)
- API endpoint exposure

Example endpoint:

/api/services/ohmsServiceGroup/ohmsService/Create

---

<a id="development-guidelines"></a>
## Development Guidelines

- Use Chain of Command.
- Avoid overlayering.
- Validate before insert.
- Use proper transaction handling.
- Follow OHMS naming standards.

---

<a id="testing--verification"></a>
## Testing & Verification

- Use Contoso demo data (USMF).
- Validate financial dimensions.
- Confirm SalesTable & SalesLine creation.
- Ensure no standard logic is broken.

---

<a id="contributing"></a>
## Contributing

1. Fork repository.
2. Create feature branch.
3. Follow coding standards.
4. Test thoroughly.
5. Submit pull request.

---

© OHMS – Omar Hesham Mohamed Shehab  
D365 Finance & Operations Customization Repository
