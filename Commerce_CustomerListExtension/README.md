```markdown
# ✨ Dynamics 365 Commerce Scale Unit Sample: Custom CustTable Extension

Introducing a **stylish** guide to integrate a custom `RefNoExt` field across the Dynamics 365 Commerce stack—from HQ to POS! Each section features icons for quick scanning and a cohesive look.

---

## 🧠 Concepts & Prerequisites

Before diving into these steps, ensure familiarity with:

- **X++ & AX Extensions**: Understand how to extend tables, forms, and classes without modifying base code.
- **C# & .NET Async Programming**: Grasp `async/await`, thread safety (locks), and disposal patterns (`using` blocks).
- **Commerce Runtime (CRT) Triggers**: Know how to implement `IRequestTriggerAsync` for pre- and post-execution pipelines.
- **SQL & DatabaseContext**: Ability to write T-SQL scripts for tables/views and use `DatabaseContext.ExecuteQueryDataSetAsync`.
- **TypeScript & POS API**: Experience creating POS view extensions, working with `ICustomerSearchColumn`, and module manifests.
- **JSON Manifest Editing**: Skills to modify `manifest.json` to register extensions in Commerce Scale Unit.

**Why it matters:**
- 📚 These foundational skills enable you to read, modify, and troubleshoot each component effectively.

---

## 📑 Table of Contents

1. 🧠 Concepts & Prerequisites
2. 🛠️ CustTable Extension and Form Update
3. 🔌 CDX Seed Data Event Handler
4. 🗂️ CDX Seed Data Resource Registration
5. ⏱️ Commerce Scheduler Initialization
6. ⚙️ Scale Unit CRT Trigger
7. 💼 POS Customer Search View Extension
8. 🗄️ Channel Database Scripts
9. 📦 Scale Unit POS Manifest Modification

---

## 1. 🛠️ CustTable Extension and Form Update

**What was done:**
- 🔹 **Table extension project**: Added `RefNoExt` field to `CustTable` without touching core code.
- 🔹 **Form customization**: Exposed the new field on the CustTable form UI.

**Key considerations:**
- ✅ AX extension model ensures upgrade safety.
- ✅ No additional form logic—purely declarative.

---

## 2. 🔌 CDX Seed Data Event Handler

**Class:** `ContosoCDXSeedDataEventHandler`

**Responsibility:**
- Subscribes to the CDX registration event.
- Detects the AX7 seed-data init.
- Registers the custom seed-data resource for `RefNoExt`.

**Why it matters:**
- 🔄 Ensures bulk export/import includes the extension.
- 🔍 Centralizes seed-data registration logic.

---

## 3. 🗂️ CDX Seed Data Resource Registration

**Resource Name:** `CustomColumnCustTable_AX7`

**Responsibility:**
- Overrides the `CustTable` subjob in the CDX manifest.
- Maps `RecId`, `AccountNum`, and `RefNoExt` to the extension target.

**Why it matters:**
- 📦 Integrates custom data seamlessly into CDX pipelines.
- 🔐 Keeps custom mapping in a version-controlled XML.

---

## 4. ⏱️ Commerce Scheduler Initialization

**Task:** Initialize Scheduler in HQ

**Responsibility:**
- Clears stale configurations.
- Runs CDX init, verifying `RefNoExt` appears in subjobs.

**Why it matters:**
- ✔️ Validates seed-data registration UI-side.
- 🚀 Prepares scale unit deployment with correct schema.

---

## 5. ⚙️ Scale Unit CRT Trigger

**Class:** `ChannelDataServiceRequestTrigger`

**Responsibility:**
- Intercepts:
  1. **ChannelConfigRequest**: Injects custom parameters.
  2. **SearchCustomersRequest**: Pulls `RefNoExt` per customer.
- Ensures thread safety and async disposal.
- Populates `GlobalCustomer.ExtensionProperties`.

**Why it matters:**
- 🌉 Bridges SQL storage and in-memory CRT entities.
- 🎯 Delivers extension data to downstream services/UI.

---

## 6. 💼 POS Customer Search View Extension

**Module:** `CustomCustomerSearchColumns`

**Responsibility:**
- Adds columns to POS search results:
  - Account#, Full Name, **RefNoExt**, Email, Phone.
- Configures layout (ratio, minWidth, collapseOrder).

**Why it matters:**
- 🔍 Surfaces `RefNoExt` directly in POS workflows.
- 🖌️ Uses POS extension framework for UI customization.

---

## 7. 🗄️ Channel Database Scripts

**0001_AddRefNoExtAndAccountNumToCustTable.sql**
- Creates `CONTOSOCUSTTABLEEXTENSION` table with `RefNoExt` and `AccountNum`.
- Grants DML rights to `DataSyncUsersRole`.

**0002_CreateCustTableView.sql**
- Defines `ext.CUSTTABLEVIEW` joining base and extension.
- Grants SELECT to `DataSyncUsersRole`.

**Why it matters:**
- 🔒 Isolates custom data storage.
- 📊 Provides unified view for sync engines and reports.

---

## 8. 📦 Scale Unit POS Manifest Modification

**File:** `manifest.json`

**Responsibility:**
- Registers `CustomCustomerSearchColumns` under `SearchView`.
- Ensures POS app loads the extension at runtime.

**Why it matters:**
- 🔗 Connects scale unit deployment with POS customizations.
- 🗂️ Maintains clear separation between manifest and code.

---

✨ **Ready to deploy your stylish Commerce extension with icons!**
```
