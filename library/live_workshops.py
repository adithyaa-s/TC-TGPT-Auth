import requests

from .common_utils import (
    DateConverter,
    TrainerCentralContext,
    get_trainercentral_context,
)


class TrainerCentralLiveWorkshops:
    """
    Handles GLOBAL Live Workshops (deliveryMode = 3).
    These are NOT associated with any course.

    API References:
      Create Workshop:
        POST /api/v4/<orgId>/sessions.json

      Edit Workshop:
        PUT /api/v4/<orgId>/sessions/<sessionId>.json

      Create Occurrence (Talk):
        POST /api/v4/<orgId>/talks.json

      Edit Occurrence:
        PUT /api/v4/<orgId>/talks/<talkId>.json

      Cancel Workshop or Occurrence:
        PUT with { "isCancelled": true }
    """

    def __init__(self, context: TrainerCentralContext | None = None):
        self.context = context or get_trainercentral_context()
        self.base_url = self.context.base_url
        self.oauth = self.context.oauth
        self.date_converter = DateConverter()


    def create_global_workshop(
        self,
        name: str,
        description_html: str,
        start_time_str: str,
        end_time_str: str
    ) -> dict:
        """
        Create a GLOBAL live workshop.

        API:
            POST /api/v4/<orgId>/sessions.json

        deliveryMode = 3  → live workshop 

        Args (LLM REQUIRED FORMAT):
            start_time_str: "DD-MM-YYYY HH:MMAM/PM"
            end_time_str:   "DD-MM-YYYY HH:MMAM/PM"

        Returns:
            dict: API response
        """

        start_ms = int(self.date_converter.convert_date_to_time(start_time_str))
        end_ms = int(self.date_converter.convert_date_to_time(end_time_str))

        url = f"{self.base_url}/sessions.json"
        headers = {
            "Authorization": f"Bearer {self.oauth.get_access_token()}",
            "Content-Type": "application/json",
        }

        body = {
            "session": {
                "name": name,
                "description": description_html,
                "deliveryMode": 3,
                "scheduledTime": start_ms,
                "scheduledEndTime": end_ms,
                "durationTime": end_ms - start_ms
            }
        }

        return requests.post(url, json=body, headers=headers).json()



    def update_workshop(self, session_id: str, updates: dict) -> dict:
        """
        Update an existing global live workshop.

        Args:
            session_id (str): workshop sessionId
            updates (dict): fields to update
                {
                   "name": "...",
                   "scheduledTime": <ms>,
                   "scheduledEndTime": <ms>,
                   "description": "<html>",
                   "isCancelled": true     # for cancellation
                }

        Returns:
            dict: API response
        """

        url = f"{self.base_url}/sessions/{session_id}.json"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.oauth.get_access_token()}"
        }

        payload = {"session": updates}
        return requests.put(url, json=payload, headers=headers).json()


    def create_occurrence(self, talk_data: dict) -> dict:
        """
        Create an occurrence (talk) for a workshop.

        Args:
            talk_data (dict):
                {
                    "scheduledTime": <ms>,
                    "scheduledEndTime": <ms>,
                    "sessionId": "<parentSessionId>",
                    "durationTime": <ms>,
                    "recurrence": { ... } # optional
                }

        Returns:
            dict: API response
        """
        url = f"{self.base_url}/talks.json"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.oauth.get_access_token()}"
        }

        payload = {"talk": talk_data}
        return requests.post(url, json=payload, headers=headers).json()


    def update_occurrence(self, talk_id: str, updates: dict) -> dict:
        """
        Update or cancel a workshop occurrence.

        Args:
            talk_id (str): talkId
            updates (dict):
                {
                    "scheduledTime": <ms>,
                    "scheduledEndTime": <ms>,
                    "informRegistrants": true/false,
                    "isCancelled": true         # for cancellation
                }

        Returns:
            dict
        """

        url = f"{self.base_url}/talks/{talk_id}.json"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.oauth.get_access_token()}"
        }

        payload = {"talk": updates}
        return requests.put(url, json=payload, headers=headers).json()

    def list_all_upcoming_workshops(self, filter_type: int = 5, limit: int = 50, si: int = 0) -> dict:
        """
        Fetch all upcoming global live workshops.
        Uses: GET /talks.json?filter=&limit=&si=

        Args:
            filter_type (int): 1 = your upcoming; 5 = all upcoming (admin).
            limit (int): number of items.
            si (int): start index.

        Returns:
            dict: API response with sessions list.
        """
        url = f"{self.base_url}/talks.json?filter={filter_type}&limit={limit}&si={si}"
        headers = {
            "Authorization": f"Bearer {self.oauth.get_access_token()}"
        }
        return requests.get(url, headers=headers).json()

    def invite_user_to_workshop(self, session_id: str, email: str, role: int = 3, source: int = 1) -> dict:
        """
        Invite / add a member (by email) to a course-linked live workshop / session.

        Args:
            session_id (str): ID of the existing session / live workshop.
            email (str): Email address of the user to invite.
            role (int): Role code in session (e.g. 3 = attendee — adjust as per your setup).
            source (int): Source indicator (per TrainerCentral API).

        Returns:
            dict: API response JSON.
        """
        url = f"{self.base_url}/sessionMembers.json"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.oauth.get_access_token()}"
        }
        body = {
            "sessionMembers": [
                {
                    "emailId": email,
                    "sessionId": session_id,
                    "role": role,
                    "source": source
                }
            ]
        }
        resp = requests.post(url, json=body, headers=headers)
        resp.raise_for_status()
        return resp.json()


