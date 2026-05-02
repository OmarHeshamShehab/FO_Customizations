# Scenarios 02 — CustTable Customizations

**Project:** `OHMS_Scenario02_CustTable_Customizations`
**Patterns:** Chain of Command (form datasource) + Event Handler (form data field)
**Form extended:** `CustTable`
**Field added:** `OHMSCommunicationPreference`

This project bundles two related customizations against the **CustTable** form because X++ allows only one extension element per base object per model. Rather than fight that constraint, real implementations group related work on the same form into a single project — which is what we do here.

---

## What's in this project

| Artifact | Type | Purpose |
|---|---|---|
| `CustTable.OHMS` | Table extension | Adds the `OHMSCommunicationPreference` string field to the `CustTable` table |
| `CustTable.OHMS` | Form extension | Adds the field to the Administration group on the customer form |
| `CustTableForm_CustTable_OHMS_Extension` | CoC class | Defaults the field value based on customer group when a record becomes active |
| `CustTable_OHMS_FieldHandlers` | Event handler class | Prompts for confirmation when the user edits the field, reverts on decline |

---

## Why two scenarios in one project

| Scenario | Pattern | What it does |
|---|---|---|
| **02 — Default Communication Preference** | CoC on form datasource `active()` | When a customer record becomes active in the form and the field is empty, default a value based on the customer's group |
| **03 — Manager Approval on Change** | Event handler on field `Modified` | When a user edits the Communication preference field, prompt with a confirmation dialog. If declined, revert the change |

Together they show that a single form often needs both **proactive defaulting** (set values) and **reactive validation** (control changes), and that the right tool differs for each.

---

# Section 1 — Scenario 02: Default Communication Preference

## Business problem

When the AR team works with customers in USMF, the **Communication preference (OHMS)** field should never be blank. The default communication channel should be set automatically based on the customer's customer group:

- Group `10` → `[OHMS] Direct phone`
- Group `20` → `[OHMS] Email - bulk`
- Any other group → `[OHMS] Standard email`

The user can override the value, but it's never empty.

## Why CoC on `active()`

`active()` is the form datasource method that fires every time a record becomes the current record on the datasource — when the user opens or navigates to a customer.

| Why this method works for defaulting | |
|---|---|
| Fires reliably regardless of how the record was created | The CustTable form has multiple entry points (quick-create dialog, data entity import, list navigation). `active()` runs in all of them. |
| Combined with an empty-field guard, it's idempotent | The guard `if (!custTable.OHMSCommunicationPreference)` ensures the assignment only happens when needed and doesn't disturb existing values. |
| Returns `int` so chain semantics are clean | `int ret = next active(); ... return ret;` is the textbook CoC wrap. |

## The code

```xpp
[ExtensionOf(formDataSourceStr(CustTable, CustTable))]
final class CustTableForm_CustTable_OHMS_Extension
{
    public int active()
    {
        // 1. Run the standard active logic
        int ret = next active();

        // 2. Get the current record
        CustTable custTable = this.cursor();

        // 3. Trigger logic if the field is currently empty
        if (!custTable.OHMSCommunicationPreference)
        {
            switch (custTable.CustGroup)
            {
                case '10':
                    custTable.OHMSCommunicationPreference = '[OHMS] Direct phone';
                    break;
                case '20':
                    custTable.OHMSCommunicationPreference = '[OHMS] Email - bulk';
                    break;
                default:
                    custTable.OHMSCommunicationPreference = '[OHMS] Standard email';
                    break;
            }
        }

        return ret;
    }
}
```

## Code commentary

| Construct | Purpose |
|---|---|
| `[ExtensionOf(formDataSourceStr(CustTable, CustTable))]` | Targets the CustTable datasource on the CustTable form. The intrinsic takes two arguments: form name, datasource name. |
| `final class` | Required for all CoC extension classes — they cannot be inherited. |
| `public int active()` | Signature must match the base method exactly: same name, same return type, same parameters. |
| `int ret = next active();` | `next` must be called exactly once and unconditionally — the X++ compiler enforces this. We capture standard's return value to pass through unchanged. |
| `this.cursor()` | On a form datasource, `this` is the datasource object (not a record). `cursor()` returns the current record as a typed buffer. |
| `if (!custTable.OHMSCommunicationPreference)` | Guard: only default when the field is empty. Existing values are preserved. |
| `return ret;` | Return standard's value untouched — we observe and supplement, not replace. |

## Trade-off

`active()` runs every time a record activates, which means the assignment evaluates on every form open. This is cheap because the empty-field guard short-circuits after the value is set once. The trade-off is acceptable in exchange for catching every entry path into the form.

---

# Section 2 — Scenario 03: Manager Approval on Change

## Business problem

The Communication preference field affects how Sales/Marketing reach customers. Changing it should not be casual. When a user edits the field on an existing customer:

1. Prompt them with a Yes/No dialog showing the FROM and TO values
2. If they confirm → log the change to the infolog for audit
3. If they decline → revert the field to its previous value

This is the standard pattern for any sensitive field change in D365: credit limits, tax groups, blocked status, payment terms.

## Why event handler (not CoC)

| Reason | Detail |
|---|---|
| **Pure observation** | We're reacting to a value change, not modifying any method's behavior |
| **No return value to alter** | Field `Modified` is `void` — nothing to wrap and return |
| **No chain to participate in** | We don't need ordering relative to other extensions |
| **Field-level events are reliable** | Field `Modified` fires whenever the user actually edits a bound field |
| **Loose coupling** | The form/field knows nothing about us — we subscribe transparently |

## The code

```xpp
public class CustTable_OHMS_FieldHandlers
{
    [FormDataFieldEventHandler(formDataFieldStr(CustTable, CustTable, OHMSCommunicationPreference),
                               FormDataFieldEventType::Modified)]
    public static void OHMSCommunicationPreference_OnModified(FormDataObject sender,
                                                              FormDataFieldEventArgs e)
    {
        info('[OHMS] OnModified fired');

        FormDataSource dataSource = sender.datasource();
        CustTable      custTable  = dataSource.cursor();
        CustTable      origRecord = custTable.orig();

        str oldValue = origRecord.OHMSCommunicationPreference;
        str newValue = custTable.OHMSCommunicationPreference;

        // Don't prompt on initial defaulting (when old value was empty).
        // Only prompt on a real change to a non-empty new value.
        if (oldValue && oldValue != newValue)
        {
            str promptText = strFmt(
                "[OHMS] You are changing the Communication preference for customer %1.\n\n"
              + "From: %2\n"
              + "To:   %3\n\n"
              + "This change requires manager approval. Continue?",
                custTable.AccountNum,
                oldValue,
                newValue);

            if (Box::yesNo(promptText, DialogButton::No) == DialogButton::Yes)
            {
                info(strFmt("[OHMS] Communication preference change accepted for %1: '%2' -> '%3'",
                            custTable.AccountNum, oldValue, newValue));
            }
            else
            {
                // User declined: revert the buffer to the original value.
                custTable.OHMSCommunicationPreference = oldValue;

                // Tell the form to refresh so the UI shows the reverted value.
                dataSource.refresh();

                info(strFmt("[OHMS] Communication preference change cancelled for %1. Value reverted to '%2'.",
                            custTable.AccountNum, oldValue));
            }
        }
    }
}
```

## Code commentary

| Construct | Purpose |
|---|---|
| `public class` (no `final`, no `[ExtensionOf]`) | Plain class containing static handler methods. Different from a CoC extension class. |
| `[FormDataFieldEventHandler(...)]` | Subscribes the method to a specific field event |
| `formDataFieldStr(CustTable, CustTable, OHMSCommunicationPreference)` | Three-argument intrinsic: form, datasource, field |
| `FormDataFieldEventType::Modified` | Fires when the user edits the bound field and tabs out (commits the change to the buffer) |
| `public static void` | Event handler methods MUST be static — they don't belong to a specific instance |
| `FormDataObject sender` | Sender type for field-level events. Datasource events use `FormDataSource`; control events use specific control types. |
| `sender.datasource()` | Walks back from the field event to the parent datasource |
| `custTable.orig()` | Returns the record as it was before the current edit session — the FROM value for our prompt |
| `Box::yesNo(...)` | Modal Yes/No dialog. Second parameter sets the default button — we choose `No` to prevent accidental confirmation |
| `if (oldValue && ...)` | Guard: don't prompt when transitioning from empty to a value — that's not a "change" worth approving |
| `dataSource.refresh()` | Forces the form to redraw from the buffer so the user sees the reverted value |

## Why `orig()` matters

`orig()` returns the record state from the database. `cursor()` returns the in-memory state. Comparing the two is how you detect what actually changed in the user's session. Without `orig()`, you'd have no way of knowing the prior value — it would already be replaced in `cursor()` by the time the handler fires.

This pattern is reusable for any "what changed?" scenario across D365.

---

# How to deploy and test in USMF

## Prerequisites

- VM with D365 F&O developer environment (any recent platform update)
- Administrator rights on the VM
- Logged into USMF (Contoso Entertainment Systems USA)

## Deployment

1. Open Visual Studio as Administrator on the VM.
2. Open the solution `Extensibility-Patterns.sln`.
3. Right-click the project `OHMS_Scenario02_CustTable_Customizations` → **Build**.
4. Confirm `Build: 1 succeeded` in the Output window.
5. **Dynamics 365 → Synchronize database → Synchronize**. (Required because we have a table extension.)
6. Wait for "Database synchronization complete."
7. Open PowerShell as Administrator and run `iisreset`. Wait for "Internet services successfully restarted."

> **Why iisreset:** IIS holds the previous compiled assembly in memory. Even after a successful build, the running AOS process won't pick up the new code until the worker process recycles. `iisreset` is the most reliable way to force this on a dev VM. Skipping this step is the #1 cause of "my changes aren't appearing" confusion.

## Test 1 — Defaulting (Scenario 02)

**Goal:** prove the field gets a value automatically.

1. Browser → log in → confirm USMF in the top-right company picker.
2. **Modules → Accounts receivable → Customers → All customers**.
3. Open any existing customer whose **Communication preference (OHMS)** field is blank.
4. Scroll to **Miscellaneous details → Communication preference (OHMS)**.

   **Expected:** the field shows a value (`[OHMS] Direct phone`, `[OHMS] Email - bulk`, or `[OHMS] Standard email`) based on the customer's group.

   The value was assigned by the `active()` CoC running when the form opened the record.

5. Save the customer. The defaulted value persists in the database from this point.

## Test 2 — Manager approval prompt accepted (Scenario 03)

**Goal:** prove the dialog appears and accepting commits the change.

1. Open a customer where the field has a value (any from Test 1).
2. Click into **Communication preference (OHMS)**.
3. Delete the existing text. Type a new value (e.g., `Test approval`).
4. Press Tab or click on another field.

   **Expected:** the infolog shows `[OHMS] OnModified fired`, then a modal dialog appears showing:
   > [OHMS] You are changing the Communication preference for customer XXX.
   > From: [previous value]
   > To: Test approval
   > This change requires manager approval. Continue?

5. Click **Yes**.

   **Expected:** dialog closes. Infolog shows:
   > [OHMS] Communication preference change accepted for XXX: '...' -> 'Test approval'

6. Save. The new value persists.

## Test 3 — Manager approval prompt declined (Scenario 03)

**Goal:** prove declining reverts the change.

1. Open the customer from Test 2.
2. Edit the Communication preference field again. Type a different value.
3. Tab out.
4. When the dialog appears, click **No**.

   **Expected:** dialog closes. The field visibly reverts to its previous value. Infolog shows:
   > [OHMS] Communication preference change cancelled for XXX. Value reverted to '...'

5. Save. The original value is preserved.

## Test 4 — Initial defaulting does not trigger the prompt

**Goal:** prove the prompt only fires on real changes, not on the initial default.

1. Find or create a customer where **Communication preference (OHMS)** is empty.
2. Open it.

   **Expected:** the `active()` CoC defaults the value silently. No prompt appears because the `if (oldValue && ...)` guard skips when the prior value was empty.

3. Now edit the field. The prompt appears as expected.

---

# Known issues and gotchas

## Customer group 10 sales restriction in Contoso demo data

Contoso USMF includes a demo restriction:
> *Sales orders for customer group 10 are not allowed in this demo.*

This affects **sales-order creation**, not our customer-level field defaulting. The `case '10'` branch in the CoC still fires correctly when you open a group-10 customer; you just can't create sales orders for those customers in demo data. For end-to-end testing involving sales-order interactions, use customers in groups 20, 30, or others.

## `iisreset` is not optional

After every X++ build, run `iisreset` before testing. This is the most common cause of confusion on dev VMs.

## `formDataFieldStr` requires three arguments

`formDataFieldStr(FormName, DataSourceName, FieldName)` — easy to confuse with `formDataSourceStr` (two args). Get the count right the first time; the compile error if you don't is unhelpful.

## Dialog default button matters

`Box::yesNo(text, DialogButton::No)` makes **No** the default. For destructive or sensitive operations, always default to the safer choice. A user who hits Enter expecting to dismiss the dialog should not accidentally approve.

---

# What this project teaches

By reading and running this project you should now be comfortable with:

- Wrapping a CoC method that returns `int` — `int ret = next active(); ... return ret;`
- The signature differences between `FormDataSourceEventHandler` and `FormDataFieldEventHandler`
- Using `this.cursor()` on a form datasource extension to access the current record
- Walking from a field event back to the datasource via `sender.datasource()`
- Using `orig()` to detect "what changed?" in field handlers
- Using `Box::yesNo` for in-form confirmation dialogs with safe default buttons
- Reverting a buffer change and refreshing the datasource
- Why event handlers are preferred over CoC for pure-observation patterns
- Why a single form often needs both CoC and event handlers working together

---

# References

- [Microsoft Learn — Method wrapping and Chain of Command](https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/extensibility/method-wrapping-coc)
- [Microsoft Learn — Customise forms through extension](https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/user-interface/customize-model-elements-extensions)
- [Microsoft Learn — Naming guidelines for extensions](https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/extensibility/naming-guidelines-extensions)
