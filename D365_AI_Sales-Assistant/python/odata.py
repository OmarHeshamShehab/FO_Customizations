"""
odata.py — D365 F&O OData Integration Layer
============================================
Handles all communication with Microsoft Dynamics 365 Finance & Operations
via the OData REST API.

Responsibilities:
  - Azure AD authentication using client credentials flow
  - Token acquisition and management
  - OData entity fetching with filtering, sorting, and pagination
  - Error handling and logging for all OData operations

Dependencies:
  - requests: HTTP client for synchronous OData calls
  - config.py: Azure AD credentials and OData base URL

Usage:
  from odata import fetch_odata, fetch_odata_entity
  records = fetch_odata('SalesOrderHeadersV2', filters="SalesOrderNumber eq '000697'")
  customers = fetch_odata_entity('CustomersV3', filters="dataAreaId eq 'usmf'")

Notes:
  - A new token is acquired on every call (stateless design for POC simplicity)
  - SSL verification is disabled for VHD local development (verify=False)
  - OData timeout is set to 120 seconds to accommodate AOS wake-up time
  - SalesOrderStatus enum cannot be filtered in OData URL — filter in Python instead
  - fetch_odata automatically adds dataAreaId company filter to all queries
  - fetch_odata_entity accepts a raw filter string for entities like CustomersV3
    that require different filter construction
"""

import logging
import requests

from config import (
    ODATA_BASE_URL, COMPANY,
    AAD_TENANT_ID, AAD_CLIENT_ID,
    AAD_CLIENT_SECRET, AAD_RESOURCE, LOGIN_URL
)

log = logging.getLogger(__name__)


# ── FIELDS ────────────────────────────────────────────────────────────────────

# Standard set of sales order header fields fetched for every query.
# Covers status, dates, customer info, delivery, payment, and origin.
HEADER_FIELDS = (
    "SalesOrderNumber,OrderingCustomerAccountNumber,SalesOrderName,"
    "SalesOrderStatus,SalesOrderProcessingStatus,OrderCreationDateTime,"
    "RequestedShippingDate,ConfirmedShippingDate,CurrencyCode,"
    "PaymentTermsName,CustomerPaymentMethodName,DeliveryModeCode,"
    "DeliveryTermsCode,SalesOrderOriginCode,SalesOrderPoolId,"
    "DeliveryAddressName,DeliveryAddressCity,DeliveryAddressStateId,"
    "DeliveryAddressCountryRegionId"
)


# ── AUTHENTICATION ─────────────────────────────────────────────────────────────

def get_token():
    """
    Acquire an OAuth2 Bearer token from Azure AD using client credentials.

    Uses the client_credentials grant type — no user interaction required.
    The token is used to authenticate all OData API calls to F&O.

    Returns:
        str: Bearer access token if successful
        None: If token acquisition fails
    """
    token_url = f"{LOGIN_URL}{AAD_TENANT_ID}/oauth2/token"

    data = {
        "grant_type":    "client_credentials",
        "client_id":     AAD_CLIENT_ID,
        "client_secret": AAD_CLIENT_SECRET,
        "resource":      AAD_RESOURCE,
    }

    try:
        r = requests.post(token_url, data=data, timeout=30)

        if r.status_code == 200:
            log.info("Token acquired successfully")
            return r.json().get("access_token")

        log.error(f"Token error {r.status_code}: {r.text[:300]}")
        return None

    except Exception as e:
        log.error(f"Token request failed: {e}")
        return None


# ── ODATA FETCH — SALES ORDERS ────────────────────────────────────────────────

def fetch_odata(entity, filters="", select="", top=50, orderby=""):
    """
    Fetch records from a D365 F&O OData entity.

    Automatically applies company filter (dataAreaId) to all queries.
    Acquires a fresh Bearer token before each request.

    Use this function for SalesOrderHeadersV2 and similar entities
    where the company filter needs to be automatically appended.

    Args:
        entity  (str): OData entity name e.g. 'SalesOrderHeadersV2'
        filters (str): Additional OData filter expression
                       e.g. "SalesOrderNumber eq '000697'"
                       The dataAreaId filter is added automatically.
        select  (str): Comma-separated list of fields to return
        top     (int): Maximum number of records to return (default 50)
        orderby (str): OData orderby expression
                       e.g. "OrderCreationDateTime desc"

    Returns:
        list: List of record dictionaries, empty list on error

    Notes:
        - SalesOrderStatus enum values must be filtered in Python after fetch
          because F&O OData does not support direct enum string filtering
        - Use top=5000 for backorder queries to ensure all records are fetched
    """
    # Always scope query to the configured company
    base_filter = f"dataAreaId eq '{COMPANY}'"
    full_filter = f"{base_filter} and {filters}" if filters else base_filter

    params = {"$filter": full_filter, "$top": top}
    if select:
        params["$select"] = select
    if orderby:
        params["$orderby"] = orderby

    url   = f"{ODATA_BASE_URL}/{entity}"
    token = get_token()

    if not token:
        log.error("Could not get auth token — aborting OData fetch")
        return []

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept":        "application/json",
        "OData-Version": "4.0",
    }

    try:
        log.info(f"OData -> {url} | filter: {full_filter} | top: {top}")
        r = requests.get(
            url,
            params=params,
            headers=headers,
            verify=False,   # SSL verification disabled for VHD local dev
            timeout=120     # Long timeout to allow AOS to wake from idle
        )

        if r.status_code == 200:
            records = r.json().get("value", [])
            log.info(f"OData returned {len(records)} records from {entity}")
            return records

        log.warning(f"OData {r.status_code}: {r.text[:200]}")
        return []

    except Exception as e:
        log.error(f"OData error: {e}")
        return []


# ── ODATA FETCH — GENERIC ENTITY ──────────────────────────────────────────────

def fetch_odata_entity(entity, filters="", select="", top=50):
    """
    Fetch records from any D365 F&O OData entity using a raw filter string.

    Unlike fetch_odata(), this function does NOT automatically append the
    dataAreaId company filter. The caller is responsible for including
    all required filters in the filters parameter.

    Use this function for entities like CustomersV3 where the filter
    construction differs from the standard sales order pattern.

    Args:
        entity  (str): OData entity name e.g. 'CustomersV3'
        filters (str): Complete filter string including dataAreaId if needed
                       e.g. "dataAreaId eq 'usmf' and CustomerAccount eq 'US-001'"
        select  (str): Comma-separated list of fields to return
        top     (int): Maximum number of records to return (default 50)

    Returns:
        list: List of record dictionaries, empty list on error

    Example:
        customers = fetch_odata_entity(
            'CustomersV3',
            filters="dataAreaId eq 'usmf'",
            select="CustomerAccount,CreditLimit,PaymentTerms",
            top=100
        )
    """
    params = {"$top": top}

    # Only add filter parameter if a filter was provided
    if filters:
        params["$filter"] = filters

    if select:
        params["$select"] = select

    url   = f"{ODATA_BASE_URL}/{entity}"
    token = get_token()

    if not token:
        log.error("Could not get auth token — aborting OData fetch")
        return []

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept":        "application/json",
        "OData-Version": "4.0",
    }

    try:
        log.info(f"OData -> {url} | filters: {filters} | top: {top}")
        r = requests.get(
            url,
            params=params,
            headers=headers,
            verify=False,   # SSL verification disabled for VHD local dev
            timeout=120     # Long timeout to allow AOS to wake from idle
        )

        if r.status_code == 200:
            records = r.json().get("value", [])
            log.info(f"OData returned {len(records)} records from {entity}")
            return records

        log.warning(f"OData {r.status_code}: {r.text[:200]}")
        return []

    except Exception as e:
        log.error(f"OData error: {e}")
        return []