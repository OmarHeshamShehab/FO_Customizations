# 🇷🇴 RO SAF-T (D406) — Electronic Reporting Test Package & Troubleshooting Guide

> **What is this, in plain English:**
> A customer's Romanian SAF-T (D406) declaration — built by an ISV as a custom package
> on top of Microsoft's standard **Electronic Reporting (ER)** engine in D365 F&O —
> started failing after a Microsoft platform upgrade, with no clear error logs.
> To prepare for the troubleshooting call with the ISV, we rebuilt the **entire
> architecture of such a package in miniature** on a local 10.0.48 VHD (Contoso USMF):
> we imported Microsoft's SAF-T base configurations, derived our own custom format
> from them (exactly what the ISV did for Romania), designed and mapped it, and wrapped
> it in a small X++ package (parameters table, form, menu, security, SysOperation stack)
> that invokes ER from code — the same way the ISV's "Generate declaration" menu item does.
> Along the way we hit and fixed three real production-class ER failures.
> This document is the full record: setup, code, tests, and a troubleshooting playbook.

---

## 📐 1. Architecture — how the ISV package is built

```
Microsoft (base, shipped via LCS/upgrades)          ISV (custom, derived)
─────────────────────────────────────────          ─────────────────────────────
Standard Audit File (SAF-T)  ← data model
  ├─ SAF-T model mappings    ← binds model                SAF-T Format (RO / D406)
  │   to F&O tables                    ▲                  provider = ISV
  └─ SAF-T Formats (DK/LT/NO)          └── derived from ──┘  Base = model version N
```

Key facts (all verified on Microsoft Learn):
- ISV localizations **must** be built on ER; they derive from Microsoft configs and
  **rebase** when Microsoft ships a new base version. Un-merged changes = conflicts,
  resolved manually in the designer.
- Every config version declares **Applicable product versions** (visible in the
  Prerequisites pane) — a version pack certified for 10.0.43–10.0.46 is not certified
  for a later build.
- At runtime the system uses the most recent **Completed** version — Draft versions
  are invisible to the runtime API.
- **Microsoft ships NO Romanian SAF-T format** (only DK/LT/NO in the GER package) —
  the customer's RO format is 100% ISV-owned, derived from Microsoft's base model.

---

## 📦 2. Part A — ER configuration setup (what we did in the UI)

### 2.1 Get the latest Microsoft ER configurations
1. LCS → **Shared asset library** → asset type **GER Configuration** → download
   **"GER Configurations – All"** (zip, all configs, version ~750).
2. Extract so the `.xml` files sit **flat** in `C:\ERConfigs` on the VHD (not nested).

### 2.2 Register a File system repository
1. **Organization administration > Workspaces > Electronic reporting**.
2. Select the **Microsoft** provider tile → **Repositories** → **+ Add** → **File system**.
3. Name: `ERConfigs`, Description: `Latest ER configs from LCS - 21-July-2026`,
   Working directory: `C:\ERConfigs` → OK.
4. Select the row → **Open** → full configuration tree loads from the folder.
   *(File system repositories work on dev/Tier-1 environments.)*

### 2.3 Import the SAF-T base
1. In the repository tree: **Standard Audit File (SAF-T) > SAF-T Financial data model mapping**.
2. Versions pane → select latest (e.g. **190.157**) → **Import** → **Yes**
   (imports parents/related recursively; result: "Imported: 9; ignored: 0").

### 2.4 Create your own configuration provider (NEVER author as Microsoft)
1. ER workspace → Related links → **Configuration providers** → **+ New**:
   Name `Contoso Test`, Internet address `https://contoso.com` → Save.
2. Back on the workspace: **⋯** on the Contoso Test tile → **Set active**.
   *(Authoring under Microsoft's provider causes collisions on future Microsoft updates.)*

### 2.5 Derive a custom format (what the ISV did for RO)
1. **Organization administration > Electronic reporting > Configurations** →
   select the model **Standard Audit File (SAF-T)** → **Create configuration**.
2. Dialog: **Format based on data model Standard Audit File (SAF-T)**,
   Name `SAF-T Format (RO test)`, Format type **XML**,
   Data model version **182** (highest), Data model definition **Audit File**.
3. Result: new child node, provider Contoso Test, version **1.182 Draft**,
   **Base = Standard Audit File (SAF-T) 182/208** — that Base link is the
   upgrade-fragility point.

### 2.6 Design the format
Designer → build the tree:
```
AuditFile            (XML \ Element)
└─ Header            (XML \ Element)
   └─ CompanyName    (Text \ String)   ← note: String emits text INSIDE parent tag
```
All properties default.

### 2.7 Bind format to model (Mapping tab)
- Left = format tree, Right = data model (root: Audit File).
- Bind **CompanyName** ↔ **Company Info(Company) > Company Name(Name)**
  → shows `CompanyName = model.Company.Name`. **Save**.

⚠️ **Error hit here:** *"More than one model mapping exists for the
'Standard Audit File (SAF-T) (Audit File)' data model… Set one of the
configurations as default."*
**Fix:** Configurations tree → select the mapping config named in the error
(**Standard Audit File model mapping**) → Edit → **Default for model mapping = Yes** → Save.
*(The default flag disambiguates per data-model ROOT — setting it on a config that
implements a different root does nothing.)*

### 2.8 Complete the version (critical!)
Configurations → SAF-T Format (RO test) → Versions →
**Change status > Complete**. Runtime (incl. the X++ API) resolves only
**Completed** versions; the designer's Run works on Drafts, which masks this.

### 2.9 Run test (UI)
Designer → **Run** → accept ER prompt → output:
```xml
<?xml version="1.0" encoding="utf-8"?>
<AuditFile>
  <Header>Contoso Entertainment System USA</Header>
</AuditFile>
```

---

## 🧱 3. Part B — X++ package (model `OHMS`, solution `ROSaftLocalization`)

Model references needed: ApplicationPlatform, ApplicationFoundation,
ApplicationSuite, **ElectronicReporting**.

### 3.1 Project inventory
```
Tables:              ROSaftParameters
EDT (Int64):         ROSaftERFormatMappingRecId   (extends RefRecId, ReferenceTable = ERFormatMappingTable)
Forms:               ROSaftParameters             (Simple List pattern)
Classes:             SAFTRoGenerateContract / SAFTRoGenerateService / SAFTRoGenerateController
Display menu item:   ROSaftParameters             (→ form)
Action menu item:    ROSaftGenerate               (→ controller)
Menu extension:      GeneralLedger.OHMS           (submenu "RO SAF-T" with both items)
Security:            ROSaftParametersMaintain, ROSaftGenerateProcess (privileges)
                     ROSaftMaintainDuty (duty) → ROSaftClerk (role)
Label file:          ROSaft (en-US)
```

### 3.2 Label file `ROSaft`
```
ROSaftParameters=RO SAF-T parameters
ROSaftParametersDevDoc=Contains the RO SAF-T module parameters. Singleton record per company.
Key=Key
ERFormatMappingRecId=ER format mapping
ERFormatMappingRecIdHelp=Reference to the Electronic reporting format mapping used to generate the SAF-T file.
ROSaftParametersFormCaption=RO SAF-T parameters
Setup=Setup
ROSaftGenerate=Generate SAF-T declaration (RO)
ROSaftGenerateHelp=Generates the Romanian SAF-T (D406) XML file using Electronic reporting.
FromDate=From date
ToDate=To date
GenerateDialogCaption=Generate SAF-T (RO test)
ROSaftParametersNotSetup=RO SAF-T parameters are not set up. Select an ER format mapping first.
ROSaftMenu=RO SAF-T
ROSaftMaintainDuty=Maintain RO SAF-T declaration
ROSaftClerkRole=RO SAF-T clerk
ROSaftParametersMaintainPriv=Maintain RO SAF-T parameters
ROSaftGenerateProcessPriv=Generate RO SAF-T declaration
MappingName=Mapping name
MappingDescription=Mapping description
```

### 3.3 Table `ROSaftParameters` (Parameter System Design Pattern)
Properties: TableGroup=**Parameter**, CacheLookup=**Found**,
Primary/Cluster/Replacement key=**KeyIdx** (Alternate Key=Yes, field `Key`),
Label + DeveloperDocumentation from labels.
Fields: `Key` (Int, EDT `ParametersKey`, Visible=No, AllowEdit=No),
`ERFormatMappingRecId` (Int64, EDT `ROSaftERFormatMappingRecId`).

```xpp
public class ROSaftParameters extends common
{
    /// <summary>
    /// Determines if concurrent deletes should throw exception.
    /// </summary>
    public boolean shouldThrowExceptionOnZeroDelete()
    {
        return true;
    }

    /// <summary>
    /// Finds the singleton parameters record (Key = 0) for the current company.
    /// Creates the record on first access if it does not exist yet.
    /// </summary>
    public static ROSaftParameters find(boolean _forUpdate = false)
    {
        ROSaftParameters parameters;

        parameters.selectForUpdate(_forUpdate);
        select firstonly parameters
            index KeyIdx
            where parameters.Key == 0;

        if (!parameters && !parameters.isTmp())
        {
            Company::createParameter(parameters);
        }

        return parameters;
    }

    /// <summary>
    /// Updates the parameters record and flushes the Found cache.
    /// </summary>
    public void update()
    {
        super();
        flush ROSaftParameters;
    }

    /// <summary>
    /// Prevents deletion of the singleton parameters record.
    /// </summary>
    public void delete()
    {
        throw error("@SYS23721");
    }

    /// <summary>
    /// Displays the name of the selected ER format mapping.
    /// </summary>
    [SysClientCacheDataMethod(true)]
    public display Name displayERFormatMappingName()
    {
        ERFormatMappingTable mapping;

        select firstonly Name from mapping
            where mapping.RecId == this.ERFormatMappingRecId;

        return mapping.Name;
    }

    /// <summary>
    /// Displays the description of the selected ER format mapping.
    /// </summary>
    [SysClientCacheDataMethod(true)]
    public display Description displayERFormatMappingDescription()
    {
        ERFormatMappingTable mapping;

        select firstonly Description from mapping
            where mapping.RecId == this.ERFormatMappingRecId;

        return mapping.Description;
    }
}
```

### 3.4 Form `ROSaftParameters`
Pattern: Simple List. Data source `ROSaftParameters` with
AllowCreate=No, AllowDelete=No, InsertAtEnd=No.
Grid: Int64 control bound to `ERFormatMappingRecId` + two String controls with
Data Method = display methods above.

```xpp
[Form]
public class ROSaftParameters extends FormRun
{
    /// <summary>
    /// Ensures the singleton parameters record exists before the data source loads.
    /// </summary>
    public void init()
    {
        ROSaftParameters::find();
        super();
    }

    [Control("Int64")]
    class ROSaftParameters_ERFormatMappingRecId
    {
        /// <summary>
        /// Lookup of ER format mappings by name; returns the mapping RecId.
        /// </summary>
        public void lookup()
        {
            SysTableLookup tableLookup = SysTableLookup::newParameters(
                tableNum(ERFormatMappingTable), this);
            Query query = new Query();

            query.addDataSource(tableNum(ERFormatMappingTable));

            tableLookup.addLookupfield(fieldNum(ERFormatMappingTable, Name));
            tableLookup.addLookupfield(fieldNum(ERFormatMappingTable, Description));
            tableLookup.addLookupfield(fieldNum(ERFormatMappingTable, RecId), true);
            tableLookup.parmQuery(query);
            tableLookup.performFormLookup();
        }
    }
}
```

### 3.5 Contract
```xpp
/// <summary>
/// Data contract for the RO SAF-T generation dialog (reporting period).
/// </summary>
[DataContract]
internal final class SAFTRoGenerateContract
{
    private FromDate fromDate;
    private ToDate   toDate;

    [DataMember, SysOperationLabel(literalStr("@ROSaft:FromDate")), SysOperationDisplayOrder('1')]
    public FromDate parmFromDate(FromDate _fromDate = fromDate)
    {
        fromDate = _fromDate;
        return fromDate;
    }

    [DataMember, SysOperationLabel(literalStr("@ROSaft:ToDate")), SysOperationDisplayOrder('2')]
    public ToDate parmToDate(ToDate _toDate = toDate)
    {
        toDate = _toDate;
        return toDate;
    }
}
```

### 3.6 Service (the ER handoff)
```xpp
using Microsoft.Dynamics365.LocalizationFramework;

/// <summary>
/// Generates the RO SAF-T file through Electronic reporting.
/// The ER format mapping is read from ROSaftParameters.
/// </summary>
internal final class SAFTRoGenerateService extends SysOperationServiceBase
{
    public void generate(SAFTRoGenerateContract _contract)
    {
        ERFormatMappingId formatMappingId = ROSaftParameters::find().ERFormatMappingRecId;

        if (!formatMappingId)
        {
            throw error("@ROSaft:ROSaftParametersNotSetup");
        }

        ERIFormatMappingRun formatMappingRun =
            ERObjectsFactory::createFormatMappingRunByFormatMappingId(
                formatMappingId, 'SAFT_RO.xml');

        if (formatMappingRun.parmShowPromptDialog(true))
        {
            formatMappingRun.run();
        }
    }
}
```
> Note: the contract dates are collected but not yet wired into ER parameters —
> that wiring uses `ERModelDefinitionParamsUIActionComposite` (future exercise).

### 3.7 Controller
```xpp
/// <summary>
/// Controller for the RO SAF-T generation; entry point of menu item ROSaftGenerate.
/// </summary>
internal final class SAFTRoGenerateController extends SysOperationServiceController
{
    public static SAFTRoGenerateController construct()
    {
        SAFTRoGenerateController controller = new SAFTRoGenerateController(
            classStr(SAFTRoGenerateService),
            methodStr(SAFTRoGenerateService, generate),
            SysOperationExecutionMode::Synchronous);

        controller.parmDialogCaption("@ROSaft:GenerateDialogCaption");
        return controller;
    }

    public static void main(Args _args)
    {
        SAFTRoGenerateController::construct().startOperation();
    }
}
```

### 3.8 Menu + security
- Menu items: Display `ROSaftParameters` → form; Action `ROSaftGenerate` → controller.
- `GeneralLedger.OHMS` extension → submenu **RO SAF-T** containing both references.
- Privileges: `ROSaftParametersMaintain` (entry point: display item, Access=Delete),
  `ROSaftGenerateProcess` (entry point: action item, Access=Invoke)
  → duty `ROSaftMaintainDuty` → role `ROSaftClerk`.
- Security is data → **DB sync required** before it applies.

---

## ✅ 4. Test script
1. **Setup:** General ledger > RO SAF-T > RO SAF-T parameters → lookup →
   select *SAF-T Format (RO test)* → Save (Name/Description columns confirm the pick).
2. **Guard:** clear the field, Save → Generate → expect
   *"RO SAF-T parameters are not set up…"*.
3. **Generate:** set field back → Generate → OK → ER prompt → OK →
   `SAFT_RO.xml` downloads with the Contoso header. ✔ Verified working.

---

## 🚨 5. Troubleshooting playbook (errors we personally hit + production analogues)

| # | Error | Root cause | Fix | Production relevance |
|---|-------|-----------|-----|----------------------|
| 1 | *More than one model mapping exists for the '… (Audit File)' data model… Set one as default* | Two mapping configs implement the same model ROOT; ER refuses to guess | Set **Default for model mapping = Yes** on the config **named in the error** (root-specific!) | Upgrades import new Microsoft mapping versions → ambiguity can (re)appear next to ISV mappings |
| 2 | *The configuration doesn't support the country/region of the current legal entity* | Selected config's ISO country codes exclude the legal entity's country | Select the correct config; check ISO Country/region codes on the config | Wrong config picked in parameters, or country codes changed between versions |
| 3 | *Expected format mapping has not been found* | Format has **no Completed version** — runtime API only resolves Completed | Change status > **Complete** on the format version | Classic post-upgrade state: config imported/rebased but left Draft; designer Run works, production run fails |
| 4 | Silent batch failure, "no logs" | Error swallowed by batch execution | Check **Org admin > ER > Electronic reporting jobs** + batch job retry count; re-run **interactively (Batch = No)** to surface the real error; ER execution trace via Configurations > User parameters | The customer's exact symptom |
| 5 | Package fails right after Microsoft upgrade | Derived config's base moved; ISV package not rebased/certified for new build | Check config **Prerequisites** (Applicable product versions) vs actual F&O build; ask ISV for certified version; Rebase + resolve conflicts + Complete | The leading theory for the customer case |

**Where errors/logs live:**
- Org admin > Electronic reporting > **Electronic reporting jobs** (execution results)
- Common > Inquiries > **Batch jobs** (retry count; >1 → cancel, run without batch)
- ER **execution trace**: Configurations > Configurations tab > Advanced settings >
  User parameters > Execution trace format
- Event log `Microsoft-Dynamics-ElectronicReporting/Operational` (dev machines)
- Designer: **Validate / Run / Start Debugging / Performance trace**

---

## 🎯 6. ISV call cheat sheet
1. Exact upgrade pair (from → to F&O build + platform update) and installed ISV
   package/model version.
2. **"Which version of your package is certified for our current build?"**
3. **"Has your RO format been rebased against the new Microsoft SAF-T base
   model/mapping version this update shipped?"**
4. **"Are all imported versions Completed in the customer environment?
   Any rebase-conflict flags? Are default-mapping flags and country codes intact?"**
5. **"Is the fix config-only (ER import, fast) or a deployable package
   (X++, servicing window)?"** — ISV packages with custom tables (parameters,
   ANAF code mappings, submission logs) require deployment.
6. Ask for a screen-share: run the SAF-T generation **interactively** and capture
   the real error; check ER jobs for the failed batch run.
```

---

