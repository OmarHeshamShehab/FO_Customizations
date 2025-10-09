# 🧩 Chain of Command (CoC) Examples – D365 Finance & Operations

## Overview

This document showcases practical examples of **Chain of Command (CoC)** in Microsoft Dynamics 365 Finance & Operations.  
Each example demonstrates how to safely extend standard application logic without overlayering, following Microsoft’s extensibility best practices.

These examples are part of the **Chain_of_Command** learning module under the **OHMS** (Omar Hesham Mohamed Shehab) customization repository.

---

## 📘 Table of Contents
1. [Introduction to Chain of Command](#-introduction-to-chain-of-command)
2. [Example 1 – SalesTableType.validateWrite() (Class CoC)](#-example-1--salestabletypevalidatewrite-class-coc)
3. [Example 2 – SalesTable Form.run() (Form CoC)](#-example-2--salestable-formrun-form-coc)
4. [General Notes & Best Practices](#-general-notes--best-practices)
5. [Author & Environment](#author--environment)


---

## 🧠 Introduction to Chain of Command

The **Chain of Command (CoC)** mechanism allows developers to extend standard methods without directly modifying Microsoft’s base code.  
It helps maintain upgrade-safe customizations by wrapping custom logic *before* or *after* standard method calls.

A CoC method always calls the original implementation using:

```x++
next <methodName>(parameters);
```

This ensures Microsoft’s base behavior runs as intended.

---

## 🧩 Example 1 – SalesTableType.validateWrite() (Class CoC)

### 📄 Purpose

Extend the `SalesTableType` class to add a **custom validation rule** that prevents saving Sales orders belonging to a specific **Customer group** (`CustGroup = "10"`).

### 🧠 How It Works

- `validateWrite()` executes when a Sales order header is saved.
- `next validateWrite()` runs the original Microsoft logic.
- The CoC checks the `CustGroup` field on the SalesTable.
- If the group equals `"10"`, an error message prevents saving.

---

### 🧪 Test Scenario (Contoso Data)

#### Prerequisites
- OneBox developer environment with Contoso data.
- Successful build including this CoC class.

#### Steps

1. **Open:**
   ```
   Modules > Sales and marketing > Sales orders > All sales orders
   ```

2. **Create a new Sales order:**
   - Customer: `US-003` (Customer group = 10)
   - Add one order line and click **Save**

3. **Expected Result:**
   > ⚠️ “Sales orders for customer group 10 are not allowed in this demo.”

4. **Positive Test:**
   - Create order for `US-001` (Customer group = 30)
   - Add line → **Save**
   - ✅ Order saves successfully.

---

### 🧩 Technical Details

| Property | Value |
|-----------|--------|
| **Extension Type** | Chain of Command (class method override) |
| **Extended Class** | `SalesTableType` |
| **Method Extended** | `validateWrite()` |
| **Purpose** | Prevent saving based on Customer group |
| **Test Data Used** | Contoso `US-001`, `US-003` |

---

### ✅ Expected Results

| Scenario | Customer | CustGroup | Result |
|-----------|-----------|-----------|--------|
| Negative | US-003 | 10 | Error – cannot save |
| Positive | US-001 | 30 | Saves successfully |

---

## 🧩 Example 2 – SalesTable Form.run() (Form CoC)

### 📄 Purpose

Extend the `SalesTable` form using Chain of Command to display a **welcome message** whenever the Sales order form is opened.  
This is a **form-only CoC** — it doesn’t access any data source.

---

### 🧠 How It Works

- `run()` executes when the form finishes initialization.
- `next run()` ensures standard logic executes first.
- Displays a message using `info()` with the current user’s ID.
- Fires every time the **SalesTable form** opens.

---

### 🧪 Test Scenario (Contoso Data)

#### Prerequisites
- D365 F&O OneBox with Contoso data.
- Successful build including the form extension.

#### Steps

1. **Open:**
   ```
   Modules > Sales and marketing > Sales orders > All sales orders
   ```

2. **Open any order**, e.g. `USMF-000001`.

3. **Expected Result:**
   > 🔹 Hello admin! The Sales order form has been opened.

4. **Optional Variation:**
   - Log in as another user (e.g., `USMF\Jodi`) and open any order.
   - The message updates dynamically with the current user ID.

---

### 🧩 Technical Details

| Property | Value |
|-----------|--------|
| **Extension Type** | Chain of Command (form method override) |
| **Extended Form** | `SalesTable` |
| **Method Extended** | `run()` |
| **Purpose** | Display message when form opens |
| **Data Source Used** | None (pure form-level logic) |
| **Test Data Used** | Contoso Sales order `USMF-000001` |

---

### ✅ Expected Results

| Scenario | User | Expected Result |
|-----------|------|-----------------|
| Any | admin | Info message appears |
| Any | Jodi | Info message appears with user name |

---

## 📘 General Notes & Best Practices

- Always call `next <method>()` **exactly once and unconditionally**.  
- The `[ExtensionOf(...)]` attribute must be the **first line** in your file.  
- Keep **business logic in classes/tables**, not forms, to follow clean architecture.  
- Use **Form CoCs** for UI or lifecycle events.  
- Use **Class/Table CoCs** for business validations or data rules.  
- Avoid heavy computations inside form events like `run()` or `init()`.

---

## 👨‍💻 Author & Environment

| Field | Value |
|--------|--------|
| **Author** | Omar Shehab |
| **Model** | OHMS |
| **Environment** | D365 F&O OneBox (Contoso data) |
| **Date** | 2025-10-09 |
