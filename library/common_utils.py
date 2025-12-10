# library/common_utils.py

import os
import logging
from datetime import datetime
from typing import Optional

import requests

from .oauth import ZohoOAuth

logger = logging.getLogger(__name__)


class TrainerCentralContext:
    """
    Central configuration carrier for domain/org and OAuth client.

    The context can be populated from ChatGPT Custom Connector OAuth payload
    (injected as environment variables) or from a local .env file.
    
    IMPORTANT: Each request should create its own context instance to avoid
    token conflicts between concurrent users.
    """

    def __init__(
        self,
        domain: Optional[str] = None,
        org_id: Optional[str] = None,
        oauth: Optional[ZohoOAuth] = None,
    ):
        self.oauth = oauth or ZohoOAuth()
        self.domain = (domain or self.oauth.domain or os.getenv("API_DOMAIN") or "").rstrip("/")

        # Prefer provided org_id, then OAuth-derived org_id
        self.org_id = org_id or self.oauth.org_id or os.getenv("TRAINERCENTRAL_ORG_ID") or os.getenv("ORG_ID")
        
        # If still no org_id, try to fetch from portals
        if not self.org_id:
            try:
                self.oauth.fetch_org_id_from_portals(portals_base_url=self.domain or None)
                self.org_id = self.oauth.org_id
            except Exception as e:
                logger.warning(f"Could not fetch org_id from portals: {e}")

    @property
    def base_url(self) -> str:
        """Get the base API URL for TrainerCentral"""
        if not self.domain:
            raise ValueError(
                "DOMAIN/API_DOMAIN missing. Provide it via OAuth payload or .env."
            )
        if not self.org_id:
            # Last-chance fetch
            try:
                self.oauth.fetch_org_id_from_portals(portals_base_url=self.domain)
                self.org_id = self.oauth.org_id
            except Exception as e:
                logger.error(f"Failed to fetch org_id: {e}")
        
        if not self.org_id:
            raise ValueError(
                "ORG_ID missing. Provide it via OAuth payload, .env, or ensure portals.json is reachable."
            )
        return f"{self.domain}/api/v4/{self.org_id}"


# Global context for backward compatibility (not recommended for concurrent requests)
_default_context: Optional[TrainerCentralContext] = None


def get_trainercentral_context() -> TrainerCentralContext:
    """
    Get or create a default context instance.
    
    WARNING: This global context is not suitable for concurrent multi-user requests.
    For per-request contexts (recommended), create a new TrainerCentralContext 
    instance with the specific OAuth token for each request.
    """
    global _default_context
    if _default_context is None:
        _default_context = TrainerCentralContext()
    return _default_context


class TrainerCentralCommon:
    """
    Shared helper for common TrainerCentral API operations.
    Provides base URL, OAuth token, and generic delete functionality.
    """

    def __init__(self, context: Optional[TrainerCentralContext] = None):
        self.context = context or get_trainercentral_context()
        self.base_url = self.context.base_url
        self.oauth = self.context.oauth

    def delete_resource(self, resource: str, resource_id: str) -> dict:
        """
        Delete a generic resource.

        Args:
            resource (str): the resource path (e.g. "sessions", "courses", "course/<courseId>/sections")
            resource_id (str): the ID of the resource to delete.

        Returns:
            dict: API response JSON.
        """
        request_url = f"{self.base_url}/{resource}/{resource_id}.json"
        headers = {
            "Authorization": f"Bearer {self.oauth.get_access_token()}"
        }
        
        try:
            response = requests.delete(request_url, headers=headers, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP error deleting {resource}/{resource_id}: {e}")
            if e.response.status_code == 401:
                # Token may be expired, try to refresh
                try:
                    self.oauth.refresh_access_token()
                    headers["Authorization"] = f"Bearer {self.oauth.get_access_token()}"
                    response = requests.delete(request_url, headers=headers, timeout=30)
                    response.raise_for_status()
                    return response.json()
                except Exception as refresh_error:
                    logger.error(f"Token refresh failed: {refresh_error}")
                    raise
            raise
        except Exception as e:
            logger.error(f"Error deleting {resource}/{resource_id}: {e}")
            raise


class DateConverter:
    def convert_date_to_time(self, givenDate: str) -> str:
        """ 
        Convert a given date-time in the format DD-MM-YYYY HH:MMAM/PM to milliseconds 
        since the Unix epoch (January 1, 1970).
        
        Args:
            givenDate (str): The date-time string in DD-MM-YYYY HH:MMAM/PM format.
        
        Returns:
            str: The equivalent time in milliseconds since Unix epoch.
        
        Example:
            convert_date_to_time("29-11-2025 4:30PM") -> "1732882800000"
        """
        try:
            date_str, time_str = givenDate.split() 
            day, month, year = map(int, date_str.split('-'))
            time_obj = datetime.strptime(time_str, "%I:%M%p")  
            target_date = datetime(year, month, day, time_obj.hour, time_obj.minute)
            milliseconds = int(target_date.timestamp() * 1000)
            return str(milliseconds)
        except Exception as e:
            logger.error(f"Error converting date '{givenDate}': {e}")
            raise ValueError(f"Invalid date format. Expected DD-MM-YYYY HH:MMAM/PM, got: {givenDate}")