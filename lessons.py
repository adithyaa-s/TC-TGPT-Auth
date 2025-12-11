"""
TrainerCentral Lessons (Sessions) API wrapper
"""

import requests
import json
import io
from typing import Dict, Any, Optional


class TrainerCentralLessons:
    """
    Handles lesson/session operations in TrainerCentral courses
    """
    
    def __init__(self, context):
        """
        Initialize with TrainerCentralContext
        
        Args:
            context: TrainerCentralContext with domain, org_id, and OAuth
        """
        self.context = context
        self.domain = context.domain
        self.org_id = context.org_id
        self.oauth = context.oauth
    
    def _get_headers(self) -> Dict[str, str]:
        """Get headers with fresh access token"""
        token = self.oauth.get_access_token()
        return {
            "Authorization": f"Zoho-oauthtoken {token}",
            "Content-Type": "application/json"
        }
    
    def _get_multipart_headers(self) -> Dict[str, str]:
        """Get headers for multipart/form-data (no Content-Type, requests sets it)"""
        token = self.oauth.get_access_token()
        return {
            "Authorization": f"Zoho-oauthtoken {token}"
        }
    
    def create_lesson(self, session_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a basic lesson (session) without content
        
        Args:
            session_data: Dict with courseId, name, sectionId (optional), deliveryMode
                Example: {
                    "courseId": "123",
                    "name": "Lesson Title",
                    "sectionId": "456",  # Optional
                    "deliveryMode": 4  # 4 = self-paced lesson
                }
        
        Returns:
            Dict with created session details including sessionId
        """
        url = f"{self.domain}/api/v4/{self.org_id}/sessions.json"
        
        # Wrap in "session" key as per API format
        payload = {"session": session_data}
        
        response = requests.post(
            url,
            headers=self._get_headers(),
            json=payload
        )
        response.raise_for_status()
        return response.json()
    
    def create_lesson_with_content(
        self,
        session_data: Dict[str, Any],
        content_html: str,
        content_filename: str = "Content"
    ) -> Dict[str, Any]:
        """
        Create a lesson with HTML content
        
        Args:
            session_data: Dict with courseId, name, sectionId, deliveryMode
            content_html: HTML content for the lesson
            content_filename: Name for the content file (default: "Content")
        
        Returns:
            Dict with created lesson details including sessionId
        """
        # First create the lesson
        lesson_response = self.create_lesson(session_data)
        
        # Extract sessionId from response
        session_id = None
        if 'session' in lesson_response:
            session_id = lesson_response['session'].get('sessionId') or lesson_response['session'].get('id')
        elif 'sessionId' in lesson_response:
            session_id = lesson_response['sessionId']
        elif 'id' in lesson_response:
            session_id = lesson_response['id']
        
        if not session_id:
            raise ValueError(f"Failed to find sessionId in response: {lesson_response}")
        
        # Upload content as HTML file
        self.upload_content(session_id, content_html, content_filename)
        
        return lesson_response
    
    def upload_content(
        self,
        session_id: str,
        content_html: str,
        filename: str = "Content"
    ) -> Dict[str, Any]:
        """
        Upload HTML content to a lesson
        
        Args:
            session_id: The session ID
            content_html: HTML content
            filename: Name for the content file
        
        Returns:
            Dict with upload status
        """
        url = f"{self.domain}/api/v4/{self.org_id}/sessions/{session_id}/materials.json"
        
        # Create HTML file in memory
        html_file = io.BytesIO(content_html.encode('utf-8'))
        
        files = {
            'file': (f"{filename}.html", html_file, 'text/html')
        }
        
        data = {
            'viewType': '4',  # HTML content view type
            'label': filename
        }
        
        response = requests.post(
            url,
            headers=self._get_multipart_headers(),
            files=files,
            data=data
        )
        response.raise_for_status()
        return response.json()
    
    def get_lesson(self, session_id: str) -> Dict[str, Any]:
        """
        Get details of a specific lesson
        
        Args:
            session_id: The session ID
        
        Returns:
            Dict with lesson details
        """
        url = f"{self.domain}/api/v4/{self.org_id}/sessions/{session_id}.json"
        
        response = requests.get(
            url,
            headers=self._get_headers()
        )
        response.raise_for_status()
        return response.json()
    
    def update_lesson(self, session_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update a lesson (session)
        
        Args:
            session_id: The session ID to update
            updates: Dict with fields to update
                Example: {"name": "New Lesson Title", "description": "Updated description"}
        
        Returns:
            Dict with updated lesson details
        """
        # TrainerCentral uses PUT for updates
        # URL format: /api/v4/{orgId}/sessions/{sessionId}.json
        url = f"{self.domain}/api/v4/{self.org_id}/sessions/{session_id}.json"
        
        # Wrap updates in "session" key as per API format
        payload = {"session": updates}
        
        response = requests.put(
            url,
            headers=self._get_headers(),
            json=payload
        )
        response.raise_for_status()
        return response.json()
    
    def delete_lesson(self, session_id: str) -> Dict[str, Any]:
        """
        Delete a lesson (session)
        
        Args:
            session_id: The session ID to delete
        
        Returns:
            Dict with deletion status
        """
        url = f"{self.domain}/api/v4/{self.org_id}/sessions/{session_id}.json"
        
        response = requests.delete(
            url,
            headers=self._get_headers()
        )
        response.raise_for_status()
        
        # Return success message if no content
        if response.status_code == 204:
            return {"success": True, "message": "Lesson deleted successfully", "sessionId": session_id}
        
        return response.json()
    
    def list_course_lessons(self, course_id: str) -> Dict[str, Any]:
        """
        List all lessons in a course
        
        Args:
            course_id: The course ID
        
        Returns:
            Dict with list of sessions
        """
        url = f"{self.domain}/api/v4/{self.org_id}/course/{course_id}/sessions.json"
        
        response = requests.get(
            url,
            headers=self._get_headers()
        )
        response.raise_for_status()
        return response.json()
    
    def get_lesson_materials(self, session_id: str) -> Dict[str, Any]:
        """
        Get all materials for a lesson
        
        Args:
            session_id: The session ID
        
        Returns:
            Dict with list of materials
        """
        url = f"{self.domain}/api/v4/{self.org_id}/sessions/{session_id}/materials.json"
        
        response = requests.get(
            url,
            headers=self._get_headers()
        )
        response.raise_for_status()
        return response.json()