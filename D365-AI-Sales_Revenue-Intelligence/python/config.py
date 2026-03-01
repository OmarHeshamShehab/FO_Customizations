import os
from dotenv import load_dotenv

load_dotenv()

ODATA_BASE_URL    = os.getenv("ODATA_BASE_URL")
COMPANY           = os.getenv("COMPANY")

AAD_TENANT_ID     = os.getenv("AAD_TENANT_ID")
AAD_CLIENT_ID     = os.getenv("AAD_CLIENT_ID")
AAD_CLIENT_SECRET = os.getenv("AAD_CLIENT_SECRET")
AAD_RESOURCE      = os.getenv("AAD_RESOURCE")
LOGIN_URL         = os.getenv("LOGIN_URL")

OLLAMA_URL        = os.getenv("OLLAMA_URL")
OLLAMA_MODEL      = os.getenv("OLLAMA_MODEL")

HOST              = os.getenv("HOST", "0.0.0.0")
PORT              = int(os.getenv("PORT", 8000))