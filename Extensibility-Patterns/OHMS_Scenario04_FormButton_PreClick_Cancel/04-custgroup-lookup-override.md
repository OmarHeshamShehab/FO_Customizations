# Scenario 04 — Override the Customer Group lookup on the CustTable form

**Project:** `OHMS_Scenario04_CustGroup_LookupOverride`
**Pattern:** Form control event handler on the `Lookup` event with `CancelSuperCall`
**Form:** `CustTable`
**Control:** `Posting_CustGroup` (the Customer group field on the General fast tab)

---

## What's in this project

| Artifact | Type | Purpose |
|---|---|---|
| `CustTable_OHMS_LookupHandlers` | X++ class (event handler) | Subscribes to the `Lookup` event of the `Posting_CustGroup` control and renders a custom 3-column lookup using `SysTableLookup` |

That's the entire project — one class, one method. No metadata changes.

---

## 1. Business problem

The standard customer group dropdown on the customer form shows only two columns: **Customer group** and **Description**. AR users want a third column showing the **Terms of payment** so they can pick a customer group and immediately see what payment terms it implies — without opening the customer group setup form to check.

The requirement: extend the standard lookup to add the **Terms of payment** column without touching standard code.

---

## 2. Why event handler on `Lookup` (and why this is the textbook D365 pattern)

When extending lookup behavior on a standard form, X++ exposes three competing options. Walking through each is more instructive than just stating the answer.

### Option A — Chain of Command on the form datasource ❌

CoC on form datasource methods works for `init`, `active`, `validateWrite`, etc. — but lookup logic on a standard field is not exposed as an extendable method on the datasource. You can't wrap it with `next`.

### Option B — Override the lookup method via `registerOverrideMethod` ⚠️

Possible — uses CoC on the form's `init` method to call `registerOverrideMethod` and bind a custom lookup method. Works but is verbose: requires CoC on the form, an `init` extension that respects `next`, and a separate method definition.

### Option C — `FormControlEventHandler` on `FormControlEventType::Lookup` ✅

The control's `Lookup` event fires when the user clicks the dropdown arrow on the field. An event handler on this event:
- Receives the control as `sender` so we can pass it to `SysTableLookup`
- Receives `e` as a `FormControlCancelableSuperEventArgs` — meaning we can cancel the standard lookup that would otherwise also open
- Requires no CoC, no form extension, no method binding

This is the cleanest, most-documented pattern and is the standard answer to "override a lookup on a standard form" in D365.

### The decision rule

> When you need to replace or augment a lookup on a standard form, prefer `FormControlEventHandler` on `Lookup` with `CancelSuperCall()` over CoC-based approaches.

---

## 3. The code

```xpp
/// <summary>
/// Form control event handler that overrides the Lookup event of the
/// Posting_CustGroup field on the CustTable form.
///
/// Replaces the default 2-column lookup with a 3-column lookup adding
/// the Payment Terms column for context.
///
/// Scenario 04 of the Extensibility-Patterns repo.
/// </summary>
public class CustTable_OHMS_LookupHandlers
{
    [FormControlEventHandler(formControlStr(CustTable, Posting_CustGroup),
                             FormControlEventType::Lookup)]
    public static void Posting_CustGroup_OnLookup(FormControl sender,
                                                  FormControlEventArgs e)
    {
        info('[OHMS] Posting_CustGroup custom lookup fired');

        SysTableLookup sysTableLookup = SysTableLookup::newParameters(
            tableNum(CustGroup), sender);

        // Add three columns to the lookup (standard shows only the first two)
        sysTableLookup.addLookupfield(fieldNum(CustGroup, CustGroup));
        sysTableLookup.addLookupfield(fieldNum(CustGroup, Name));
        sysTableLookup.addLookupfield(fieldNum(CustGroup, PaymTermId));

        sysTableLookup.performFormLookup();

        // Cancel the standard super lookup to prevent a duplicate form opening.
        FormControlCancelableSuperEventArgs cancelArgs = e as FormControlCancelableSuperEventArgs;
        if (cancelArgs)
        {
            cancelArgs.CancelSuperCall();
        }
    }
}
```

### Code commentary

| Construct | Purpose |
|---|---|
| `public class` (no `final`, no `[ExtensionOf]`) | Plain class containing static handler methods. Not a CoC extension class. |
| `[FormControlEventHandler(formControlStr(CustTable, Posting_CustGroup), FormControlEventType::Lookup)]` | Subscribes the method to the `Lookup` event of the `Posting_CustGroup` control on the `CustTable` form. The intrinsic `formControlStr` takes two arguments: form name and control name. |
| `public static void` | Event handler methods MUST be static. |
| `FormControl sender` | The control on which the lookup was triggered. We pass this directly to `SysTableLookup` so the lookup form anchors correctly under the dropdown arrow. |
| `FormControlEventArgs e` | The event arguments. We cast it to `FormControlCancelableSuperEventArgs` later to access the cancellation API. |
| `SysTableLookup::newParameters(tableNum(CustGroup), sender)` | Initializes a custom lookup. First parameter is the backing table (`CustGroup`). Second parameter is the control that triggered the lookup. |
| `addLookupfield(fieldNum(CustGroup, ...))` | Each call adds one column to the lookup grid. Order matters — the first field added becomes the value returned to the caller control when the user picks a row. Standard shows two columns; we add a third (`PaymTermId`). |
| `performFormLookup()` | Renders and runs the lookup. The lookup form opens immediately under the dropdown arrow. |
| `e as FormControlCancelableSuperEventArgs` | Cast the base event args to the cancellable variant. This is the only way to access `CancelSuperCall()`. |
| `cancelArgs.CancelSuperCall()` | Suppresses the standard kernel-driven lookup. Without this call, BOTH the custom lookup and the standard lookup attempt to open, and D365 raises *"More than one form was opened at once for the lookup control"*. |

### Why `CancelSuperCall()` is non-negotiable

In other patterns we've used in this repo (table CoC `validateDelete` for example), the chain naturally orders standard logic via `next`. With form control events, both the handler AND the kernel's standard lookup pipeline run independently unless we explicitly suppress one. Skipping `CancelSuperCall()` produces a runtime error within seconds of clicking the dropdown.

---

## 4. How to deploy and test in USMF

### Prerequisites

- Local OneBox or Tier-1 dev VM with D365 F&O developer tools.
- USMF legal entity (Contoso Entertainment Systems USA).
- Administrator rights on the VM.

### Deployment

1. Open Visual Studio as Administrator.
2. Open `Extensibility-Patterns.sln`.
3. Right-click project `OHMS_Scenario04_CustGroup_LookupOverride` → **Build**.
4. Confirm `Build: 1 succeeded` in the Output window.
5. PowerShell as Administrator → run `iisreset`. Wait for *"Internet services successfully restarted."*

> No database synchronization required. This scenario adds no fields, no tables, no metadata that affects SQL — just one class.

### Test 1 — Custom lookup with three columns

1. Browser → confirm USMF in the top-right company picker.
2. **Modules → Accounts receivable → Customers → All customers**.
3. Open any customer (e.g. `OHMS-T05`).
4. Locate the **Customer group** field on the General fast tab.
5. Click the dropdown arrow on the field.

**Expected:**
- Top of screen, infolog message: `[OHMS] Posting_CustGroup custom lookup fired`
- Lookup opens under the field showing **three columns**:
  - Customer group (e.g. `100`, `20`, `30`, `40`, `80`, `90`)
  - Description (e.g. *Intercompany retail customers*, *Major customers*, *Retail customers*, *Internet customers*, *Other customers*, *Intercompany customers*)
  - Terms of payment (e.g. `Net10`, `Net30`)

### Test 2 — Pick a value

1. Click any row in the lookup (e.g. group `30 — Retail customers — Net10`).
2. **Expected:** dropdown closes, the field is populated with `30`. The other two columns were for display only — only the first column (`CustGroup`) is written back into the control.

### Test 3 — Confirm `CancelSuperCall` matters

If you want to see why `CancelSuperCall()` is essential:

1. Comment out the `cancelArgs.CancelSuperCall()` line.
2. Save → Build → `iisreset`.
3. Click the dropdown.
4. **Expected error:** *"More than one form was opened at once for the lookup control."* The standard lookup tries to open at the same time as ours.
5. Restore the line and rebuild.

This experiment is worth doing once. It makes the role of `CancelSuperCall()` concrete.

---

## 5. Common gotchas

| Symptom | Cause | Fix |
|---|---|---|
| Standard 2-column lookup still appears | Build didn't deploy | Run `iisreset`; if still wrong, full rebuild via Dynamics 365 → Build models. |
| *"More than one form was opened at once for the lookup control"* | Forgot `CancelSuperCall()`, or the cast `e as FormControlCancelableSuperEventArgs` returned null and the if-guard skipped | Confirm `CancelSuperCall()` is reached. The cast should normally succeed for `Lookup` events. |
| Method doesn't fire at all | Wrong control name in `formControlStr(...)` | The control on this form is `Posting_CustGroup` (verified). Not `CustGroup`. The form can have multiple controls bound to the same field. |
| Lookup appears but only shows one column | Used `addLookupfield(_, true)` with the `true` flag (which selects only that column) | Drop the second parameter or pass `false`. The verified pattern omits it. |
| First column in lookup is not what gets written back | Field order wrong — the **first** `addLookupfield` becomes the return value | Make sure the column you want returned is added first (here: `CustGroup`). |

---

## 6. What this scenario teaches

By reading and running this project you should now be comfortable with:

- The `FormControlEventHandler` attribute and the `Lookup` event type
- The `formControlStr(FormName, ControlName)` two-argument intrinsic
- Building a custom lookup with `SysTableLookup::newParameters` and `addLookupfield`
- Why the **first column added** becomes the value written back to the calling control
- The role of `FormControlCancelableSuperEventArgs.CancelSuperCall()` when both kernel-driven and event-handler-driven flows would otherwise compete
- When event handlers are preferred over CoC: pure cancellation/replacement scenarios where there's no `next`-based chain on the standard side

---

## 7. References

- [Dynamics 365 Musings — How To Override An Existing Lookup Method: Event Handler](https://dynamics365musings.com/override-an-existing-lookup-method-event-handler/)
- [Stoneridge Software — Use Event Handlers to Override a Form Control Lookup Method](https://stoneridgesoftware.com/use-event-handlers-to-override-a-form-control-lookup-method-in-dynamics-365-finance-and-operations/)
- [Microsoft Learn — Lookup controls](https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/user-interface/lookups-controls)
