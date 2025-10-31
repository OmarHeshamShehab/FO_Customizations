# 🧩 Chain of Command (CoC) Examples – D365 Finance & Operations

## Overview
This document showcases practical examples of **Chain of Command (CoC)** in Microsoft Dynamics 365 Finance & Operations. Each example demonstrates how to safely extend standard application logic without overlayering, following Microsoft's extensibility best practices. These examples are part of the **Chain_of_Command** learning module under the **OHMS** (Omar Hesham Mohamed Shehab) customization repository.

## 📘 Table of Contents
1. [Introduction to Chain of Command](#introduction-to-chain-of-command)
2. [Example 1 – SalesTableType.validateWrite()](#example-1--salestabletypevalidatewrite-class-coc)
3. [Example 2 – SalesTable Form.run()](#example-2--salestable-formrun-form-coc)
4. [Example 3 – HcmGoal Form Data Source Display Coloring](#example-3--hcmgoal-form-data-source-display-coloring)
5. [General Notes & Best Practices](#general-notes--best-practices)

## 🧠 Introduction to Chain of Command
The **Chain of Command (CoC)** mechanism allows developers to extend standard methods without directly modifying Microsoft's base code. It helps maintain upgrade-safe customizations by wrapping custom logic *before* or *after* standard method calls. A CoC method always calls the original implementation using: `next <methodName>(parameters);` This ensures Microsoft's base behavior runs as intended.

## 🧩 Example 1 – SalesTableType.validateWrite() (Class CoC)
**Purpose:** Extend the `SalesTableType` class to add a **custom validation rule** that prevents saving Sales orders belonging to a specific **Customer group** (`CustGroup = "10"`).

**How It Works:** `validateWrite()` executes when a Sales order header is saved. `next validateWrite()` runs the original Microsoft logic. The CoC checks the `CustGroup` field on the SalesTable. If the group equals `"10"`, an error message prevents saving.

**Test Scenario (Contoso Data):** **Prerequisites:** OneBox developer environment with Contoso data. Successful build including this CoC class. **Steps:** Open `Modules > Sales and marketing > Sales orders > All sales orders`. Create a new Sales order with Customer: `US-003` (Customer group = 10). Add one order line and click **Save**. **Expected Result:** `⚠️ "Sales orders for customer group 10 are not allowed in this demo."` **Positive Test:** Create order for `US-001` (Customer group = 30). Add line → **Save**. ✅ Order saves successfully.

**Technical Details:**
| Property | Value |
|-----------|--------|
| Extension Type | Chain of Command (class method override) |
| Extended Class | `SalesTableType` |
| Method Extended | `validateWrite()` |
| Purpose | Prevent saving based on Customer group |
| Test Data Used | Contoso `US-001`, `US-003` |

**Expected Results:**
| Scenario | Customer | CustGroup | Result |
|-----------|-----------|-----------|--------|
| Negative | US-003 | 10 | Error – cannot save |
| Positive | US-001 | 30 | Saves successfully |

## 🧩 Example 2 – SalesTable Form.run() (Form CoC)
**Purpose:** Extend the `SalesTable` form using Chain of Command to display a **welcome message** whenever the Sales order form is opened. This is a **form-only CoC** — it doesn't access any data source.

**How It Works:** `run()` executes when the form finishes initialization. `next run()` ensures standard logic executes first. Displays a message using `info()` with the current user's ID. Fires every time the **SalesTable form** opens.

**Test Scenario (Contoso Data):** **Prerequisites:** D365 F&O OneBox with Contoso data. Successful build including the form extension. **Steps:** Open `Modules > Sales and marketing > Sales orders > All sales orders`. Open any order, e.g. `USMF-000001`. **Expected Result:** `🔹 Hello admin! The Sales order form has been opened.` **Optional Variation:** Log in as another user (e.g., `USMF\Jodi`) and open any order. The message updates dynamically with the current user ID.

**Technical Details:**
| Property | Value |
|-----------|--------|
| Extension Type | Chain of Command (form method override) |
| Extended Form | `SalesTable` |
| Method Extended | `run()` |
| Purpose | Display message when form opens |
| Data Source Used | None (pure form-level logic) |
| Test Data Used | Contoso Sales order `USMF-000001` |

**Expected Results:**
| Scenario | User | Expected Result |
|-----------|------|-----------------|
| Any | admin | Info message appears |
| Any | Jodi | Info message appears with user name |

## 🧩 Example 3 – HcmGoal Form Data Source Display Coloring
**Purpose:** Extend the `HcmGoal` form data source to apply **conditional background coloring** to goals based on their status. This provides visual status tracking for performance management, allowing users to quickly assess goal progress at a glance.

**How It Works:** `displayOption()` executes for each record as it's rendered in the form grid. `next displayOption()` ensures standard display logic runs. The CoC checks the `Status` field of each HcmGoal record. Applies background colors using `WinAPI::RGB2int()` based on status value. Creates an intuitive color-coded interface for performance tracking.

**Test Scenario (Contoso Data):** **Prerequisites:** D365 F&O environment with Human Resources module. Contoso demo data with existing goals. **Steps:** Navigate to `Human resources > Performance > Goals`. View the goals list - you should see records colored based on status. **Expected Visual Results:** 🟢 **Light Green** - Goals with status: `Completed` or `OnTrack`. 🟠 **Light Orange** - Goals with status: `NeedsImprovement`. 🟡 **Light Yellow** - Goals with status: `NotStarted`. **Verification:** Create or modify goals to see color changes in real-time.

**Technical Details:**
| Property | Value |
|-----------|--------|
| Extension Type | Chain of Command (form data source method override) |
| Extended Element | `HcmGoal` form data source |
| Method Extended | `displayOption()` |
| Purpose | Visual status indication through background coloring |
| Color Logic | Status-based RGB color mapping |
| Test Location | HR > Performance > Goals |

**Color Scheme Reference:**
| Status | Color | RGB Value | Visual Meaning |
|--------|-------|------------|----------------|
| Completed | Light Green | (144, 238, 144) | Success/Achieved |
| OnTrack | Light Green | (144, 238, 144) | Progressing Well |
| NeedsImprovement | Light Orange | (255, 165, 0) | Requires Attention |
| NotStarted | Light Yellow | (255, 255, 224) | Action Needed |

**Expected Results:**
| Scenario | Goal Status | Visual Result |
|-----------|-------------|---------------|
| Positive Progress | Completed/OnTrack | Light Green background |
| Needs Attention | NeedsImprovement | Light Orange background |
| Not Initiated | NotStarted | Light Yellow background |

## 📘 General Notes & Best Practices
- Always call `next <method>()` **exactly once and unconditionally**.
- The `[ExtensionOf(...)]` attribute must be the **first line** in your file.
- Keep **business logic in classes/tables**, not forms, to follow clean architecture.
- Use **Form CoCs** for UI or lifecycle events.
- Use **Class/Table CoCs** for business validations or data rules.
- Use **Form Data Source CoCs** for record-level visual enhancements like coloring.
- Avoid heavy computations inside form events like `run()` or `init()`.
- For display enhancements, ensure colors provide sufficient contrast for accessibility.
- Test color schemes across different themes and user preferences.

## 🔧 Technical Implementation Notes
All examples follow the standard CoC pattern:
```x++
[ExtensionOf(<elementToExtend>)]
final class <MeaningfulExtensionName>
{
    public <returnType> <methodName>(<parameters>)
    {
        // Pre-logic (if needed)
        next <methodName>(<parameters>);
        // Post-logic (if needed)
    }
}