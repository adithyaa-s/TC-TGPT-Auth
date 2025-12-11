"""
TrainerCentral Chapters (Sections) API wrapper

This module provides methods to interact with TrainerCentral's chapter/section API.
Chapters are organizational units within courses that contain lessons, assignments, and tests.

API Documentation: https://help.trainercentral.com/portal/en/kb/articles/create-a-chapter
"""

import requests
import json
from typing import Dict, Any, List, Optional


class TrainerCentralChapters:
    """
    Handles chapter/section operations in TrainerCentral courses.
    
    Chapters (also called sections in the API) are containers that organize course content.
    Each chapter can contain multiple lessons, assignments, and tests.
    
    Attributes:
        context (TrainerCentralContext): Context object containing domain, org_id, and OAuth
        domain (str): TrainerCentral domain URL (e.g., 'https://trainercentral.zoho.in')
        org_id (str): Organization ID for API calls
        oauth (ZohoOAuth): OAuth handler for authentication
    """
    
    def __init__(self, context):
        """
        Initialize the TrainerCentralChapters handler.
        
        Args:
            context (TrainerCentralContext): Context object containing:
                - domain (str): TrainerCentral domain URL
                - org_id (str): Organization ID
                - oauth (ZohoOAuth): OAuth handler for token management
        
        Example:
            >>> from library.common_utils import TrainerCentralContext
            >>> from library.oauth import ZohoOAuth
            >>> oauth = ZohoOAuth(...)
            >>> context = TrainerCentralContext(domain="https://...", org_id="12345", oauth=oauth)
            >>> chapters = TrainerCentralChapters(context)
        """
        self.context = context
        self.domain = context.domain
        self.org_id = context.org_id
        self.oauth = context.oauth
    
    def _get_headers(self) -> Dict[str, str]:
        """
        Get HTTP headers with fresh OAuth access token.
        
        Returns:
            Dict[str, str]: Headers dictionary containing:
                - Authorization: Zoho OAuth token
                - Content-Type: application/json
        
        Raises:
            Exception: If token refresh fails
        """
        token = self.oauth.get_access_token()
        return {
            "Authorization": f"Zoho-oauthtoken {token}",
            "Content-Type": "application/json"
        }
    
    def create_chapter(self, section_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new chapter (section) in a course.
        
        This method creates a chapter that can contain lessons, assignments, and tests.
        The chapter will appear in the course structure and can be reordered later.
        
        Args:
            section_data (Dict[str, Any]): Chapter data containing:
                - courseId (str, required): ID of the course to add chapter to
                - name (str, required): Name of the chapter
                - description (str, optional): Chapter description
        
        Returns:
            Dict[str, Any]: API response containing:
                {
                    "section": {
                        "sectionId": str,  # Unique chapter ID
                        "sectionName": str,  # Chapter name
                        "sectionIndex": str,  # Position in course (0-based)
                        "courseId": str,  # Parent course ID
                        "createdTime": str,  # Timestamp in milliseconds
                        "lastUpdatedTime": str,  # Timestamp in milliseconds
                        "status": str,  # "0" = active
                        ...
                    }
                }
        
        Raises:
            requests.HTTPError: If API request fails (400, 401, 403, 404, 500)
        
        Example:
            >>> chapters = TrainerCentralChapters(context)
            >>> result = chapters.create_chapter({
            ...     "courseId": "19208000000009003",
            ...     "name": "Introduction to Python"
            ... })
            >>> print(result['section']['sectionId'])
            '19208000000009004'
        
        API Endpoint:
            POST /api/v4/{orgId}/sections.json
        
        API Documentation:
            https://help.trainercentral.com/portal/en/kb/articles/create-a-chapter
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
        Get details of a specific chapter including its name.
        
        This method retrieves full details about a single chapter, including its name,
        index, timestamps, and other metadata. Use this to get a chapter's name when
        you only have its ID.
        
        Args:
            section_id (str): The section/chapter ID to retrieve.
                Example: "19208000000009004"
        
        Returns:
            Dict[str, Any]: API response containing:
                {
                    "section": {
                        "sectionId": str,  # Chapter ID
                        "sectionName": str,  # Chapter name (e.g., "Introduction")
                        "sectionIndex": str,  # Position in course
                        "courseId": str,  # Parent course ID
                        "status": str,  # "0" = active, "1" = archived
                        "createdTime": str,  # Creation timestamp (ms)
                        "lastUpdatedTime": str,  # Last update timestamp (ms)
                        "createdBy": str,  # Creator user ID
                        "lastUpdatedBy": str,  # Last editor user ID
                        ...
                    }
                }
        
        Raises:
            requests.HTTPError: If section not found (404) or other API errors
        
        Example:
            >>> chapters = TrainerCentralChapters(context)
            >>> result = chapters.get_chapter("19208000000009004")
            >>> print(result['section']['sectionName'])
            'Introduction to Python'
        
        API Endpoint:
            GET /api/v4/{orgId}/sections/{sectionId}.json
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
        List all chapters in a course (basic info only).
        
        This method returns a list of all chapters in a course. Note that the basic
        list may not include full details like names. Use get_chapters_with_details()
        to get complete information including chapter names.
        
        Args:
            course_id (str): The course ID to list chapters for.
                Example: "19208000000009003"
        
        Returns:
            Dict[str, Any]: API response containing:
                {
                    "sections": [
                        {
                            "sectionId": str,  # Chapter ID
                            "courseId": str,  # Parent course ID
                            "sectionIndex": str,  # Position
                            # May or may not include sectionName
                            ...
                        },
                        ...
                    ]
                }
        
        Raises:
            requests.HTTPError: If course not found or access denied
        
        Example:
            >>> chapters = TrainerCentralChapters(context)
            >>> result = chapters.list_course_chapters("19208000000009003")
            >>> for section in result['sections']:
            ...     print(section['sectionId'])
        
        API Endpoint:
            GET /api/v4/{orgId}/course/{courseId}/sections.json
        
        Note:
            For full chapter details including names, use get_chapters_with_details()
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
        Get all chapters in a course with FULL details including names.
        
        This is the RECOMMENDED method for listing chapters when you need names.
        It first gets the list of chapter IDs, then fetches full details for each
        chapter individually to ensure you get the chapter names.
        
        This method is essential for workflows where you need to:
        - Display chapter names to users
        - Find a specific chapter by name
        - Show a complete course structure
        
        Args:
            course_id (str): The course ID to get chapters for.
                Example: "19208000000009003"
        
        Returns:
            List[Dict[str, Any]]: List of chapter details:
                [
                    {
                        "section": {
                            "sectionId": str,  # Chapter ID
                            "sectionName": str,  # CHAPTER NAME (guaranteed)
                            "sectionIndex": str,  # Position (0, 1, 2, ...)
                            "courseId": str,  # Parent course ID
                            "status": str,  # "0" = active
                            "createdTime": str,
                            "lastUpdatedTime": str,
                            ...
                        }
                    },
                    ...
                ]
                
                If a chapter fetch fails, it returns:
                {
                    "sectionId": str,
                    "error": str  # Error message
                }
        
        Raises:
            requests.HTTPError: If course not found or access denied
        
        Example:
            >>> chapters = TrainerCentralChapters(context)
            >>> all_chapters = chapters.get_chapters_with_details("19208000000009003")
            >>> for chapter in all_chapters:
            ...     if 'section' in chapter:
            ...         print(f"{chapter['section']['sectionName']}: {chapter['section']['sectionId']}")
            Introduction: 19208000000009004
            Core Concepts: 19208000000009017
            Project Examples: 19208000000009019
        
        Performance:
            Makes N+1 API calls (1 for list, N for details).
            For a course with 10 chapters, makes 11 API calls.
        
        Use Case:
            This method solves the problem where users need to identify a chapter
            by name (e.g., "Project Examples") but only have IDs from a basic list.
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
        
        # Fetch details for each chapter to get names
        detailed_chapters = []
        for section_id in section_ids:
            try:
                chapter_details = self.get_chapter(section_id)
                detailed_chapters.append(chapter_details)
            except Exception as e:
                # If we can't get details, include what we have with error
                detailed_chapters.append({
                    "sectionId": section_id,
                    "error": str(e)
                })
        
        return detailed_chapters
    
    def update_chapter(self, course_id: str, section_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update a chapter's properties.
        
        This method updates an existing chapter using HTTP PUT. All fields in the
        updates dictionary will be applied to the chapter. Only include fields you
        want to change.
        
        Args:
            course_id (str): The course ID (may be required for validation).
                Example: "19208000000009003"
            section_id (str): The section/chapter ID to update.
                Example: "19208000000009004"
            updates (Dict[str, Any]): Fields to update:
                - name (str, optional): New chapter name
                - description (str, optional): New description
                - Any other chapter fields
        
        Returns:
            Dict[str, Any]: API response with updated chapter:
                {
                    "section": {
                        "sectionId": str,
                        "sectionName": str,  # Updated name
                        "sectionIndex": str,
                        "lastUpdatedTime": str,  # New timestamp
                        ...
                    }
                }
        
        Raises:
            requests.HTTPError: If chapter not found, access denied, or invalid data
        
        Example:
            >>> chapters = TrainerCentralChapters(context)
            >>> result = chapters.update_chapter(
            ...     course_id="19208000000009003",
            ...     section_id="19208000000009004",
            ...     updates={"name": "Advanced Python Concepts"}
            ... )
            >>> print(result['section']['sectionName'])
            'Advanced Python Concepts'
        
        API Endpoint:
            PUT /api/v4/{orgId}/sections/{sectionId}.json
        
        API Documentation:
            https://help.trainercentral.com/portal/en/kb/articles/edit-chapter-api
        
        Note:
            Uses PUT method (full update). All provided fields replace existing values.
        """
        # TrainerCentral uses PUT for updates
        url = f"{self.domain}/api/v4/{self.org_id}/sections/{section_id}.json"
        
        # Wrap updates in "section" key as per API format
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
        Delete a chapter and all its contents.
        
        WARNING: This permanently deletes the chapter and all lessons, assignments,
        and tests within it. This action cannot be undone.
        
        Args:
            course_id (str): The course ID (for validation).
                Example: "19208000000009003"
            section_id (str): The section/chapter ID to delete.
                Example: "19208000000009004"
        
        Returns:
            Dict[str, Any]: Success response:
                {
                    "success": True,
                    "message": "Chapter deleted successfully",
                    "sectionId": str  # ID of deleted chapter
                }
        
        Raises:
            requests.HTTPError: If chapter not found, access denied, or has dependencies
        
        Example:
            >>> chapters = TrainerCentralChapters(context)
            >>> result = chapters.delete_chapter(
            ...     course_id="19208000000009003",
            ...     section_id="19208000000009004"
            ... )
            >>> print(result['message'])
            'Chapter deleted successfully'
        
        API Endpoint:
            DELETE /api/v4/{orgId}/sections/{sectionId}.json
        
        API Documentation:
            https://help.trainercentral.com/portal/en/kb/articles/delete-chapter-api
        
        HTTP Status Codes:
            - 204 No Content: Deletion successful (no body returned)
            - 200 OK: Deletion successful (with response body)
            - 404 Not Found: Chapter doesn't exist
            - 403 Forbidden: No permission to delete
        """
        url = f"{self.domain}/api/v4/{self.org_id}/sections/{section_id}.json"
        
        response = requests.delete(
            url,
            headers=self._get_headers()
        )
        response.raise_for_status()
        
        # Return success message if no content (204 status)
        if response.status_code == 204:
            return {
                "success": True,
                "message": "Chapter deleted successfully",
                "sectionId": section_id
            }
        
        return response.json()