"""
TrainerCentral Chapters (Sections) API Wrapper.
"""

import requests

from .common_utils import TrainerCentralContext, get_trainercentral_context


class TrainerCentralChapters:
    """
    Provides helper functions to interact with TrainerCentral's
    chapter (section) APIs.
    """

    def __init__(self, context: TrainerCentralContext | None = None):
        self.context = context or get_trainercentral_context()
        self.base_url = self.context.base_url
        self.oauth = self.context.oauth

    def create_chapter(self, section_data: dict):
        """
        Create a chapter under a course.

        API (Create chapter) details:
        - Method: POST
        - Endpoint: /api/v4/<orgId>/sections.json
        - OAuth Scope: TrainerCentral.sectionapi.CREATE

        Body:
        {
            "section": {
                "courseId": "<courseId>",
                "name": "<chapter name>"
            }
        }

        Args:
            section_data (dict): e.g.
                {
                    "courseId": "3000094000002000004",
                    "name": "Introduction"
                }

        Returns:
            dict: API response containing the created section.
        """
        request_url = f"{self.base_url}/sections.json"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.oauth.get_access_token()}",
        }
        data = {"section": section_data}

        return requests.post(request_url, json=data, headers=headers).json()

    def update_chapter(self, course_id: str, section_id: str, updates: dict):
        """
        Edit a chapter name or reorder a chapter inside a course.

        API (Edit chapter) details:
        - Method: PUT
        - Endpoint:
          /api/v4/<orgId>/course/<courseId>/sections/<sectionId>.json
        - OAuth Scope: TrainerCentral.sectionapi.UPDATE

        Body:
        {
            "section": {
                "name": "<chapter name>",
                "sectionIndex": 0        # only when reordering
            }
        }

        Args:
            course_id (str): ID of the course that owns the chapter.
            section_id (str): ID of the chapter (section).
            updates (dict): fields to update.

        Returns:
            dict: API response containing the updated section.
        """
        request_url = (
            f"{self.base_url}/course/{course_id}/sections/{section_id}.json"
        )
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.oauth.get_access_token()}",
        }
        data = {"section": updates}

        return requests.put(request_url, json=data, headers=headers).json()

    def delete_chapter(self, course_id: str, section_id: str):
        """
        Delete a chapter from a course.

        API (Delete chapter) details:
        - Method: DELETE
        - Endpoint:
          /api/v4/<orgId>/course/<courseId>/sections/<sectionId>.json
        - OAuth Scope: TrainerCentral.sectionapi.DELETE

        Args:
            course_id (str): ID of the course.
            section_id (str): ID of the chapter (section).

        Returns:
            dict: Response JSON from the delete call.
        """
        request_url = (
            f"{self.base_url}/course/{course_id}/sections/{section_id}.json"
        )
        headers = {
            "Authorization": f"Bearer {self.oauth.get_access_token()}",
        }

        return requests.delete(request_url, headers=headers).json()
