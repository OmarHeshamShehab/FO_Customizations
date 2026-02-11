# 📦 SalesOrderExcelUpload -- D365 Finance & Operations (OHMS)

## Overview

**SalesOrderExcelUpload** is a custom solution developed in Microsoft
Dynamics 365 Finance & Operations that enables automated Sales Order
creation from an Excel file.

The solution allows users to:

-   Upload an Excel (.xlsx) file
-   Automatically create Sales Orders
-   Automatically create Sales Lines
-   Apply Financial Dimensions line-wise
-   Receive a success message listing created Sales Orders

Developed under the **OHMS (Omar Hesham Mohamed Shehab)** customization
repository.

------------------------------------------------------------------------

# 🧩 Solution Structure (Visual Studio)

## Solution Name

SalesOrderExcelUpload

## Project Name

SalesOrderExcelUpload (USR) \[OHMS\]

## Components

  --------------------------------------------------------------------------------------
  Component                          Type                 Name
  ---------------------------------- -------------------- ------------------------------
  Runnable Class                     X++ Class            OHMSSalesOrderUploader

  Action Menu Item                   MenuItemAction       OHMSSalesOrderUploaderAction

  Form Extension                     SalesTableListPage   SalesTableListPage.OHMS
                                     Extension            
  --------------------------------------------------------------------------------------

------------------------------------------------------------------------

# 🏗 Architecture Overview

## 1️⃣ Form Extension

Extended Form: SalesTableListPage

Adds: - Custom button - Linked to Action Menu Item

------------------------------------------------------------------------

## 2️⃣ Action Menu Item

Name: OHMSSalesOrderUploaderAction

Type: Action

Object: OHMSSalesOrderUploader

Purpose: - Executes the runnable class - Opens upload dialog

------------------------------------------------------------------------

## 3️⃣ Runnable Class

Class: OHMSSalesOrderUploader

Responsibilities:

-   Show file upload dialog
-   Read Excel using OfficeOpenXml
-   Validate data
-   Create Sales Orders
-   Create Sales Lines
-   Apply Financial Dimensions
-   Display success message

------------------------------------------------------------------------

# 📊 Excel Template Structure (USMF -- Working Version)

  -----------------------------------------------------------------------------------
  CustomerAccount   BusinessUnit   CostCenter   ItemId   Department   Qty   Project
  ----------------- -------------- ------------ -------- ------------ ----- ---------
  US-001            2              14           D0001    22           5     

  US-001            3              14           1000     22           2     

  US-002            4              14           D0003    22           3     
  -----------------------------------------------------------------------------------

------------------------------------------------------------------------

## 📌 Excel Rules

-   Row 1 = Header
-   Data starts from Row 2
-   File format must be `.xlsx`
-   ItemId column formatted as **Text**
-   Excel sorted by CustomerAccount
-   Dimension values must match Operating Units exactly

Correct dimension format in USMF: 2, 14, 22

------------------------------------------------------------------------

# ⚙ Functional Logic

## 🔹 Sales Order Header Creation

New Sales Order created when: CustomerAccount changes

Process:

-   Generate SalesId from Number Sequence
-   Call initValue()
-   Set SalesType = Sales
-   Assign CustAccount
-   Trigger modifiedField(CustAccount)
-   Call initFromCustTable()
-   Insert SalesTable record

------------------------------------------------------------------------

## 🔹 Sales Line Creation

Lines created only when: Qty \> 0

Process:

-   Validate Item exists
-   Set SalesId
-   Set ItemId
-   Call modifiedField(ItemId)
-   Set SalesQty
-   Call createLine()
-   Apply financial dimensions

------------------------------------------------------------------------

# 🧮 Financial Dimension Handling

Dimensions applied line-wise:

-   BusinessUnit
-   CostCenter
-   Department
-   Project

Validation process:

1.  Find DimensionAttribute
2.  Validate value exists
3.  Build DimensionAttributeValueSetStorage
4.  Assign to SalesLine.DefaultDimension

------------------------------------------------------------------------

# 🛡 Validation Logic

  Validation                Behavior
  ------------------------- --------------
  Blank row                 Skipped
  Missing CustomerAccount   Error
  Missing ItemId            Error
  Customer does not exist   Error
  Item does not exist       Error
  Qty = 0                   Line skipped
  Invalid dimension value   Error

------------------------------------------------------------------------

# 🔄 Transaction Handling

Entire upload runs inside: ttsBegin / ttsCommit

If any error occurs: ttsAbort

Ensures data integrity and no partial insert.

------------------------------------------------------------------------

# 🟢 Success Messaging

After successful upload: Upload successful. Created X sales order(s):
000885, 000886. Total line(s): Y.

If nothing created: Upload completed. No sales orders were created.

------------------------------------------------------------------------

# 🧪 Test Scenario (Contoso -- USMF)

Environment: - OneBox - Company: USMF - Contoso demo data

Test Steps:

1.  Navigate to: Sales and marketing \> Sales orders \> All sales orders

2.  Click Upload Excel (OHMS button).

3.  Select working Excel file.

4.  Click OK.

Expected Results:

-   Sales Orders created
-   Lines created
-   Dimensions applied
-   Success message displayed
-   SalesTableListPage refreshes

------------------------------------------------------------------------

# 📌 Technical Summary

  Property               Value
  ---------------------- ---------------------------
  Model                  USR
  Custom Prefix          OHMS
  Company Tested         USMF
  Framework Used         OfficeOpenXml
  Transaction Control    ttsBegin / ttsCommit
  Line Creation Method   createLine()
  Dimension Method       getFinancialDimensionUSMF
  Form Extended          SalesTableListPage

------------------------------------------------------------------------

# 🚀 Production Recommendations

-   Replace hardcoded strings with Labels
-   Add logging table
-   Convert to SysOperation (Batch processing)
-   Commit per customer block
-   Add file size validation
-   Add security privilege mapping
-   Cache dimension attributes for performance

------------------------------------------------------------------------

# 🏁 Final Summary

The SalesOrderExcelUpload solution demonstrates:

✔ Real-world automation\
✔ Clean X++ architecture\
✔ Financial dimension handling\
✔ Upgrade-safe development\
✔ Production-level validation\
✔ Working implementation in USMF
