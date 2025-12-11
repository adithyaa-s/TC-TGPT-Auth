"""
TrainerCentral Chapters (Sections) API wrapper
"""

import requests
import json
from typing import Dict, Any, List


class TrainerCentralChapters:
    """
    Handles chapter/section operations in TrainerCentral courses
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
    
    def create_chapter(self, section_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new chapter (section) in a course
        
        Args:
            section_data: Dict with courseId and name
                Example: {"courseId": "123", "name": "Introduction"}
        
        Returns:
            Dict with created section details including sectionId
        """
        url = f"{self.domain}/api/v4/{self.org_id}/sections.json"
        
        # Wrap in "section" key as per API format
        payload = {"section": section_data}
        
        response = requests.post(
            url,
            headers=self._get_headers(),
            json=payload
        )
        response.raise_for_status()
        return response.json()
    
    def get_chapter(self, section_id: str) -> Dict[str, Any]:
        """
        Get details of a specific chapter including its name
        
        Args:
            section_id: The section ID
        
        Returns:
            Dict with section details including sectionName
        """
        url = f"{self.domain}/api/v4/{self.org_id}/sections/{section_id}.json"
        
        response = requests.get(
            url,
            headers=self._get_headers()
        )
        response.raise_for_status()
        return response.json()
    
    def list_course_chapters(self, course_id: str) -> Dict[str, Any]:
        """
        List all chapters in a course with their names
        
        Args:
            course_id: The course ID
        
        Returns:
            Dict with list of sections including names
        """
        url = f"{self.domain}/api/v4/{self.org_id}/course/{course_id}/sections.json"
        
        response = requests.get(
            url,
            headers=self._get_headers()
        )
        response.raise_for_status()
        return response.json()
    
    def get_chapters_with_details(self, course_id: str) -> List[Dict[str, Any]]:
        """
        Get all chapters with full details including names.
        This fetches the list and then gets details for each chapter.
        
        Args:
            course_id: The course ID
        
        Returns:
            List of dicts with full chapter details including names
        """
        # First get the list of chapter IDs
        chapters_response = self.list_course_chapters(course_id)
        
        # Extract section IDs from response
        section_ids = []
        if 'sections' in chapters_response:
            for section in chapters_response['sections']:
                section_id = section.get('sectionId') or section.get('id')
                if section_id:
                    section_ids.append(section_id)
        
        # Fetch details for each chapter
        detailed_chapters = []
        for section_id in section_ids:
            try:
                chapter_details = self.get_chapter(section_id)
                detailed_chapters.append(chapter_details)
            except Exception as e:
                # If we can't get details, include what we have
                detailed_chapters.append({
                    "sectionId": section_id,
                    "error": str(e)
                })
        
        return detailed_chapters
    
    def update_chapter(self, course_id: str, section_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update a chapter (section)
        
        Args:
            course_id: The course ID (may be required by API)
            section_id: The section ID to update
            updates: Dict with fields to update (e.g., {"name": "New Name"})
        
        Returns:
            Dict with updated section details
        """
        # TrainerCentral uses PUT for full updates
        # URL format: /api/v4/{orgId}/sections/{sectionId}.json
        url = f"{self.domain}/api/v4/{self.org_id}/sections/{section_id}.json"
        
        # Wrap updates in "section" key
        payload = {"section": updates}
        
        response = requests.put(
            url,
            headers=self._get_headers(),
            json=payload
        )
        response.raise_for_status()
        return response.json()
    
    def delete_chapter(self, course_id: str, section_id: str) -> Dict[str, Any]:
        """
        Delete a chapter (section)
        
        Args:
            course_id: The course ID
            section_id: The section ID to delete
        
        Returns:
            Dict with deletion status
        """
        url = f"{self.domain}/api/v4/{self.org_id}/sections/{section_id}.json"
        
        response = requests.delete(
            url,
            headers=self._get_headers()
        )
        response.raise_for_status()
        
        # Return success message if no content
        if response.status_code == 204:
            return {"success": True, "message": "Chapter deleted successfully", "sectionId": section_id}
        
        return response.json()