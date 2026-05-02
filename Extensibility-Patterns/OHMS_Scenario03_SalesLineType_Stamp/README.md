# Scenario 03 — Class CoC and Event Handlers on `SalesLineType`

**Project:** `OHMS_Scenario03_SalesLineType_Stamp`
**Class extended:** `SalesLineType` (AOT → Code → Classes)
**Method extended:** `initFromSalesTable()`
**Patterns demonstrated:** Chain of Command, Pre-event handler, Post-event handler

This project is the first in the repo to extend a true X++ **class** (not a table or form). It also demonstrates all three ways the same standard method can be extended in D365, side-by-side, in one project.

---

## What's in this project

| Artifact | Type | Role |
|---|---|---|
| `SalesLine.OHMS` | Table extension | Adds `OHMSCommunicationPreference` (string, 255) to the `SalesLine` table |
| `SalesTable.OHMS` | Form extension | Adds the new field as a column on the `SalesLineGrid` of the `SalesTable` form |
| `SalesLineType_OHMS_Extension` | CoC class | Wraps `SalesLineType.initFromSalesTable()` and stamps the customer's `OHMSCommunicationPreference` onto the new line |
| `SalesLineType_OHMS_EventHandlers` | Event handler class | Pre and Post handlers on the same `initFromSalesTable()` method that log to the infolog before and after standard runs |

---

## Section 1 — Business problem

When a sales line is added to a sales order, the line should automatically inherit the customer's `OHMSCommunicationPreference` value (set by the customizations in Scenario 02). The user shouldn't have to copy this value manually onto each line.

Standard D365 already copies a long list of header fields onto every new sales line (CustAccount, CustGroup, Currency, DlvMode, DlvTerm, payment terms, tax group, etc.) inside the method `SalesLineType.initFromSalesTable()`. We extend that same method to add our custom field to the copy operation.

---

## Section 2 — Why CoC on `SalesLineType.initFromSalesTable()`

`SalesLineType` is the **helper class** that contains the business logic for sales line operations. The pattern of having a `<TableName>Type` class is used throughout D365 (`SalesLineType`, `SalesTableType`, `PurchLineType`, `CustTableType`, etc.). When standard code creates or modifies a sales line, it routes through this class.

`initFromSalesTable()` is the single method called whenever a sales line needs to inherit values from its parent header. Hooking here means:

- The stamp happens at exactly the right moment, alongside Microsoft's own header→line copies
- The parent SalesTable is passed as a parameter — no extra lookups needed
- Any future Microsoft additions to the standard copy operation automatically run before our stamp because we call `next` first

---

## Section 3 — The CoC implementation

```xpp
[ExtensionOf(classStr(SalesLineType))]
final class SalesLineType_OHMS_Extension
{
    public void initFromSalesTable(SalesTable _salesTable, boolean _ignoreInventDim)
    {
        info('[OHMS] SalesLineType.initFromSalesTable CoC fired');

        next initFromSalesTable(_salesTable, _ignoreInventDim);

        CustTable custTable = CustTable::find(_salesTable.CustAccount);

        if (custTable.RecId)
        {
            this.parmSalesLine().OHMSCommunicationPreference =
                custTable.OHMSCommunicationPreference;
        }
    }
}
```

### Code commentary

| Construct | Purpose |
|---|---|
| `[ExtensionOf(classStr(SalesLineType))]` | Targets the `SalesLineType` X++ class. `classStr` is the single-argument intrinsic for class targets — different from `tableStr` (table) and `formDataSourceStr` (form datasource). |
| `final class` | Required for all CoC extension classes — they cannot be inherited. |
| `public void initFromSalesTable(SalesTable _salesTable, boolean _ignoreInventDim)` | Signature must match the base method exactly. The default value (`_ignoreInventDim = false`) is OMITTED in the extension — X++ rule. |
| `next initFromSalesTable(...)` | Must be called exactly once and unconditionally. Called BEFORE our logic so all standard header→line copies happen first. |
| `CustTable::find(...)` | Standard X++ pattern — `::find()` is the universal "fetch by primary key" static method on tables. |
| `this.parmSalesLine()` | Public getter on `SalesLineType` that returns the `SalesLine` record being initialized. (Note: there is **no** `salesLine()` method — the protected member is exposed via the `parm` prefix accessor.) |
| `this.parmSalesLine().OHMSCommunicationPreference = ...` | Direct assignment to the line buffer. Since this happens during the initialization phase, the value will be part of the same insert when standard eventually saves the line. |

---

## Section 4 — The event handler implementation

```xpp
public class SalesLineType_OHMS_EventHandlers
{
    [PreHandlerFor(classStr(SalesLineType), methodStr(SalesLineType, initFromSalesTable))]
    public static void SalesLineType_Pre_initFromSalesTable(XppPrePostArgs args)
    {
        SalesTable salesTable = args.getArg('_salesTable') as SalesTable;

        info(strFmt("[OHMS] PRE handler: about to initialize sales line for customer %1 (SO %2)",
                    salesTable.CustAccount,
                    salesTable.SalesId));
    }

    [PostHandlerFor(classStr(SalesLineType), methodStr(SalesLineType, initFromSalesTable))]
    public static void SalesLineType_Post_initFromSalesTable(XppPrePostArgs args)
    {
        SalesLineType salesLineType = args.getThis() as SalesLineType;
        SalesLine     salesLine     = salesLineType.parmSalesLine();

        info(strFmt("[OHMS] POST handler: sales line initialized. Item=%1, CommunicationPreference=%2",
                    salesLine.ItemId ? salesLine.ItemId : 'not yet set',
                    salesLine.OHMSCommunicationPreference ? salesLine.OHMSCommunicationPreference : '(empty)'));
    }
}
```

### Code commentary

| Construct | Purpose |
|---|---|
| `public class` (no `final`, no `[ExtensionOf]`) | Plain class containing static handler methods. Different from a CoC extension class. |
| `[PreHandlerFor(classStr(...), methodStr(...))]` | Subscribes the method to fire BEFORE the named class method. |
| `[PostHandlerFor(classStr(...), methodStr(...))]` | Subscribes the method to fire AFTER the named class method (and after any CoC extensions). |
| `public static void` | Event handler methods MUST be static — they don't belong to an instance. |
| `XppPrePostArgs args` | Carrier object that gives access to: the calling instance (`getThis()`), the method's parameters (`getArg(name)`), the cancellation flag, and the return value (post-handlers only). |
| `args.getArg('_salesTable') as SalesTable` | Retrieves the original `_salesTable` parameter that was passed to the standard method. The `as` cast is required because `getArg` returns `anytype`. |
| `args.getThis() as SalesLineType` | Returns the `SalesLineType` instance whose method just ran. From there we use the same `parmSalesLine()` getter as the CoC class. |

---

## Section 5 — The three patterns compared

The same method (`SalesLineType.initFromSalesTable`) can be extended three different ways. All three coexist in this project on the same target method without conflict.

| | Chain of Command | Pre-event handler | Post-event handler |
|---|---|---|---|
| **Class declaration** | `[ExtensionOf(classStr(...))]` + `final class` | Plain `public class` | Plain `public class` |
| **Method binding** | Same-named method using `next` keyword | `[PreHandlerFor(...)]` attribute | `[PostHandlerFor(...)]` attribute |
| **Method modifier** | Instance method | Must be `public static` | Must be `public static` |
| **Runs relative to standard** | Wraps it (before AND after via `next` placement) | Strictly before | Strictly after |
| **Can read parameters** | Yes — directly | Yes — via `args.getArg()` | Yes — via `args.getArg()` |
| **Can modify parameters** | Yes — code before `next` | Yes — `args.setArg()` | No — already used by standard |
| **Can read return value** | Yes — after `next` | No — not computed yet | Yes — `args.getReturnValue()` |
| **Can modify return value** | Yes — assign to local `ret` | No | Yes — `args.setReturnValue()` |
| **Can cancel base method** | Effectively yes (skip `next` — but X++ forbids skipping conditionally) | Yes — `args.Cancel(true)` for cancellable methods | No — too late |
| **When to use** | When you need to **change** behavior | When you need to **observe** before, possibly cancel | When you need to **observe** after, possibly modify return |

### When to use which

- **CoC** — when you need to MODIFY behavior (change parameters, change return value, run code conditionally around standard). Tight binding, full chain semantics. The `next` keyword is the only way to participate in the standard chain.
- **Pre-handler** — when you just need to OBSERVE BEFORE standard runs, or to cancel a cancellable operation. Looser coupling than CoC.
- **Post-handler** — when you just need to OBSERVE AFTER standard runs, or to read/log/modify the result. Looser coupling than CoC.

---

## Section 6 — When do the three patterns fire? (the "execution timeline" confusion)

When testing this project, you will see all three messages appear in the infolog **even before you add or modify a sales line**. This caused confusion during development, so the explanation deserves its own section.

### What actually happens

`initFromSalesTable()` is called by D365 to **initialize the empty placeholder row** that appears in the lines grid the moment a sales order form opens. This is not waiting for the user to type anything.

When the SalesTable form opens:

1. The form needs the lines grid to be ready for the user to start typing.
2. D365 internally creates a new `SalesLine` buffer to back the empty placeholder row.
3. `initFromSalesTable()` is called on that buffer to copy header context (CustAccount, CustGroup, Currency, etc.) onto it.
4. If the user starts typing an item, the buffer is already pre-populated with header values.
5. If the user never types anything, the buffer is discarded — never persisted.

So the messages you see are from this **placeholder initialization**, not from a real save.

### How the three patterns relate during a single call

For each call to `initFromSalesTable()`, the framework runs all three patterns back-to-back:

```
ONE call to initFromSalesTable()
├── PRE handler runs first
├── CoC class's method runs
│   ├── Code BEFORE next executes
│   ├── next initFromSalesTable() runs (= standard logic)
│   └── Code AFTER next executes
└── POST handler runs last
```

The PRE and POST handlers are tied to the same method invocation as the CoC. There is no scenario where PRE fires "when the form opens" and POST fires "later when a line is added" — they are three sides of the same call.

### When the method gets called in real-world use

| User action | How many times `initFromSalesTable()` fires | What `RecId` looks like |
|---|---|---|
| User opens an existing SO | Once — for the empty placeholder row | `RecId == 0` (placeholder, not saved) |
| User clicks **+ New** on All sales orders | Once — for the placeholder | `RecId == 0` |
| User picks an item on the placeholder line and tabs out | Once more — as the line gets saved | `RecId != 0` (real save) |
| User adds a SECOND line | Once more for that line | `RecId != 0` |
| User just opens the form and does nothing | Only the first placeholder initialization | One set of messages only |

### Optional — guarding against placeholder noise

For audit-style logging where you only want messages on real saves, add this guard at the top of the handler body:

```xpp
SalesLine salesLine = salesLineType.parmSalesLine();
if (salesLine.RecId == 0)
{
    return;   // skip placeholder/uncommitted line
}
```

`RecId == 0` means the buffer exists in memory but has never been saved to the database. The guard makes the handler exit early without logging.

This guard is NOT applied in the current code because the goal of this scenario is to demonstrate that the patterns fire — including on placeholders. In production audit code you would typically add it.

---

## Section 7 — How to deploy and test in USMF

### Prerequisites

- This project **depends on** `OHMS_Scenario02_CustTable_Customizations` being deployed, because the CoC reads `OHMSCommunicationPreference` from the customer record.
- USMF legal entity (Contoso Entertainment Systems USA).
- Administrator rights on the dev VM.

### Deployment

1. Open Visual Studio as Administrator.
2. Open `Extensibility-Patterns.sln`.
3. Right-click project `OHMS_Scenario03_SalesLineType_Stamp` → **Build**.
4. Confirm `Build: 1 succeeded` in the Output window.
5. **Dynamics 365 → Synchronize database → Synchronize**. Required because the table extension adds a new column to `SalesLine`.
6. Wait for "Database synchronization complete."
7. PowerShell as Administrator: `iisreset`. Wait for "Internet services successfully restarted."

### Test 1 — All three patterns fire on form open

**Goal:** confirm the chain works end-to-end.

1. Browser → confirm USMF in the top-right company picker.
2. **Modules → Accounts receivable → Orders → All sales orders → + New**.
3. Customer account: pick a customer that has a value in **Communication preference (OHMS)** — for example `OHMS-T03` or `OHMS-T04` from Scenario 02.
4. Click **OK**.

**Expected — three messages appear in the infolog at the top of the form:**

```
[OHMS] POST handler: sales line initialized. Item=not yet set, CommunicationPreference=(empty)
[OHMS] PRE handler: about to initialize sales line for customer OHMS-T03 (SO 001135)
[OHMS] SalesLineType.initFromSalesTable CoC fired
```

Notes on the messages:
- All three messages appear from the placeholder initialization, before you've added any line.
- The POST handler shows `Item=not yet set` and `CommunicationPreference=(empty)` because the placeholder buffer hasn't been populated yet at this stage (RecId == 0).
- The display order in the infolog is not necessarily the execution order — D365 displays messages in its own order.

### Test 2 — Stamp on a real line

**Goal:** confirm the CoC actually populates the new field on a saved line.

1. On the same SO, click into the empty placeholder line in the **Sales order lines** grid.
2. Item number: pick `1000` (or any item with stock at WH 13).
3. Quantity: `1`.
4. Press Tab.

**Expected:**
- Another set of all three messages fires in the infolog. This time the POST handler's message includes the populated item and the correct communication preference value.
- Scroll the lines grid horizontally to find the **Communication preference (OHMS)** column. It should match the customer's preference.

### Test 3 — Add a second line

1. On the same SO, add a second line with another item.
2. Confirm the new line also receives the customer's communication preference automatically.

### Test 4 — Customer with empty preference

1. Pick a customer where `OHMSCommunicationPreference` is empty.
2. Create an SO, add a line.
3. **Expected:** infolog still fires (the CoC always runs), but the line's communication preference is empty because we copied an empty value. Correct, expected behavior.

### Optional — see column in grid

If you can't see the **Communication preference (OHMS)** column in the lines grid, it may be far to the right. Either:
- Scroll the grid horizontally
- Right-click any column header → **Personalize → Insert columns** → confirm the field is in the visible list

---

## Section 8 — Important behavioral note

The CoC fires only at **line creation time**. Once a line exists with a stamped value, later changes to the customer's `OHMSCommunicationPreference` do NOT cascade onto existing lines.

| Scenario | Result |
|---|---|
| Customer's preference changes BEFORE line is created | New line gets the new value |
| Customer's preference changes AFTER line already exists | Line keeps the OLD value |
| Customer's preference changes, user adds another NEW line | New line gets the new value; old lines unchanged |

This is **point-in-time defaulting** and matches every standard D365 header→line copy pattern. Currency, payment terms, delivery mode all behave the same way: snapshot at creation, independent thereafter.

---

## Section 9 — What this project teaches

By reading and running this project you should now be comfortable with:

- The single-argument `classStr(...)` intrinsic for class CoC targets
- The `<TableName>Type` helper class pattern (`SalesLineType`, `SalesTableType`, etc.)
- Why class CoC > table CoC for header-aware logic (parameters give you context for free)
- Verifying method names against actual standard X++ source before writing extensions (`parmSalesLine`, not `salesLine`)
- Three different ways to extend the same method: CoC, pre-handler, post-handler
- The `XppPrePostArgs` API: `getArg`, `getThis`, `getReturnValue`, `setReturnValue`, `Cancel`
- The placeholder-initialization timing of `initFromSalesTable` and why messages can fire before the user adds anything
- The `RecId == 0` guard pattern for separating placeholder buffers from real saves
- Why the three patterns run as a single bundled call, not as independent triggers

---

## Section 10 — References

- [Microsoft Learn — Class extension model in X++](https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/extensibility/class-extensions)
- [Microsoft Learn — Method wrapping and Chain of Command](https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/extensibility/method-wrapping-coc)
- [Microsoft Learn — Pre and post events for methods](https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/extensibility/customize-model-elements-extensions)
