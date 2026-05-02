# Scenario 01 — Block Customer Deletion When Open Sales Orders Exist

**Pattern:** Chain of Command on a table method
**Element type:** Table (`CustTable`)
**Method extended:** `validateDelete()`
**Project:** `OHMS_Scenario01_BlockCustomerDelete`
**Difficulty:** ⭐ Beginner — first real CoC scenario most F&O developers meet on the job

---

## 1. Business problem

In any real implementation, the AR (Accounts Receivable) team periodically cleans up the customer master by deleting customers that look unused. Standard Dynamics 365 F&O does protect against deleting customers with related sales orders, but the message is generic — it just says *"Transactions exist in table Sales orders"* without telling the user **which** order is in the way.

The Finance team's request is precise:

> *"If a customer has any open sales order — meaning the order is neither fully invoiced nor cancelled — block the deletion and tell the user **which order number** is in the way so they can deal with it."*

This is one of the most common "first real CoC ticket" scenarios that lands in a developer's queue, and it is an excellent introduction to the chain-of-command pattern because:

- The required behaviour cannot be achieved by metadata alone
- The method to extend is a **boolean validation method**, which makes the chain semantics easy to reason about
- It demonstrates the correct way to **add** to standard validation rather than replace it

---

## 2. Why Chain of Command (and why not the alternatives)

When a developer first sees this requirement, three options come to mind. Walking through why two of them are wrong is more instructive than just stating the answer.

### Option A — Pre-event handler on `CustTable.delete()` ❌

A pre-event handler **fires before** the method runs, but in F&O the pre-handler on table `delete()` cannot cancel the operation by returning `false`. The delete proceeds regardless of what the handler does. This is a fundamental mismatch between intent ("stop the delete") and capability ("observe but not cancel").

### Option B — Post-event handler on `CustTable.delete()` ❌

By the time a post-event handler runs, the record has already been deleted. There is nothing to validate against, no record to keep, and no way to communicate failure back to the caller. This is too late.

### Option C — Chain of Command on `CustTable.validateDelete()` ✅

`validateDelete` is a **boolean-returning validation method** designed to be wrapped. Returning `false` from this method tells the framework to abort the deletion, and any messages emitted to the infolog during validation are surfaced to the user automatically.

CoC also gives access to:

- The full chain of other extensions (preserved by calling `next`)
- Standard's own validation logic (executed inside `next`)
- Protected and public methods/variables of the base object — something event handlers cannot reach

### The decision rule

> When a method **returns a boolean to signal validation success/failure**, prefer Chain of Command on that method over event handlers on the surrounding action.

This rule applies equally to `validateWrite`, `validateField`, `validateDelete`, and any custom validation method.

---

## 3. Why our custom check runs *before* `next` — and why that's correct here

This is the most important design decision in the scenario, and it is the **opposite** of what many CoC tutorials recommend as a default. The reasoning matters.

### The "after `next`" pattern (the common default)

The textbook CoC pattern is:

```xpp
boolean ret = next validateDelete();   // standard runs first
if (ret)                                // only check if standard approved
{
    // ...custom check, may set ret = false
}
return ret;
```

This is defensive: standard runs, and you only add stricter rules on top. It is the right pattern when **standard's validation is permissive enough** that your check actually gets a chance to run.

### Why "after `next`" fails for *this specific method*

Microsoft's standard `CustTable.validateDelete` is **aggressive**. It rejects the delete the moment it sees **any** related `SalesTable` record, regardless of status — Open, Delivered, Invoiced, or Cancelled. The standard message is the generic *"Transactions exist in table Sales orders"*.

If we run our check after `next`, the flow is:

```
next validateDelete()  →  standard finds a SalesTable record  →  ret = false
if (ret)               →  false, body skipped
return ret             →  false, with only standard's generic message
```

Our `select` never executes. The user never sees our specific, helpful "*Open sales order 000962*" message. The CoC technically works but is functionally invisible.

### The "before `next`" pattern — used here

```xpp
// 1. Run our query first so we know if there's an open SO
SalesTable salesTable;
select firstonly RecId, SalesId from salesTable
    where /* ... open status filter ... */;

// 2. Always call next exactly once (X++ rule)
ret = next validateDelete();

// 3. After next, override ret if we found an open SO
if (salesTable.RecId)
{
    ret = checkFailed(strFmt("[OHMS] ...", ...));
}

return ret;
```

What this gives us:

- **The `select` runs every time** — visible in the debugger, testable, demonstrable
- **`next` still runs unconditionally and exactly once** — satisfies the X++ compiler
- **Both messages can stack in the infolog** — standard's generic message *and* our specific one — giving the user more information, not less
- **`ret` ends up `false`** when our condition matches, which still cancels the delete

### The X++ rule that makes this design mandatory

The X++ compiler enforces:

> **The `next` call must execute exactly once, unconditionally. It cannot be inside an `if`, `while`, `try`, or any other block that might skip it.**

Compiler error if you violate this:
> *Call to 'next' should be done only once and unconditionally.*

This rules out the naive "early return if condition" version:

```xpp
// ❌ DOES NOT COMPILE
if (openSalesOrderExists)
{
    return checkFailed("...");   // skips next entirely
}
return next validateDelete();
```

The valid pattern is: do the work you need before `next`, call `next` once at the top level, then adjust `ret` afterward.

---

## 4. Implementation

### 4.1 Project setup

| Item               | Value                                          |
|--------------------|------------------------------------------------|
| Solution           | `Extensibility-Patterns`                       |
| Project            | `OHMS_Scenario01_BlockCustomerDelete`          |
| Model              | `OHMS`                                         |
| Layer              | `usr`                                          |
| Referenced packages| `ApplicationSuite`, `ApplicationPlatform`, `ApplicationFoundation`, `Directory` |

### 4.2 The extension class

File: `CustTable_OHMS_Extension.xpp`

```xpp
/// <summary>
/// Extension on CustTable that blocks customer deletion
/// when the customer has open (non-Invoiced, non-Cancelled) sales orders
/// and surfaces a specific message naming the offending order.
/// Scenario 01 of the Extensibility-Patterns repo.
/// </summary>
[ExtensionOf(tableStr(CustTable))]
final class CustTable_OHMS_Extension
{
    /// <summary>
    /// Wraps validateDelete to enforce the open-sales-order rule.
    /// </summary>
    /// <returns>
    /// true if deletion is allowed; false (with infolog message) otherwise.
    /// </returns>
    public boolean validateDelete()
    {
        boolean    ret;
        SalesTable salesTable;

        // Query first so the result is available regardless of what
        // standard validation decides. This guarantees our select
        // executes on every call, which makes debugging straightforward.
        select firstonly RecId, SalesId from salesTable
            where salesTable.CustAccount  == this.AccountNum
               && salesTable.SalesStatus  != SalesStatus::Invoiced
               && salesTable.SalesStatus  != SalesStatus::Canceled;

        // X++ requires next to be called exactly once and unconditionally.
        ret = next validateDelete();

        // Override ret with our specific failure if an open SO exists.
        // If standard already returned false, calling checkFailed adds
        // a second, more informative message to the infolog rather than
        // hiding standard's broader rejection reason.
        if (salesTable.RecId)
        {
            ret = checkFailed(strFmt(
                "[OHMS] Customer %1 cannot be deleted. Open sales order %2 exists. "
              + "Cancel or invoice all open orders before deleting the customer.",
                this.AccountNum,
                salesTable.SalesId));
        }

        return ret;
    }
}
```

### 4.3 Line-by-line commentary

| Line / construct                                | What it does and why it matters                                                                                                                                                          |
|--------------------------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `[ExtensionOf(tableStr(CustTable))]`             | Declares this class as an extension of `CustTable`. `tableStr` is a compile-time intrinsic — if `CustTable` were renamed in a future PU, the build fails loudly instead of silently breaking. |
| `final class`                                    | F&O requires extension classes to be `final`. They cannot be inherited, which keeps the chain deterministic.                                                                              |
| `public boolean validateDelete()`                | The signature **must match exactly** — same name, same return type, same parameter list. Default parameter values are omitted in the extension.                                          |
| `select firstonly RecId, SalesId from salesTable` | We only need to know whether *any* qualifying order exists, and to name one in the message. `firstonly` and selecting only `RecId, SalesId` (not `*`) is good practice from day one.    |
| `SalesStatus != Invoiced && != Canceled`         | "Open" is defined as not yet fully invoiced and not abandoned. `Backorder` and `Delivered` both still imply downstream work, so we treat them as open.                                  |
| `ret = next validateDelete();`                   | Calls the rest of the chain: any other extensions, then Microsoft's standard `validateDelete`. **Must be exactly once and unconditional.** Whatever the chain decides is captured in `ret`. |
| `if (salesTable.RecId)`                          | If our select found an open SO, override `ret` with our specific failure. `RecId` is non-zero only when a record was actually fetched, so this is the idiomatic "did we find anything?" test. |
| `checkFailed(strFmt(...))`                       | `checkFailed` writes the message to the infolog **and returns `false`** in a single call. It is the idiomatic X++ way to fail a validation. Always prefer it over `info(); return false;`. |
| `strFmt`                                         | Parameterised formatting. Never concatenate user-facing messages with `+` — it makes labels and translation fragile.                                                                     |
| `[OHMS]` prefix in the message                   | Development-time tag that makes our message visually distinguishable from standard messages in the infolog. Useful for proving "yes, my code fired." Remove the prefix before production. |
| `return ret;`                                    | Hands the final boolean back to the framework, which uses it to decide whether to proceed with the delete.                                                                               |

---

## 5. Functional verification

All testing uses the **USMF** legal entity (Contoso Entertainment Systems USA) and standard demo data.

### 5.1 Test setup — create a disposable customer

1. Switch to legal entity **USMF** (top-right company picker).
2. Navigate: **Modules → Accounts receivable → Customers → All customers**.
3. Click **+ New** and fill:
   - **Customer account:** `OHMS-T01`
   - **Name:** `OHMS Delete Test`
   - **Customer group:** `100` (or any valid group in your environment)
   - **Currency:** `USD`
   - **Site:** `1`
   - **Warehouse:** `13` (a warehouse with on-hand stock)
4. **Save & close**.

### 5.2 Test 1 — delete a clean customer (should succeed)

**Goal:** confirm the extension does not interfere with legitimate deletes.

1. On the customer list, select `OHMS-T01`.
2. Click **Delete** (or press the Delete key) and confirm.
3. **Expected:** the customer is deleted normally. Our `select` ran, found no records, `salesTable.RecId == 0`, `next` returned `true`, our `if` body did not execute, and `ret` stayed `true`.

### 5.3 Test 2 — delete a customer with an open sales order

**Goal:** confirm the new business rule fires and our specific message is shown.

1. Re-create `OHMS-T01` as in section 5.1.
2. Navigate: **Modules → Accounts receivable → Orders → All sales orders → + New**.
3. **Customer account:** `OHMS-T01`, accept defaults, **OK**.
4. Add one line: **Item number:** `1000` (or any item with on-hand stock at WH 13), **Quantity:** `1`. **Save**.
5. Note the SO number (e.g. `000XXX`). Leave the order in **Open order** status — do not confirm, pick, pack, or invoice.
6. Return to **All customers**, select `OHMS-T01`, click **Delete**.

**Expected — both messages appear stacked in the infolog:**

> *The record cannot be deleted. Transactions exist in table Sales orders.* (standard)
>
> *[OHMS] Customer OHMS-T01 cannot be deleted. Open sales order 000XXX exists. Cancel or invoice all open orders before deleting the customer.* (ours)

The standard message is fired by Microsoft's `validateDelete` inside `next`. Our message is fired by `checkFailed` in the `if` block after `next`. Both contribute to `ret = false`, and the delete is cancelled. The user gets **more useful information** than they would with standard alone — they now know exactly which SO to fix.

### 5.4 Debugger verification — proving the select runs

This is the experiment that puts to bed any doubt about whether our code is actually executing.

1. In Visual Studio, open `CustTable_OHMS_Extension.xpp`.
2. Set breakpoints on:
   - `select firstonly RecId, SalesId from salesTable`
   - `ret = next validateDelete();`
   - `if (salesTable.RecId)`
   - `ret = checkFailed(...)`
3. **Debug → Attach to Process**.
4. Tick **Show processes from all users**.
5. Select `w3wp.exe` (the AOS process).
6. Click **Attach**.
7. In the browser, attempt the delete on `OHMS-T01` (the one with the open SO).

**What you will observe:**

| Step | Action                                  | Observation                                                                 |
|------|-----------------------------------------|-----------------------------------------------------------------------------|
| 1    | Breakpoint hits on the `select`         | Our extension is invoked.                                                  |
| 2    | F10 over the `select`                   | Hover `salesTable` — `RecId` is non-zero, `SalesId` shows the order number. |
| 3    | F10 onto `ret = next validateDelete();` | We are at the `next` call.                                                 |
| 4    | F10 over `next`                         | Standard runs, infolog gains the *"Transactions exist..."* message. `ret = false`. |
| 5    | F10 onto `if (salesTable.RecId)`        | We did find a record, so the body executes.                                |
| 6    | F10 over `checkFailed`                  | Infolog gains our `[OHMS]` message. `ret` is reassigned to `false`.        |
| 7    | F10 to `return ret;`                    | We exit returning `false`. Delete is cancelled.                            |

**Key debugger keys:**

| Key            | Action       | When to use                                                                    |
|----------------|--------------|-------------------------------------------------------------------------------|
| **F10**        | Step over    | Run the next line; do not dive into method calls.                             |
| **F11**        | Step into    | Dive into the called method — useful on the `next` line to step into standard. |
| **Shift+F11**  | Step out     | You stepped too deep — climb back up one level.                               |

Try **F11** on the `next validateDelete()` line at least once. You will descend into Microsoft's standard `validateDelete` and watch its checks run. This is the single best way to internalise what `next` actually does.

### 5.5 Test 3 — confirm the rule does not over-block

1. Take a customer whose only sales orders are fully invoiced (or use `OHMS-T01` from section 5.3 after invoicing the order through Confirm → Pack → Invoice).
2. Try to delete the customer.

**Expected:** our custom message no longer appears (the SO is invoiced, so the `select` finds nothing — `salesTable.RecId == 0` — and the `if` body is skipped). Standard may still block the delete because of posted transactions on the customer ledger, and that is the correct, desired behaviour.

---

## 6. Common gotchas

| Symptom                                                          | Cause                                                                                            | Fix                                                                                  |
|------------------------------------------------------------------|--------------------------------------------------------------------------------------------------|--------------------------------------------------------------------------------------|
| Compile error: *"Call to 'next' should be done only once and unconditionally."* | `next` is inside an `if`, `return` happens before `next`, or `next` appears twice                      | Restructure: do work, call `next` once at the top level, then adjust `ret` afterward. |
| Build error: *"The name CustTable does not denote..."*           | Model is missing reference to `ApplicationSuite`                                                 | Dynamics 365 → Model Management → Update model parameters → add `ApplicationSuite`.  |
| Extension does not fire after build                              | AOS still running old assembly                                                                   | Restart **World Wide Web Publishing Service** in `services.msc`, or use VS → Restart IIS Express. |
| Infolog message does not appear                                  | Notification surfaced as a toast and dismissed                                                   | Click the bell icon in the top-right or look for the red strip across the form.     |
| `checkFailed` not recognised                                     | Mistyped — it is camelCase: `checkFailed`                                                        | Correct the casing.                                                                  |
| Only standard's message appears, not ours                        | The customer has no open SO matching our filter (status is Invoiced/Cancelled, or no SO at all)  | Create a SO and leave it in `Open order` status. See section 5.3.                    |

---

## 7. What this scenario teaches

By the end of this scenario you should be comfortable with:

- The structure of a Chain of Command class (`[ExtensionOf]`, `final class`, matching signatures)
- The semantics of `next` — what runs before, what runs after
- The X++ rule that **`next` must be called exactly once and unconditionally**
- When **before-`next`** is the correct placement, even though "after `next`" is the textbook default
- The difference between `info()` + `return false` and `checkFailed()`
- How to make custom infolog messages visually distinguishable with a `[OHMS]` tag during development
- Using `tableStr`, `classStr`, and friends instead of magic strings
- Attaching the Visual Studio debugger to AOS to step through CoC chains, and using F10 / F11 / Shift+F11 effectively

These mental models carry directly into Scenarios 02 onward, where the same patterns apply to forms, datasources, and class methods.

---

## 8. References

- [Microsoft Learn — Class extensions and Chain of Command](https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/extensibility/method-wrapping-coc)
- [Microsoft Learn — Naming guidelines for extensions](https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/extensibility/naming-guidelines-extensions)
- [Microsoft Learn — Customise through extension and overlayering](https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/extensibility/customization-overlayering-extensions)
