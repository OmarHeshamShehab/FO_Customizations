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

## Project Overview

This repository serves as a comprehensive resource for D365FO customizations, including:

- Client-specific solutions for real business requirements.
- Tutorials and cookbooks for learning and reference.
- Best practices for upgrade-safe, maintainable extensions.
- End-to-end examples covering data, business logic, and UI.

All solutions are designed to be **upgrade-friendly** and follow Microsoft’s extensibility guidelines.

---

## Repository Structure

### Customization Modules

- **ConVehicleManagement**
- **Reports (SSRS Custom Report)**
- **Halwani**
- **Metadata**
- **Commerce_CustomerListExtension**
- **Chain_of_Command**
- **SalesOrderExcelUpload**
- **OHMS Service Integration**

---

## Key Features

- Upgrade-safe customizations
- Real-world implementation scenarios
- SSRS reporting
- Service integrations
- Chain of Command extensions
- Excel-based automation tools
- Production-ready coding patterns

---

## Getting Started

1. Clone repository.
2. Open solution in Visual Studio.
3. Build and synchronize database.
4. Deploy reports/services.
5. Test using Contoso demo data (USMF).

---

# Customization Modules

---

## Reports (SSRS Custom Report)

Custom SSRS report demonstrating full implementation pattern:

- TempDB table (TmpCarInvoice)
- Data Contract
- UI Builder
- RDP Class
- Controller
- Action Menu Item
- Precision Design Layout

Displays Daily Sales Data filtered by date range and warehouse.

---

## SalesOrderExcelUpload (Sales Order Upload from Excel)

### Overview

A complete automation solution allowing Excel upload to automatically create:

- Sales Orders (SalesTable)
- Sales Lines (SalesLine)
- Line-level Financial Dimensions (DefaultDimension)

Built under the **OHMS model** and tested in **USMF (Contoso demo environment)**.

---

### Business Logic

- Creates new Sales Order when CustomerAccount changes.
- Skips rows where Qty = 0.
- Validates Customer and Item existence.
- Applies Financial Dimensions line-wise.
- Displays summary message after upload.

---

### Excel Template (USMF)

Row 1 = Header  
Data starts from Row 2.

| CustomerAccount | BusinessUnit | CostCenter | ItemId | Department | Qty | Project |
|----------------|-------------|------------|--------|------------|-----|---------|
| US-001 | 2 | 14 | D0001 | 22 | 5 | |
| US-001 | 3 | 14 | 1000 | 22 | 2 | |
| US-002 | 4 | 14 | D0003 | 22 | 3 | |

---

### Technical Components

| Object | Type |
|--------|------|
| OHMSSalesOrderUploader | Runnable Class |
| OHMSSalesOrderUploaderAction | Action Menu Item |
| SalesTableListPage.OHMS | Form Extension |

---

### Example Success Message

Upload successful. Created 2 sales order(s): SO-000123, SO-000124. Total line(s): 5.

---

### Testing (USMF)

- Validate customer exists.
- Validate item exists.
- Validate financial dimension values.
- Verify SalesLine.DefaultDimension populated.
- Confirm status = Open order.

---

## OHMS Service Integration

Custom service module implementing:

- DataContract classes
- changecompany execution
- Structured response pattern
- Secure API endpoint exposure

Example Endpoint:

/api/services/ohmsServiceGroup/ohmsService/Create

---

## Development Guidelines

- Use Chain of Command (CoC).
- Avoid overlayering.
- Keep logic in classes.
- Use proper transaction handling.
- Follow OHMS naming convention.
- Keep customizations upgrade-safe.

---

## Testing & Verification

- Use Contoso demo data.
- Validate headers and lines creation.
- Confirm no regression in standard logic.
- Perform negative scenario testing.

---

## Contributing

1. Fork repository.
2. Create feature branch.
3. Follow coding standards.
4. Test thoroughly.
5. Submit pull request with documentation.

---

© OHMS – Omar Hesham Mohamed Shehab  
D365 Finance & Operations Customization Repository
