# OHMS Service for Dynamics 365 Finance and Operations

## 📄 Overview

This project implements a simple **custom service** in X++ within Microsoft Dynamics 365 Finance and Operations (D365 F&O).  
The service provides a sample **"Create"** operation that demonstrates the correct usage of:
- Data contracts (`ohmsRequest`, `ohmsResponse`)
- Service class (`ohmsService`)
- Secure .NET interop via `InteropPermission`
- Company context switching via `changecompany`
- Proper error handling and response patterns

---

## 🧩 Components

### 1. `ohmsRequest`
Defines the input contract for the service.  
Used to pass the **company context** (`dataAreaId`) in which the operation should run.

**Key Field:**
- `dataAreaId` — The target legal entity ID.

```x++
[DataContractAttribute]
class ohmsRequest
{
    private str dataAreaId;

    [DataMember("dataAreaId")]
    public str parmDataAreaId(str _value = dataAreaId)
    {
        if (!prmIsDefault(_value))
        {
            dataAreaId = _value;
        }
        return dataAreaId;
    }
}
```

---

### 2. `ohmsResponse`
Defines the output contract for the service, encapsulating success, error, and debug information.

**Key Fields:**
- `Success` — "true" or "false"
- `ErrorMessage` — descriptive error message
- `DebugMessage` — internal diagnostic text

```x++
[DataContractAttribute]
class ohmsResponse
{
    private str errorMessage;
    private str success;
    private str debugMessage;

    [DataMember("ErrorMessage")]
    public str parmErrorMessage(str _value = errorMessage)
    {
        if (!prmIsDefault(_value))
            errorMessage = _value;
        return errorMessage;
    }

    [DataMember("Success")]
    public str parmSuccess(str _value = success)
    {
        if (!prmIsDefault(_value))
            success = _value;
        return success;
    }

    [DataMember("debugMessage")]
    public str parmDebugMessage(str _value = debugMessage)
    {
        if (!prmIsDefault(_value))
            debugMessage = _value;
        return debugMessage;
    }
}
```

---

### 3. `ohmsService`
Implements the main logic for the OHMS operations.  
Contains a single method named `Create` that executes inside the target company context.

**Key Features:**
- Asserts and reverts CLR interop permissions.
- Uses `changecompany` for cross-company execution.
- Returns structured responses for all success/failure paths.

```x++
public class ohmsService
{
    public ohmsResponse Create(ohmsRequest _request)
    {
        ohmsResponse response = new ohmsResponse();
        new InteropPermission(InteropKind::ClrInterop).assert();

        try
        {
            str company = _request.parmDataAreaId();

            if (!company)
                throw error("dataAreaId cannot be empty.");

            changecompany (company)
            {
                response.parmDebugMessage(strFmt("Hello World from %1", company));
                response.parmSuccess("true");
            }
        }
        catch (Exception::CLRError)
        {
            System.Exception netEx = CLRInterop::getLastException();
            response.parmSuccess("false");
            response.parmErrorMessage(netEx.ToString());
        }
        catch
        {
            response.parmSuccess("false");
            response.parmErrorMessage("An unknown X++ exception occurred.");
        }

        CodeAccessPermission::revertAssert();
        return response;
    }
}
```

---

## 🛠️ Configuration Steps

### Step 1: Create the Service
1. In **AOT → Services**, create a new service named:
   ```
   ohmsService
   ```
2. Set the **Class** property to:
   ```
   ohmsService
   ```
3. In the **Methods** node, add the `Create` method.

---

### Step 2: Create the Service Group
1. In **AOT → Service Groups**, create a new service group named:
   ```
   ohmsServiceGroup
   ```
2. Add the `ohmsService` service to this group.
3. Set **Auto Deploy** to `Yes` to ensure deployment during package synchronization.

---

### Step 3: Deploy the Service
1. Build and synchronize your model.
2. Restart the IIS AOS service (optional but recommended):
   ```bash
   iisreset
   ```
3. Verify service availability via:
   ```
   https://<your_env>.cloud.onebox.dynamics.com/api/services
   ```

---

## 🔍 Testing via Postman

### 1. Set up the request
- **Method:** `POST`
- **URL:**
  ```
  https://usnconeboxax1aos.cloud.onebox.dynamics.com/api/services/ohmsServiceGroup/ohmsService/Create
  ```
- **Headers:**
  | Key | Value |
  |-----|--------|
  | Content-Type | application/json |
  | Authorization | Bearer `<your-access-token>` |

> 🔑 You must generate a valid **OAuth2 token** via Azure AD for your D365 environment.

---

### 2. Request Body (Raw JSON)

```json
{
    "_request": {
        "dataAreaId": "usmf"
    }
}
```

---

### 3. Example Response

```json
{
    "Success": "true",
    "ErrorMessage": "",
    "debugMessage": "Hello World from usmf"
}
```

---

## ✅ Notes

- Always call `CodeAccessPermission::revertAssert()` after asserting permissions.
- Use `try/catch` blocks to isolate X++ and CLR errors separately.
- The `changecompany` statement is critical for ensuring proper data isolation.
- This service pattern can be extended to include CRUD or integration operations.

---
