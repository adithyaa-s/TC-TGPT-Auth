import requests

from .common_utils import (
    TrainerCentralCommon,
    TrainerCentralContext,
    get_trainercentral_context,
)

class TrainerCentralLessons:
    def __init__(self, context: TrainerCentralContext | None = None):
        self.context = context or get_trainercentral_context()
        self.base_url = self.context.base_url
        self.oauth = self.context.oauth
        self.common = TrainerCentralCommon(context=self.context)

    def create_lesson_with_content(
        self,
        lesson_data: dict,
        content_html: str,
        content_filename: str = "Content"
    ) -> dict:
        """
        Create a lesson (session) with full rich-text content.

        Args:
            lesson_data (dict): session metadata, e.g.
                {
                   "name": "Lesson Title",
                   "courseId": "...",
                   "sectionId": "...",
                   "deliveryMode": 4,
                   # optionally: description (short summary/blurb)
                }
            content_html (str): full lesson body (HTML text)
            content_filename (str, optional): filename/title used for content upload

        Returns:
            dict: {
              "lesson": {... response from session creation ...},
              "content": {... response from content upload ...}
            }
        """
        # Step 1: create session
        url = f"{self.base_url}/sessions.json"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.oauth.get_access_token()}"
        }
        payload = {"session": lesson_data}
        create_resp = requests.post(url, json=payload, headers=headers).json()

        # Step 2: upload content
        session_obj = create_resp.get("session")
        session_id = None
        if isinstance(session_obj, dict):
            session_id = session_obj.get("id") or session_obj.get("sessionId")
        if not session_id:
            raise RuntimeError(f"Failed to find sessionId in response: {create_resp}")

        content_url = f"{self.base_url}/session/{session_id}/createTextFile.json"
        content_headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.oauth.get_access_token()}"
        }
        content_body = {
            "richTextContent": content_html,
            "filename": content_filename
        }
        content_resp = requests.post(content_url, json=content_body, headers=content_headers).json()

        return {
            "lesson": create_resp,
            "content": content_resp
        }

    def update_lesson(self, session_id: str, updates: dict) -> dict:
        url = f"{self.base_url}/sessions/{session_id}.json"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.oauth.get_access_token()}"
        }
        payload = {"session": updates}
        return requests.put(url, json=payload, headers=headers).json()

    def delete_lesson(self, session_id: str) -> dict:
        return self.common.delete_resource("sessions", session_id)
