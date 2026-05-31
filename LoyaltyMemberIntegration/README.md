# Loyalty Member Integration — D365 Finance & Operations

A custom OData integration surface in D365 F&O that lets an external system (e-commerce
site, CRM, loyalty engine) create, read, and update loyalty members **and invoke a
business operation** — adding points and recalculating the member's tier server-side.

- **Model:** `OHMS`
- **Project:** `LoyaltyMemberIntegration`
- **Object prefix:** `OHM_`
- **OData endpoint:** `/data/OHM_LoyaltyMembers`

---

## 1. Business scenario

Customers earn loyalty points and move through tiers (Bronze → Silver → Gold → Platinum)
that unlock perks. The system where points are *earned* (storefront / CRM) is usually not
the system where finance and operations live (D365). The two must stay in sync, and the
tier rules must be owned in one place so every channel agrees on who is "Gold."

This solution gives the outside system a controlled doorway into D365 to:

1. **Register** a new member (POST).
2. **Read** a member's current points and tier (GET), including a computed "points to next tier".
3. **Update** member details such as phone or linked customer (PATCH).
4. **Add points** via a custom action — D365 itself adds the points and re-evaluates the tier.

The fourth point is the core of the design: the external system *reports activity*; D365
*owns the rule*. The website never decides who is Gold.

### Members can be created on either side

- **Outside, synced in:** someone signs up on the web before they are a customer in F&O.
  This is why `CustAccount` is **optional** — there may be no customer to link yet.
- **Inside D365:** a clerk enrolls a member on the form, or a process auto-enrolls on first
  invoice and links the customer immediately.

Both paths converge on the same table. `MemberId` is owned by the source system so retries
are idempotent (see §8, duplicate POST).

---

## 2. Tier rules

Bronze is the entry tier (0). Thresholds are the points required to *reach* each tier:

| Tier | Points required |
|---|---|
| Bronze | 0 (entry) |
| Silver | 500 |
| Gold | 1500 |
| Platinum | 5000 |

These live in exactly one place — the helper class — so the entity's computed field and the
add-points action can never disagree.

---

## 3. Object inventory

| Type | Name | Purpose |
|---|---|---|
| Base Enum | `OHM_LoyaltyTier` | Fixed tier set: None, Bronze, Silver, Gold, Platinum |
| EDT (String) | `OHM_LoyaltyMemberId` | Member key, supplied by the external system |
| EDT (Int) | `OHM_LoyaltyPoints` | Points balance |
| Table | `OHM_LoyaltyMember` | Where member data lives |
| Data Entity | `OHM_LoyaltyMemberEntity` | OData contract → `/data/OHM_LoyaltyMembers` |
| Class | `OHM_LoyaltyMemberHelper` | All loyalty logic (tier resolution, add points) |
| Form | `OHM_LoyaltyMemberForm` | Simple List view inside F&O |
| Display menu item | `OHM_LoyaltyMember` | Opens the form |
| Menu extension | `<Module>.OHMS` | Places the menu item under a module |

---

## 4. Data layer

### 4.1 Base enum `OHM_LoyaltyTier`

`IsExtensible = Yes`. Elements: `None(0), Bronze(1), Silver(2), Gold(3), Platinum(4)`.

### 4.2 EDTs

- `OHM_LoyaltyMemberId` — String, size 40, **no number sequence** (the external system owns the value).
- `OHM_LoyaltyPoints` — Int.

### 4.3 Table `OHM_LoyaltyMember`

**Fields**

| Field | Type / EDT | Notes |
|---|---|---|
| `MemberId` | `OHM_LoyaltyMemberId` | Mandatory; the natural key |
| `MemberName` | `Name` | |
| `CustAccount` | `CustAccount` | Optional link to customer |
| `PointsBalance` | `OHM_LoyaltyPoints` | |
| `Tier` | `OHM_LoyaltyTier` (enum) | |
| `Phone` | `Phone` (standard EDT, EUII) | |

**Index** — `MemberIdIdx`: field `MemberId`, `AllowDuplicates = No`, `AlternateKey = Yes`.
Set as the table's **PrimaryIndex**. This enforces idempotency and makes records addressable
by `MemberId` over OData.

**Field group** — `Overview`: MemberId, MemberName, CustAccount, PointsBalance, Tier, Phone.

**Relation to CustTable** (validation only)
- Related table `CustTable`, `RelationshipType = Association`
- `Cardinality = ZeroMore`, `RelatedTableCardinality = ExactlyOne`
- Constraint: `CustAccount → CustTable.AccountNum`
- No `OnDelete` action (deleting a customer leaves loyalty rows intact rather than cascading)

**Table properties** — `TableGroup = Main`, `SaveDataPerCompany = Yes`,
CreatedBy / CreatedDateTime / ModifiedBy / ModifiedDateTime = Yes,
TitleField1 = `MemberId`, TitleField2 = `MemberName`.

**`find` method**

```xpp
public static OHM_LoyaltyMember find(OHM_LoyaltyMemberId _memberId, boolean _forUpdate = false)
{
    OHM_LoyaltyMember member;

    if (_memberId)
    {
        member.selectForUpdate(_forUpdate);

        select firstonly member
            where member.MemberId == _memberId;
    }

    return member;
}
```

---

## 5. Logic layer — `OHM_LoyaltyMemberHelper`

All loyalty logic lives here, so the rules have a single definition.

```xpp
public class OHM_LoyaltyMemberHelper
{
    #define.SilverThreshold(500)
    #define.GoldThreshold(1500)
    #define.PlatinumThreshold(5000)

    public static OHM_LoyaltyTier resolveTier(OHM_LoyaltyPoints _points)
    {
        OHM_LoyaltyTier tier;

        if (_points >= #PlatinumThreshold)      { tier = OHM_LoyaltyTier::Platinum; }
        else if (_points >= #GoldThreshold)     { tier = OHM_LoyaltyTier::Gold; }
        else if (_points >= #SilverThreshold)   { tier = OHM_LoyaltyTier::Silver; }
        else                                    { tier = OHM_LoyaltyTier::Bronze; }

        return tier;
    }

    public static int nextTierThreshold(OHM_LoyaltyPoints _points)
    {
        int threshold;

        if (_points < #SilverThreshold)         { threshold = #SilverThreshold; }
        else if (_points < #GoldThreshold)      { threshold = #GoldThreshold; }
        else if (_points < #PlatinumThreshold)  { threshold = #PlatinumThreshold; }
        else                                    { threshold = _points; } // already Platinum

        return threshold;
    }

    public static OHM_LoyaltyMember addPoints(OHM_LoyaltyMemberId _memberId, OHM_LoyaltyPoints _points)
    {
        OHM_LoyaltyMember member;

        if (!_memberId)
        {
            throw error("Member ID is required.");
        }

        ttsbegin;

        member = OHM_LoyaltyMember::find(_memberId, true); // select for update (row lock)

        if (!member.RecId)
        {
            ttsabort;
            throw error(strFmt("Loyalty member %1 was not found.", _memberId));
        }

        if (member.PointsBalance + _points < 0)
        {
            ttsabort;
            throw error("Resulting points balance cannot be negative.");
        }

        member.PointsBalance += _points;
        member.Tier = OHM_LoyaltyMemberHelper::resolveTier(member.PointsBalance);
        member.update();

        ttscommit;

        return member;
    }
}
```

**Key points**
- `#define` macros = compile-time text substitution; one place to change a threshold.
- `resolveTier` checks **highest tier first** so a high balance isn't caught by a lower test.
- `addPoints` runs inside `ttsbegin/ttscommit` with a `selectForUpdate` lock to prevent
  lost updates from concurrent calls. Accepts negative points for redemptions and guards
  against a negative balance.

---

## 6. OData layer

### 6.1 Entity `OHM_LoyaltyMemberEntity`

Created via the table's **Create data entity** add-in.

| Property | Value |
|---|---|
| Public Entity Name | `OHM_LoyaltyMember` |
| Public Collection Name | `OHM_LoyaltyMembers` |
| Is Public | Yes |
| Entity Category | Master |
| Primary Company Context | `DataAreaId` |
| Primary Key | `EntityKey` (based on `MemberId`) |
| Data Management Enabled | No (live OData, no DMF staging table) |

**Fields:** MemberId, MemberName, CustAccount, PointsBalance, Tier, Phone, plus the unmapped
`PointsToNextTier`.

> The wizard's audit fields (`CreatedBy`, `CreatedDateTime`, `ModifiedBy`, `ModifiedDateTime`)
> were **removed** — those names are reserved system field names and the entity rejects them.
> If audit timestamps are needed on the API later, re-add them under non-reserved names
> (e.g. `CreatedOn`, `ModifiedOn`) while leaving their `Data Field` mapping intact.

**Virtual field `PointsToNextTier`** — `DataEntityViewUnmappedFieldInt64`,
`Is Computed Field = No` (it is *unmapped*, populated in X++ via `postLoad`, not a SQL view).

### 6.2 Entity code-behind

```xpp
public class OHM_LoyaltyMemberEntity extends common
{
    /// Runs after each record is read through the entity (every GET).
    /// Fills the unmapped PointsToNextTier field.
    public void postLoad()
    {
        super();

        int nextThreshold = OHM_LoyaltyMemberHelper::nextTierThreshold(this.PointsBalance);

        // 0 if already at the top tier (nextThreshold == balance)
        this.PointsToNextTier = nextThreshold - this.PointsBalance;
    }

    /// OData action bound to a single member. Adds points and recalculates tier.
    /// Returns the new balance.
    [SysODataActionAttribute('addPoints', true)]
    public int addPoints(int pointsToAdd)
    {
        OHM_LoyaltyMember updated = OHM_LoyaltyMemberHelper::addPoints(this.MemberId, pointsToAdd);
        return updated.PointsBalance;
    }
}
```

- `postLoad` is the hook where unmapped fields are computed at read-time.
- `[SysODataActionAttribute('addPoints', true)]` publishes `addPoints` as an OData action;
  `true` = bound to an instance, so `this` is the member addressed in the URL.

---

## 7. UI layer

- **Form `OHM_LoyaltyMemberForm`** — Simple List pattern, data source `OHM_LoyaltyMember`,
  grid bound to the `Overview` field group, QuickFilter targeting the grid.
  - Data source `InsertIfEmpty = No` and `InsertAtEnd = No` so the form does **not** open on a
    blank new row; new records appear only when the user clicks **New**.
- **Display menu item `OHM_LoyaltyMember`** → Object Type `Form`, Object `OHM_LoyaltyMemberForm`.
- **Menu extension** on the chosen module (`AccountsReceivable` or `SalesAndMarketing`) →
  becomes `<Module>.OHMS`; the menu item is dropped into a section (e.g. Common / Inquiries).

> Note: the form shows 6 columns; the OData entity also exposes `PointsToNextTier`. The form
> binds to table columns and the computed field is not a column, so it appears only on the API.

---

## 8. Build & deploy

1. **Build** the project.
2. **Dynamics 365 → Synchronize database.** Required — the OData endpoint and the action are
   not registered until sync completes (calls 404 before that).

---

## 9. Postman testing

Auth: OAuth2 bearer token (set as `Authorization: Bearer ...`). All write requests need
`Content-Type: application/json`.

> The base URL is held in a Postman variable ending in `/data/`. Make sure there is **no stray
> `}` and no space** between the variable and the collection name in the URL, or you get a
> 404 "No route data was found."

### Requests

| # | Method | Name | URL (after the `/data/` base) | Body |
|---|---|---|---|---|
| 1 | GET | Get Loyalty Members | `OHM_LoyaltyMembers?cross-company=true` | — |
| 2 | GET | Get Single Member | `OHM_LoyaltyMembers(dataAreaId='USMF',MemberId='LM-0001')` | — |
| 3 | POST | Create Member | `OHM_LoyaltyMembers` | see below |
| 4 | PATCH | Update Member | `OHM_LoyaltyMembers(dataAreaId='USMF',MemberId='LM-0001')` | see below |
| 5 | POST | Add Points (action) | `OHM_LoyaltyMembers(dataAreaId='USMF',MemberId='LM-0001')/Microsoft.Dynamics.DataEntities.addPoints` | see below |

**Create (POST) body** — do not send `Tier` or `PointsToNextTier`:

```json
{
    "dataAreaId": "USMF",
    "MemberId": "LM-0001",
    "MemberName": "Test Member",
    "PointsBalance": 0,
    "Phone": "555-0100"
}
```

**Update (PATCH) body** — only the changed field(s):

```json
{
    "Phone": "555-0199"
}
```

To link a customer (validated against `CustTable` in the company — must be a real account):

```json
{
    "CustAccount": "US-001"
}
```

**Add Points (action) body** — parameter name must be exactly `pointsToAdd`:

```json
{
    "pointsToAdd": 600
}
```

### Order matters

POST must run first; PATCH and Add Points act on the record it creates. The list GET returns
`"value": []` until a record exists — that is the endpoint working, not an error.

---

## 10. Test scenarios & expected results

| Test | Action | Expected |
|---|---|---|
| Endpoint live | GET list | `200`, `value: []` (empty until first POST) |
| Create | POST LM-0001 | `201 Created`, `Tier: None`, `PointsToNextTier: 500` |
| Update phone | PATCH `{ "Phone": "555-0199" }` | `204 No Content` |
| Add points → Silver | Action `{ "pointsToAdd": 600 }` | `200`, body `600`; tier flips to **Silver** (≥500) |
| Add points → Gold | Action `{ "pointsToAdd": 900 }` | balance 1500, tier **Gold**; `PointsToNextTier: 3500` |
| Link customer | PATCH `{ "CustAccount": "US-001" }` | `204` if the account exists in USMF; `400` if not (relation validation) |
| Redemption / demotion | Action `{ "pointsToAdd": -1400 }` | balance drops, tier recalculates **down** |
| Negative-balance guard | Action `{ "pointsToAdd": -99999 }` | error: "Resulting points balance cannot be negative." |
| Idempotency / duplicate | Re-POST LM-0001 | error: "The record already exists." (unique key) |
| Computed field | GET single after each change | `PointsToNextTier` = next threshold − balance; `0` at Platinum |

### Validating the computed field

`PointsToNextTier` exists only on the API (not on the form). Read a member and check the value
against (next threshold − current balance). Change the balance with the action and GET again —
the value recalculating on each read (e.g. 400 → 1000 as balance goes 100 → 500) proves it is
computed live in `postLoad`, not stored. If the field is **absent** from the response, the
entity field's **Name** is not exactly `PointsToNextTier`.

---

## 11. Design decisions & gotchas (lessons)

- **External system owns `MemberId`** (no number sequence) → retries are idempotent; the unique
  key rejects duplicates instead of creating them.
- **Reserved field names** — `CreatedBy/CreatedDateTime/ModifiedBy/ModifiedDateTime` cannot be
  exposed under those names on an entity; remove or rename.
- **Unmapped vs computed** — unmapped fields are filled in X++ (`postLoad`); computed fields are
  SQL-view methods. This field is unmapped.
- **Action vs CRUD** — plain OData edits columns; an action invokes server-side logic. The tier
  rule stays in F&O.
- **Transaction + lock** in `addPoints` prevents lost updates from concurrent calls.
- **CustTable relation** validates `CustAccount`; linking a non-existent account fails by design.
- **No DMF staging table** — staging is only for file-based import/export, not live OData.
- **URL hygiene** — a stray brace/space between the base variable and the collection name causes
  a 404 "No route data."

---

## 12. Possible next steps (not built)

- Move tier thresholds to a **setup table** so finance can change them without a code deploy.
- Re-expose audit timestamps (renamed) and enable change tracking for incremental "what changed
  since" sync.
- Add a **display method** so the form can also show `PointsToNextTier`.
- Add an **unbound** action (e.g. bulk enroll) for operations not tied to a single member.
- Secure a dedicated integration role/privilege and assign it to the service account.
