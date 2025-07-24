# ✨ Dynamics 365 Commerce Scale Unit Sample: Custom CustTable Extension

Introducing a **stylish** guide to integrate a custom `RefNoExt` field across the Dynamics 365 Commerce stack—from HQ to POS! Each section features icons for quick scanning and a cohesive look.

## 📑 Table of Contents

* 🧠 [Concepts & Prerequisites](#concepts-prerequisites)
* 🛠️ [CustTable Extension and Form Update](#custtable-extension-and-form-update)
* 🔌 [CDX Seed Data Event Handler](#cdx-seed-data-event-handler)
* 🗂️ [CDX Seed Data Resource Registration](#cdx-seed-data-resource-registration)
* ⏱️ [Commerce Scheduler Initialization](#commerce-scheduler-initialization)
* ⚙️ [Scale Unit CRT Trigger](#scale-unit-crt-trigger)
* 💼 [POS Customer Search View Extension](#pos-customer-search-view-extension)
* 🗄️ [Channel Database Scripts](#channel-database-scripts)
* 📦 [Scale Unit POS Manifest Modification](#scale-unit-pos-manifest-modification)

---

<a id="concepts-prerequisites"></a>

## 🧠 Concepts & Prerequisites

Before diving into these steps, ensure familiarity with:

* **X++ & AX Extensions**: Extending tables, forms, and classes via the AX extension model.
* **C# & .NET Async Programming**: Using `async/await`, ensuring thread safety with locks, and proper disposal via `using` blocks.
* **Commerce Runtime (CRT) Triggers**: Implementing the `IRequestTriggerAsync` interface for pre- and post-execution hooks.
* **SQL & DatabaseContext**: Writing T‑SQL scripts for tables and views, and querying via `DatabaseContext.ExecuteQueryDataSetAsync`.
* **TypeScript & POS API**: Creating POS view extensions with `ICustomerSearchColumn`, handling `GlobalCustomer.ExtensionProperties`, and localization.
* **JSON Manifest Editing**: Modifying `manifest.json` to register extensions under the POS `SearchView`.

**Why it matters:** These foundational skills allow you to implement, troubleshoot, and extend each component effectively.

---

<a id="custtable-extension-and-form-update"></a>

## 🛠️ CustTable Extension and Form Update

**What was done:**

* **Table extension project**: Added the `RefNoExt` field to the existing `CustTable` schema without modifying base objects.
* **Form customization**: Updated the CustTable form design to display the new reference number field.

**Key considerations:**

* Using the AX extension model prevents upgrade conflicts.
* No additional X++ form logic is required—purely declarative UI changes.

---

<a id="cdx-seed-data-event-handler"></a>

## 🔌 CDX Seed Data Event Handler

**Class:** `ContosoCDXSeedDataEventHandler`

**Responsibility:**

* Subscribes to the CDX seed-data registration event in the HQ commerce pipeline.
* Detects when the standard AX7 seed-data initialization runs.
* Registers the custom seed-data resource for the `CustTable` extension.

**Why it matters:** Bulk export/import operations will automatically include the new `RefNoExt` field.

---

<a id="cdx-seed-data-resource-registration"></a>

## 🗂️ CDX Seed Data Resource Registration

**Resource Name:** `CustomColumnCustTable_AX7`

**Responsibility:**

* Overrides the `CustTable` subjob in the CDX XML manifest.
* Maps the `RecId`, `AccountNum`, and `RefNoExt` fields to the extension table target.

**Why it matters:** Integrates custom data into the standard CDX process, maintainable via version-controlled XML.

---

<a id="commerce-scheduler-initialization"></a>

## ⏱️ Commerce Scheduler Initialization

**Task:** Initialize the Commerce Scheduler in Headquarters.

**Responsibility:**

* Clears any stale scheduler configurations for a clean state.
* Executes the CDX initialization job and confirms the presence of `RefNoExt` in the subjob definitions.

**Why it matters:** Ensures channel databases are seeded with the updated schema before scale-unit deployment.

---

<a id="scale-unit-crt-trigger"></a>

## ⚙️ Scale Unit CRT Trigger

**Class:** `ChannelDataServiceRequestTrigger`

**Responsibility:**

* Intercepts two CRT request types:

  1. **GetChannelConfigurationDataRequest** to inject custom configuration parameters.
  2. **SearchCustomersDataRequest** to retrieve and append `RefNoExt` for each customer.
* Applies thread-safe locking for cache updates and disposes database contexts properly.

**Why it matters:** Bridges SQL storage of the extension with in-memory `GlobalCustomer` entities, enabling downstream access.

---

<a id="pos-customer-search-view-extension"></a>

## 💼 POS Customer Search View Extension

**Module:** `CustomCustomerSearchColumns`

**Responsibility:**

* Defines additional columns for the POS customer search results (Account Number, Full Name, **RefNoExt**, Email, Phone).
* Configures column layout details: ratio, minimum width, and collapse order.

**Why it matters:** Surfaces the new reference number directly in the POS UI for end-user efficiency.

---

<a id="channel-database-scripts"></a>

## 🗄️ Channel Database Scripts

**0001\_AddRefNoExtAndAccountNumToCustTable.sql**

* Creates the `CONTOSOCUSTTABLEEXTENSION` table with `RefNoExt` and `AccountNum` columns matching `CustTable.RecId`.
* Grants DML permissions to the `DataSyncUsersRole`.

**0002\_CreateCustTableView\.sql**

* Defines the `ext.CUSTTABLEVIEW` view joining base and extension tables.
* Grants SELECT permission to the `DataSyncUsersRole`.

**Why it matters:** Isolates custom data and provides a unified access point for synchronization and reporting.

---

<a id="scale-unit-pos-manifest-modification"></a>

## 📦 Scale Unit POS Manifest Modification

**File:** `manifest.json`

**Responsibility:**

* Registers `CustomCustomerSearchColumns` under the POS `SearchView` in the `extend.views` section of the manifest.

**Why it matters:** Ensures the POS application loads the custom view extension at runtime without manual binary edits.
