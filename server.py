"""
Lightweight HTTP server to expose the well-known OAuth metadata required by
ChatGPT Apps SDK / MCP authorization spec. This does NOT implement Zoho OAuth;
it simply advertises metadata so ChatGPT can complete the OAuth flow against
Zoho and then call this MCP server with the bearer token.
"""

import os
from typing import Dict, List

from fastapi import FastAPI, Response

# Base URL where this MCP server is reachable by ChatGPT (Render public URL)
RESOURCE_BASE_URL = os.getenv("RESOURCE_BASE_URL", "https://tc-tgpt-auth.onrender.com").rstrip("/")

# Zoho accounts base (region-specific)
ZOHO_ACCOUNTS_URL = os.getenv("ZOHO_ACCOUNTS_URL", "https://accounts.zoho.in").rstrip("/")

# Scopes we want to request from ChatGPT for TrainerCentral
DEFAULT_SCOPES: List[str] = [
    "TrainerCentral.courseapi.ALL",
    "TrainerCentral.sessionapi.ALL",
    "TrainerCentral.sectionapi.ALL",
    "TrainerCentral.talkapi.ALL",
    "TrainerCentral.userapi.ALL",
    "TrainerCentral.portalapi.ALL",
]

app = FastAPI()


def resource_metadata() -> Dict:
    """
    Metadata for this protected resource, per RFC 9728 / Apps SDK guide.
    """
    return {
        "resource": RESOURCE_BASE_URL,
        "authorization_servers": [ZOHO_ACCOUNTS_URL],
        "scopes_supported": DEFAULT_SCOPES,
        "resource_documentation": f"{RESOURCE_BASE_URL}/docs",
    }


def oauth_authorization_server_metadata() -> Dict:
    """
    Static OAuth authorization-server metadata. Since we cannot modify Zoho's
    well-known, we mirror the essential fields here and point to Zoho endpoints.
    """
    return {
        "issuer": ZOHO_ACCOUNTS_URL,
        "authorization_endpoint": f"{ZOHO_ACCOUNTS_URL}/oauth/v2/auth",
        "token_endpoint": f"{ZOHO_ACCOUNTS_URL}/oauth/v2/token",
        # ChatGPT uses PKCE (S256)
        "code_challenge_methods_supported": ["S256"],
        # dynamic client registration is not available for Zoho; ChatGPT can skip if not provided
        # "registration_endpoint": "<optional-if-you-host-a-proxy>",
        "scopes_supported": DEFAULT_SCOPES,
    }


@app.get("/.well-known/oauth-protected-resource")
async def well_known_oauth_protected_resource():
    return resource_metadata()


@app.get("/.well-known/oauth-authorization-server")
async def well_known_oauth_authorization_server():
    return oauth_authorization_server_metadata()


@app.get("/healthz")
async def healthz():
    return {"status": "ok"}


def make_unauthorized_response(scope: str | None = None) -> Response:
    """
    Helper to emit a WWW-Authenticate challenge. This can be used by
    MCP tool handlers when a token is missing/invalid to prompt ChatGPT
    to show the OAuth UI.
    """
    challenge = f'Bearer resource_metadata="{RESOURCE_BASE_URL}/.well-known/oauth-protected-resource"'
    if scope:
        challenge += f', scope="{scope}"'
    headers = {"WWW-Authenticate": challenge}
    return Response(status_code=401, headers=headers)

