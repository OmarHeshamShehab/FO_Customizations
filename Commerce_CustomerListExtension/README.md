# 🚀 Contoso D365 Commerce – RefNoExt Extension

### 🔍 Overview
This solution extends the standard D365 Commerce Customer entity to include a custom string field **RefNoExt** that can be edited in POS and synchronized back to HQ in real time.

- 📦 Adds `RefNoExt` to **CustTable** via X++ extension  
- 🔄 Propagates changes HQ → Channel DB → POS → HQ  
- 🌱 Implements CDX seed-data extension for initial replication  
- 🛠️ Provides SQL scripts for extension tables, views & procs  
- 💻 Hooks into Commerce Runtime (CRT) to persist & push updates  
- 🛍️ Enhances POS customer search & add/edit forms  

---

## 📚 Table of Contents
1. [Prerequisites](#prerequisites)
2. [Solution Structure](#solution-structure)
3. [X++ Extension (HQ)](#x-extension-hq)
4. [Channel Database (Scale Unit)](#channel-database-scale-unit)
5. [Commerce Runtime (CRT) -- C#](#commerce-runtime-crt--c)
6. [POS Customizations](#pos-customizations)
    - [Customer Search Columns](#customer-search-columns)
    - [Customer Add/Edit Control](#customer-addedit-control)
7. [Installation & Deployment](#installation--deployment)
8. [Testing & Verification](#testing--verification)
9. [Contributing](#contributing)
10. [License](#license)

 

---

## 🔧 Prerequisites
- D365 Commerce (v10+)  
- Commerce Scale Unit / Channel DB  
- Commerce SDK (ScaleUnitSample)  
- Visual Studio with AX/X++ tools  
- SQL Server permissions for `ext` schema  
- .NET SDK for CRT extensions  
- POS Extensibility framework & build tools  

---

## 🗂️ Solution Structure
    ├── AX
    │   ├── Extensions/CustTableRefNoExt
    │   ├── Classes/
    │   │   ├── RunnableClassRetTransService
    │   │   ├── ContosoRetailTransactionServiceEx_Extension
    │   │   └── ContosoCDXSeedDataEventHandler
    │   └── Resources/CustomColumnCustTable_AX7.xml
    ├── ScaleUnitSample
    │   ├── ChannelDatabase/
    │   │   ├── 0001_AddRefNoExtToCustTable_ExtReplication.sql
    │   │   ├── 0002_CreateCustTableView.sql
    │   │   └── 0010_UPDATECUSTOMEREXTENEDPROPERTIES.sql
    │   ├── CommerceRuntime/
    │   │   ├── RequestHandlers/CreateUpdateCustomerDataRequestHandler.cs
    │   │   └── Triggers/GetCustomerTrigger.cs
    │   └── POS/ViewExtensions/
    │       ├── Search/CustomColumns.ts
    │       └── CustomerAddEdit/CustomerCustomField.html & .ts
    └── README.md

---

## 💡 X++ Extension (HQ)
- **DataContract**  
    class UpdateCustomerResponse  
    {  
        boolean success;  
        str message;  
    }  

- **Service Extension**  
    [ExtensionOf(classStr(RetailTransactionServiceEx))]  
    final class ContosoRetailTransactionServiceEx_Extension  
    {  
        public static container UpdateCustomerExtendedProperties(str _accountNum, str _refNoExt) { … }  
    }  

- **Seed‑Data Event Handler**  
    class ContosoCDXSeedDataEventHandler  
    {  
        [SubscribesTo(...)]  
        public static void RetailCDXSeedDataBase_registerCDXSeedDataExtension(...) { … }  
    }  

---

## 🗄️ Channel Database (Scale Unit)
1. **0001_AddRefNoExtToCustTable_ExtReplication.sql**  
   - Creates/updates `[ext].[CONTOSOCUSTTABLEEXTENSION]`  
2. **0002_CreateCustTableView.sql**  
   - Defines `[ext].[CUSTTABLEVIEW]` join view  
3. **0010_UPDATECUSTOMEREXTENEDPROPERTIES.sql**  
   - Stored proc `[ext].[UPDATECUSTOMEREXTENEDPROPERTIES]`

---

## 🖥️ Commerce Runtime (CRT) – C#
- **Request Handler**  
    internal class CreateUpdateCustomerDataRequestHandler  
        : SingleAsyncRequestHandler<CreateOrUpdateCustomerDataRequest>  
    {  
        protected override async Task<Response> Process(...) { … }  
    }  

    1. Persist core customer  
    2. Extract `REFNOEXT` from `ExtensionProperties`  
    3. Call stored proc to upsert ext table  
    4. Invoke HQ real‑time service  

- **Trigger**  
    internal class GetCustomerTrigger : IRequestTriggerAsync { … }  
    - Appends `RefNoExt` to customer on GET requests

---

## 🛍️ POS Customizations

### Customer Search Columns
**File**: `ViewExtensions/Search/CustomColumns.ts`  
    export default (context): ICustomerSearchColumn[] => [  
      // … other columns …,  
      {  
        title: context.resources.getString("OHMS_4312"),  
        computeValue: row =>  
          row.ExtensionProperties.find(p => p.Key === "RefNoExt")?.Value.StringValue ?? "",  
        ratio: 25,  
        collapseOrder: 1,  
        minWidth: 200  
      },  
      // …  
    ];

### Customer Add/Edit Control
- **HTML**: `CustomerCustomField.html`  
- **TS Control**: `CustomerCustomField.ts`  
    - Clones template, binds `onchange` to update `customer.ExtensionProperties["REFNOEXT"]`

---

## ⚙️ Installation & Deployment
1. **AX**: Import X++ artifacts → Build & deploy → CDX init  
2. **Channel DB**: Run SQL scripts in order (0001 → 0002 → 0010)  
3. **CRT**: Add/compile C# handler & trigger → Deploy to Scale Unit  
4. **POS**: Include ViewExtensions → Update `Extensions.config` → Rebuild POS

---

## ✅ Testing & Verification
1. In POS, set **Reference Number** → Save  
2. Verify Channel DB & CRT writes & HQ real‑time push  
3. In HQ “Customers” form, confirm `RefNoExt` value  
4. Update in HQ → CDX sync → Confirm in POS

---

## 🤝 Contributing
1. Fork repo & create feature branch  
2. Commit changes & push to your fork  
3. Open a Pull Request

---