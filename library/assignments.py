# library/assignments.py
import requests

from .common_utils import (
    TrainerCentralCommon,
    TrainerCentralContext,
    get_trainercentral_context,
)


class TrainerCentralAssignments:
    def __init__(self, context: TrainerCentralContext | None = None):
        self.context = context or get_trainercentral_context()
        self.base_url = self.context.base_url
        self.oauth = self.context.oauth
        self.common = TrainerCentralCommon(context=self.context)

    def create_assignment(self, assignment_data: dict) -> dict:
        """
        Create an assignment under a course/chapter (session with deliveryMode=7).
        """
        url = f"{self.base_url}/sessions.json"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.oauth.get_access_token()}"
        }
        payload = {"session": assignment_data}
        return requests.post(url, json=payload, headers=headers).json()

    def add_text_instructions(self,
                              session_id: str,
                              html_content: str,
                              filename: str = "Instructions",
                              view_type: int = 4) -> dict:
        """
        Attach rich-text instructions (or description) to a session (assignment/lesson).

        Args:
            session_id: str — ID of the session to attach instructions to.
            html_content: str — HTML or rich-text string for the instructions.
            filename: str — Title/filename for the instructions text.
            view_type: int — ViewType as used by UI (observed as 4 in browser trace).

        Returns:
            dict: API response from the text-file creation call.
        """
        url = f"{self.base_url}/session/{session_id}/createTextFile.json"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.oauth.get_access_token()}"
        }
        body = {
            "richTextContent": html_content,
            "filename": filename,
            "viewType": view_type
        }
        return requests.post(url, json=body, headers=headers).json()

    def create_assignment_with_instructions(self,
                                            assignment_data: dict,
                                            instruction_html: str,
                                            instruction_filename: str = "Instructions",
                                            view_type: int = 4) -> dict:
        """
        Create an assignment AND attach instructions text in one go.

        Returns a dict containing:
          - "assignment": response from create assignment
          - "instructions": response from adding instructions (or None on failure)
        """
        create_resp = self.create_assignment(assignment_data)

        session = create_resp.get("session") or create_resp.get("session")
        session_id = None
        if isinstance(session, dict):
            session_id = session.get("id") or session.get("sessionId")
        if not session_id:
            raise RuntimeError(f"Assignment created but sessionId missing: {create_resp}")

        instr_resp = self.add_text_instructions(session_id,
                                                instruction_html,
                                                filename=instruction_filename,
                                                view_type=view_type)

        return {
            "assignment": create_resp,
            "instructions": instr_resp
        }

    def delete_assignment(self, session_id: str) -> dict:
        """
        Delete an assignment / session by session ID.
        Uses DELETE /sessions/{sessionId}.json
        """
        return self.common.delete_resource("sessions", session_id)
