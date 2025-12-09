"""
TrainerCentral Course Management API Wrapper.
"""

import requests

from .common_utils import TrainerCentralContext, get_trainercentral_context


class TrainerCentralCourses:
    """
    Provides helper functions to interact with TrainerCentral's course APIs.
    """

    def __init__(self, context: TrainerCentralContext | None = None):
        self.context = context or get_trainercentral_context()
        self.base_url = self.context.base_url
        self.oauth = self.context.oauth

    def post_course(self, course_data: dict):
        """
        Create a new course in TrainerCentral.

        API (Create Course) details:
        - Method: POST  
        - Endpoint: /api/v4/{orgId}/courses.json  
        - OAuth Scope: TrainerCentral.courseapi.CREATE  

        Body format:
        {
            "course": {
                "courseName": "<Course Title>",
                "subTitle": "<Subtitle>",
                "description": "<Description>",
                "courseCategories": [
                    {"categoryName": "Category1"},
                    {"categoryName": "Category2"}
                ]
            }
        }

        Returns:
            dict: API response containing created course, ticket, category mapping, etc.
        """
        request_url = f"{self.base_url}/courses.json"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.oauth.get_access_token()}"
        }
        data = {"course": course_data}

        return requests.post(request_url, json=data, headers=headers).json()

    def get_course(self, course_id: str):
        """
        Fetch the details of a single course.

        API (View Course) details:
        - Method: GET  
        - Endpoint: /api/v4/{orgId}/courses/{courseId}.json  

        Returns:
            dict: Contains course details such as:
                - id / courseId  
                - courseName  
                - subTitle  
                - description  
                - links to sessions, tickets, etc.
        """
        request_url = f"{self.base_url}/courses/{course_id}.json"
        headers = {"Authorization": f"Bearer {self.oauth.get_access_token()}"}

        return requests.get(request_url, headers=headers).json()

    def list_courses(self):
        """
        List all courses (or paginated subset) from TrainerCentral.

        API (List Courses) details:
        - Method: GET  
        - Endpoint: /api/v4/{orgId}/courses.json  
        - Query Params:
            * limit  
            * si (start index)

        Returns:
            dict with:
            - "courses": list of courses  
            - "courseCategories": mapping data  
            - "meta": includes totalCourseCount
        """
        request_url = f"{self.base_url}/courses.json"
        headers = {"Authorization": f"Bearer {self.oauth.get_access_token()}"}

        return requests.get(request_url, headers=headers).json()

    def update_course(self, course_id: str, updates: dict):
        """
        Edit/update an existing TrainerCentral course.

        API (Edit Course) details:
        - Method: PUT  
        - Endpoint: /api/v4/{orgId}/courses/{courseId}.json  
        - OAuth Scope: TrainerCentral.courseapi.UPDATE  

        Body:
        {
            "course": {
                "courseName": "<New Title>",
                "subTitle": "<New Subtitle>",
                "description": "<Updated Description>",
                "courseCategories": [
                    {"categoryName": "Category1"},
                    {"categoryName": "Category2"}
                ]
            }
        }

        Returns:
            dict: Response containing the updated course object.
        """
        request_url = f"{self.base_url}/courses/{course_id}.json"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.oauth.get_access_token()}"
        }
        data = {"course": updates}

        return requests.put(request_url, json=data, headers=headers).json()

    def delete_course(self, course_id: str):
        """
        Permanently delete a TrainerCentral course.

        API (Delete Course) details:
        - Method: DELETE  
        - Endpoint: /api/v4/{orgId}/courses/{courseId}.json  
        - OAuth Scope: TrainerCentral.courseapi.DELETE  

        Returns:
            dict: Response JSON from the delete call.
        """
        request_url = f"{self.base_url}/courses/{course_id}.json"
        headers = {"Authorization": f"Bearer {self.oauth.get_access_token()}"}

        return requests.delete(request_url, headers=headers).json()
