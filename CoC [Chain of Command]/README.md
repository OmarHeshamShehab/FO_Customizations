# 🧩 Chain of Command Example – SalesTableType.validateWrite()

## Overview
This example demonstrates how to use **Chain of Command (CoC)** in Dynamics 365 Finance & Operations to extend standard business logic on the `SalesTableType` class.

The customization adds a simple validation rule:

> Prevent saving Sales orders where the **Customer group** is `"10"`.

This example uses **Contoso demo data** for easy testing.

---

## 🧠 How It Works
- The `validateWrite()` method runs whenever a Sales order header is **saved**.  
- The `next validateWrite()` call executes Microsoft’s standard logic first.  
- The extension then checks the **Customer group** field (`CustGroup`) on the SalesTable record.  
- If the group equals `"10"`, it displays an error and prevents saving the record.

---

## 🧪 Test Scenario (Contoso Data)

### Prerequisites
- D365 F&O development environment with **Contoso demo data** loaded.
- A build with the above extension compiled successfully.

### Steps

#### 1. Open the Sales order form
```
Modules > Sales and marketing > Sales orders > All sales orders
```

#### 2. Create a new Sales order
- Click **+ New**
- In the dialog:
  - **Customer account:** `US-003` (belongs to customer group 10)
  - Click **OK**

#### 3. Add one order line
- **Item number:** `D0001`
- **Quantity:** `1`
- Click **Save**

#### 4. Expected behavior
- The system displays:
  > ⚠️ “Sales orders for customer group 10 are not allowed in this demo.”
- The Sales order record will **not save**.

#### 5. Positive test
- Create another Sales order for `US-001` (Customer group = 30)
- Add one item line and **Save**
- ✅ Order saves successfully (no error message)

---

## 🧩 Technical Details

| Property | Value |
|-----------|--------|
| **Extension Type** | Chain of Command (method override) |
| **Extended Class** | `SalesTableType` |
| **Method Extended** | `validateWrite()` |
| **Purpose** | Custom validation before record save |
| **Test Data Used** | Contoso `US-001`, `US-003` customers |

---

## ✅ Expected Results Summary

| Scenario | Customer | CustGroup | Expected Result |
|-----------|-----------|-----------|-----------------|
| Negative | US-003 | 10 | Error message; cannot save |
| Positive | US-001 | 30 | Saves successfully |

---

## 🧩 Notes

- Always call `next validateWrite()` **exactly once** to comply with CoC rules.
- Avoid blank lines before `[ExtensionOf(...)]` — it must be the first line in your file.
- Replace the validation logic with your own business rule when building real extensions.

---

**Author:** Omar Shehab 
**Model:** MyCustomizations  
**Environment:** D365 F&O OneBox (Contoso data)  
**Date:** 2025-10-09  
