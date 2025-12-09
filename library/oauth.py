"""
OAuth handling for Zoho TrainerCentral API.

This module now supports dynamic credentials for ChatGPT Custom Connectors:
- OAuth 2.0 authorization-code and refresh-token flows
- api_domain/org_id propagation so domain/org are no longer hardcoded
"""

import os
import time
from typing import Any, Dict, Optional

import dotenv
import requests

dotenv.load_dotenv()


class ZohoOAuth:
    """
    Handles OAuth2 authentication for Zoho APIs used by TrainerCentral.

    Supports ChatGPT Custom Connector OAuth 2.0 (not OIDC) by allowing
    tokens, api_domain, and org_id to be injected at runtime (typically
    from the connector's OAuth callback payload).
    """

    def __init__(
        self,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        refresh_token: Optional[str] = None,
        access_token: Optional[str] = None,
        expires_at: float = 0,
        api_domain: Optional[str] = None,
        org_id: Optional[str] = None,
        domain: Optional[str] = None,
        accounts_base_url: Optional[str] = None,
    ):
        # Prefer values passed in from the caller (e.g., ChatGPT OAuth payload),
        # then fall back to environment variables for local development.
        self.client_id = (
            client_id
            or os.getenv("ZOHO_CLIENT_ID")
            or os.getenv("CLIENT_ID")
        )
        self.client_secret = (
            client_secret
            or os.getenv("ZOHO_CLIENT_SECRET")
            or os.getenv("CLIENT_SECRET")
        )
        self.refresh_token = (
            refresh_token
            or os.getenv("ZOHO_REFRESH_TOKEN")
            or os.getenv("REFRESH_TOKEN")
        )
        self.access_token = (
            access_token
            or os.getenv("ZOHO_ACCESS_TOKEN")
            or os.getenv("ACCESS_TOKEN")
        )
        # Absolute expiry timestamp (seconds since epoch)
        self.expires_at = float(
            expires_at
            or os.getenv("ACCESS_TOKEN_EXPIRES_AT", "0")
        )

        # Region-aware Zoho accounts URL (defaults to .com if unspecified)
        self.accounts_base_url = (
            accounts_base_url
            or os.getenv("ZOHO_ACCOUNTS_URL")
            or os.getenv("ACCOUNTS_URL")
            or "https://accounts.zoho.in"
        ).rstrip("/")

        # Region-specific API domain returned by Zoho OAuth responses
        self.api_domain = (
            api_domain
            or os.getenv("ZOHO_API_DOMAIN")
            or os.getenv("API_DOMAIN")
        )

        # TrainerCentral org + domain can be injected from OAuth payload
        # or environment variables. Domain falls back to api_domain when possible.
        self.org_id = (
            org_id
            or os.getenv("TRAINERCENTRAL_ORG_ID")
            or os.getenv("TC_ORG_ID")
            or os.getenv("ORG_ID")
        )
        self.domain = (
            domain
            or os.getenv("TRAINERCENTRAL_DOMAIN")
            or os.getenv("TC_DOMAIN")
            or os.getenv("DOMAIN")
            or (f"{self.api_domain}/trainercentral" if self.api_domain else None)
        )

    # ------------------------------------------------------------------ #
    # Internal helpers
    # ------------------------------------------------------------------ #
    def _token_endpoint(self) -> str:
        return f"{self.accounts_base_url}/oauth/v2/token"

    def _apply_token_response(self, result: Dict[str, Any]) -> str:
        """
        Persist token fields from the Zoho OAuth response.
        """
        if "access_token" not in result:
            raise Exception(f"Failed to acquire access token: {result}")

        self.access_token = result["access_token"]
        # Zoho returns expires_in seconds; store absolute expiry timestamp
        expires_in = int(result.get("expires_in", 3600))
        self.expires_at = time.time() + expires_in

        # Optional fields we can re-use
        self.refresh_token = result.get("refresh_token", self.refresh_token)
        self.api_domain = result.get("api_domain", self.api_domain)
        if not self.domain and self.api_domain:
            self.domain = f"{self.api_domain}/trainercentral"
        return self.access_token

    # ------------------------------------------------------------------ #
    # Public API
    # ------------------------------------------------------------------ #
    def exchange_authorization_code(
        self,
        code: str,
        redirect_uri: str,
        scope: Optional[str] = None,
        portals_base_url: Optional[str] = None,
    ) -> str:
        """
        Exchange an authorization code for access + refresh tokens.

        This is the flow ChatGPT Custom Connectors should use (OAuth 2.0),
        not OIDC. The connector will send the code/redirect_uri; we persist
        the resulting tokens for subsequent API calls.
        """
        data = {
            "code": code,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "redirect_uri": redirect_uri,
            "grant_type": "authorization_code",
        }
        if scope:
            data["scope"] = scope

        response = requests.post(self._token_endpoint(), data=data, timeout=30)
        response.raise_for_status()
        self._apply_token_response(response.json())

        # If org_id is still missing, try to derive it from portals.json.
        if not self.org_id:
            self.fetch_org_id_from_portals(portals_base_url=portals_base_url)
        return self.access_token

    def refresh_access_token(self) -> str:
        """
        Refresh the Zoho OAuth2 access token using the stored refresh token.
        """
        if not self.refresh_token:
            raise Exception(
                "Missing refresh_token. Ensure the OAuth 2.0 flow provided "
                "one (ChatGPT Custom Connector should request offline access)."
            )

        data = {
            "refresh_token": self.refresh_token,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "refresh_token",
        }

        response = requests.post(self._token_endpoint(), data=data, timeout=30)
        response.raise_for_status()
        return self._apply_token_response(response.json())

    def get_access_token(self) -> str:
        """
        Return a valid access token. If the current token is expired or missing,
        it refreshes automatically using the stored refresh token.
        """
        if not self.access_token or time.time() >= self.expires_at:
            return self.refresh_access_token()
        return self.access_token

    def set_tokens(
        self,
        access_token: str,
        expires_in: Optional[int] = None,
        refresh_token: Optional[str] = None,
        api_domain: Optional[str] = None,
        org_id: Optional[str] = None,
        domain: Optional[str] = None,
    ) -> None:
        """
        Allow callers (e.g., ChatGPT connector bootstrap) to inject tokens
        and org/context details directly.
        """
        self.access_token = access_token
        if expires_in is not None:
            self.expires_at = time.time() + int(expires_in)
        self.refresh_token = refresh_token or self.refresh_token
        self.api_domain = api_domain or self.api_domain
        self.org_id = org_id or self.org_id
        self.domain = domain or self.domain
        if not self.domain and self.api_domain:
            self.domain = f"{self.api_domain}/trainercentral"
        if not self.org_id:
            self.fetch_org_id_from_portals()

    def fetch_org_id_from_portals(self, portals_base_url: Optional[str] = None) -> Optional[str]:
        """
        Fallback: fetch portals.json to derive orgId when OAuth response
        does not include it. Requires a valid access_token.

        Args:
            portals_base_url: Optional base URL (e.g., https://myacademy.trainercentral.in).
                              If omitted, uses self.domain or api_domain/trainercentral.
        """
        if not self.access_token:
            return None

        base = portals_base_url or self.domain
        if not base and self.api_domain:
            base = f"{self.api_domain}/trainercentral"
        if not base:
            return None

        url = f"{base.rstrip('/')}/portals.json"
        headers = {"Authorization": f"Bearer {self.access_token}"}
        try:
            resp = requests.get(url, headers=headers, timeout=30)
            resp.raise_for_status()
            data = resp.json()
            # Expecting a list or dict containing an org identifier
            # Example: { "portals": [ { "id": "...", ... } ] }
            portals = data.get("portals") if isinstance(data, dict) else data
            if isinstance(portals, list) and portals:
                first = portals[0]
                org_candidate = first.get("id") if isinstance(first, dict) else None
                if org_candidate:
                    self.org_id = org_candidate
                    return self.org_id
        except Exception:
            # Best-effort; leave org_id unset if this fails.
            return None
        return None
