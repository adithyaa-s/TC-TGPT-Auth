"""
TrainerCentral Lessons (Sessions) API wrapper

This module provides methods to interact with TrainerCentral's lesson/session API.
Lessons are the primary content delivery mechanism in courses, containing materials,
videos, documents, and other learning resources.

API Documentation: https://help.trainercentral.com/portal/en/kb/articles/create-a-session
"""

import requests
import json
import io
from typing import Dict, Any, Optional, List


class TrainerCentralLessons:
    """
    Handles lesson/session operations in TrainerCentral courses.
    
    Lessons (called "sessions" in the API) are individual learning units that contain
    educational content like HTML lessons, videos, documents, and assignments. They
    are organized within chapters and can be self-paced or scheduled.
    
    Attributes:
        context (TrainerCentralContext): Context object containing domain, org_id, and OAuth
        domain (str): TrainerCentral domain URL (e.g., 'https://trainercentral.zoho.in')
        org_id (str): Organization ID for API calls
        oauth (ZohoOAuth): OAuth handler for authentication
    """
    
    def __init__(self, context):
        """
        Initialize the TrainerCentralLessons handler.
        
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
            >>> lessons = TrainerCentralLessons(context)
        """
        self.context = context
        self.domain = context.domain
        self.org_id = context.org_id
        self.oauth = context.oauth
    
    def _get_headers(self) -> Dict[str, str]:
        """
        Get HTTP headers with fresh OAuth access token for JSON requests.
        
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
    
    def _get_multipart_headers(self) -> Dict[str, str]:
        """
        Get HTTP headers for multipart/form-data uploads.
        
        Note: Content-Type header is NOT included because the requests library
        automatically sets it with the proper boundary parameter when files are uploaded.
        
        Returns:
            Dict[str, str]: Headers dictionary containing:
                - Authorization: Zoho OAuth token
        
        Raises:
            Exception: If token refresh fails
        """
        token = self.oauth.get_access_token()
        return {
            "Authorization": f"Zoho-oauthtoken {token}"
        }
    
    def create_lesson(self, session_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a basic lesson (session) without content.
        
        This creates an empty lesson container. You'll need to separately upload
        content using upload_content(). For creating a lesson with content in one
        step, use create_lesson_with_content().
        
        Args:
            session_data (Dict[str, Any]): Lesson data containing:
                - courseId (str, required): ID of the parent course
                - name (str, required): Lesson title
                - sectionId (str, optional): Chapter/section ID to place lesson in
                - deliveryMode (int, required): Type of session:
                    * 4 = Self-paced lesson (most common)
                    * 7 = Assignment
                    * 2 = Live workshop
                - description (str, optional): Lesson description
                - duration (int, optional): Lesson duration in minutes
        
        Returns:
            Dict[str, Any]: API response containing:
                {
                    "session": {
                        "sessionId": str,  # Unique lesson ID
                        "name": str,  # Lesson title
                        "courseId": str,  # Parent course
                        "sectionId": str,  # Parent chapter (if specified)
                        "deliveryMode": int,  # Session type
                        "status": str,  # "0" = active
                        "createdTime": str,  # Timestamp (ms)
                        "lastUpdatedTime": str,
                        ...
                    }
                }
        
        Raises:
            requests.HTTPError: If API request fails (400, 401, 403, 404, 500)
        
        Example:
            >>> lessons = TrainerCentralLessons(context)
            >>> result = lessons.create_lesson({
            ...     "courseId": "19208000000009003",
            ...     "name": "Introduction to Variables",
            ...     "sectionId": "19208000000009019",
            ...     "deliveryMode": 4
            ... })
            >>> session_id = result['session']['sessionId']
        
        API Endpoint:
            POST /api/v4/{orgId}/sessions.json
        
        API Documentation:
            https://help.trainercentral.com/portal/en/kb/articles/create-a-session
        
        Note:
            After creating a lesson, use upload_content() to add learning materials.
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
        Create a lesson with HTML content in one operation.
        
        This is a convenience method that:
        1. Creates the lesson container
        2. Uploads HTML content as a material
        
        This is the recommended way to create lessons with content.
        
        Args:
            session_data (Dict[str, Any]): Lesson data containing:
                - courseId (str, required): Parent course ID
                - name (str, required): Lesson title
                - sectionId (str, optional): Chapter to place lesson in
                - deliveryMode (int, optional): Default 4 (self-paced)
                - description (str, optional): Lesson description
            
            content_html (str): HTML content for the lesson. Can include:
                - Text, headers, lists
                - Images (base64 or URLs)
                - Code blocks
                - Embedded videos
            
            content_filename (str, optional): Display name for the content file.
                Default: "Content"
        
        Returns:
            Dict[str, Any]: API response from lesson creation:
                {
                    "session": {
                        "sessionId": str,  # Use this for updates
                        "name": str,
                        "courseId": str,
                        "sectionId": str,
                        ...
                    }
                }
        
        Raises:
            ValueError: If sessionId cannot be extracted from create response
            requests.HTTPError: If lesson creation or content upload fails
        
        Example:
            >>> lessons = TrainerCentralLessons(context)
            >>> html_content = '''
            ... <h1>Variables in Python</h1>
            ... <p>Variables store data values...</p>
            ... <pre><code>x = 5</code></pre>
            ... '''
            >>> result = lessons.create_lesson_with_content(
            ...     session_data={
            ...         "courseId": "19208000000009003",
            ...         "name": "Python Variables",
            ...         "sectionId": "19208000000009019",
            ...         "deliveryMode": 4
            ...     },
            ...     content_html=html_content,
            ...     content_filename="Variables Lesson"
            ... )
            >>> print(f"Created lesson: {result['session']['sessionId']}")
        
        Process Flow:
            1. Call create_lesson() to create empty lesson
            2. Extract sessionId from response
            3. Call upload_content() to add HTML material
            4. Return original create_lesson response
        
        Note:
            The content is uploaded as an HTML file and will be rendered
            in TrainerCentral's lesson viewer.
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
        Upload HTML content to an existing lesson.
        
        This method uploads content as an HTML file that will be displayed
        in the lesson viewer. Can be called multiple times to update content.
        
        Args:
            session_id (str): The lesson/session ID to upload content to.
                Example: "4500000000003000022"
            
            content_html (str): HTML content to upload. Supports:
                - Standard HTML tags (h1-h6, p, div, span, etc.)
                - Lists (ul, ol, li)
                - Tables
                - Images (img tags with src as URL or base64)
                - Code blocks (pre, code tags)
                - Styling (inline styles or style tags)
            
            filename (str, optional): Display name for the content file.
                Default: "Content"
                Will be shown as "{filename}.html" in the lesson
        
        Returns:
            Dict[str, Any]: API response from material upload:
                {
                    "material": {
                        "materialId": str,
                        "label": str,  # filename
                        "viewType": str,  # "4" for HTML
                        "sessionId": str,
                        ...
                    }
                }
        
        Raises:
            requests.HTTPError: If session not found or upload fails
        
        Example:
            >>> lessons = TrainerCentralLessons(context)
            >>> html = "<h1>Updated Content</h1><p>New lesson material</p>"
            >>> result = lessons.upload_content(
            ...     session_id="4500000000003000022",
            ...     content_html=html,
            ...     filename="Updated Lesson"
            ... )
        
        API Endpoint:
            POST /api/v4/{orgId}/sessions/{sessionId}/materials.json
        
        Content-Type:
            multipart/form-data (automatically set by requests library)
        
        View Types:
            - viewType "4" = HTML content (what this method uses)
            - Other view types: videos, PDFs, documents, etc.
        
        Note:
            The HTML content is uploaded as a file attachment to the lesson.
            It will be rendered in an iframe or content viewer in TrainerCentral.
        """
        url = f"{self.domain}/api/v4/{self.org_id}/sessions/{session_id}/materials.json"
        
        # Create HTML file in memory
        html_file = io.BytesIO(content_html.encode('utf-8'))
        
        # Prepare multipart form data
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
        Get details of a specific lesson.
        
        Retrieves complete information about a lesson including its name, status,
        content materials, and metadata. Use this to check lesson properties or
        get the current lesson name before updating.
        
        Args:
            session_id (str): The lesson/session ID to retrieve.
                Example: "4500000000003000022"
        
        Returns:
            Dict[str, Any]: API response containing:
                {
                    "session": {
                        "sessionId": str,  # Lesson ID
                        "name": str,  # Lesson title
                        "description": str,  # Lesson description
                        "courseId": str,  # Parent course
                        "sectionId": str,  # Parent chapter (if any)
                        "deliveryMode": int,  # 4=self-paced, 7=assignment
                        "duration": int,  # Duration in minutes
                        "status": str,  # "0"=active, "1"=draft, "2"=archived
                        "createdTime": str,  # Creation timestamp (ms)
                        "lastUpdatedTime": str,  # Last update timestamp (ms)
                        "materials": [...]  # List of attached materials
                        ...
                    }
                }
        
        Raises:
            requests.HTTPError: If lesson not found (404) or access denied (403)
        
        Example:
            >>> lessons = TrainerCentralLessons(context)
            >>> result = lessons.get_lesson("4500000000003000022")
            >>> print(f"Lesson: {result['session']['name']}")
            >>> print(f"Materials: {len(result['session']['materials'])}")
            Lesson: Introduction to Variables
            Materials: 2
        
        API Endpoint:
            GET /api/v4/{orgId}/sessions/{sessionId}.json
        
        Use Cases:
            - Verify lesson exists before updating
            - Get current lesson name
            - Check lesson status and properties
            - List attached materials
            - Audit lesson metadata (created time, updated time, etc.)
        """
        url = f"{self.domain}/api/v4/{self.org_id}/sessions/{session_id}.json"
        
        response = requests.get(
            url,
            headers=self._get_headers()
        )
        response.raise_for_status()
        return response.json()
    
    def list_course_lessons(self, course_id: str) -> Dict[str, Any]:
        """
        List all lessons in a course.
        
        Retrieves a list of all lessons (sessions) in the specified course,
        including lessons in all chapters. This is useful for getting an overview
        of all course content or finding a specific lesson by name.
        
        Args:
            course_id (str): The course ID to list lessons for.
                Example: "19208000000009003"
        
        Returns:
            Dict[str, Any]: API response containing:
                {
                    "sessions": [
                        {
                            "sessionId": str,
                            "name": str,  # Lesson title
                            "courseId": str,
                            "sectionId": str,  # Chapter ID (if assigned)
                            "deliveryMode": int,
                            "status": str,
                            "duration": int,
                            ...
                        },
                        ...
                    ]
                }
        
        Raises:
            requests.HTTPError: If course not found or access denied
        
        Example:
            >>> lessons = TrainerCentralLessons(context)
            >>> result = lessons.list_course_lessons("19208000000009003")
            >>> for lesson in result['sessions']:
            ...     print(f"{lesson['name']} (ID: {lesson['sessionId']})")
            Introduction to Variables (ID: 4500000000003000022)
            Data Types (ID: 4500000000003000023)
            Control Flow (ID: 4500000000003000024)
        
        API Endpoint:
            GET /api/v4/{orgId}/course/{courseId}/sessions.json
        
        Use Cases:
            - Display course outline
            - Find lesson by name
            - Count total lessons
            - Filter lessons by chapter (sectionId)
            - Bulk operations on all lessons
        
        Note:
            This returns ALL sessions including lessons, assignments, and tests.
            Filter by deliveryMode to get specific types:
            - deliveryMode 4 = Self-paced lessons
            - deliveryMode 7 = Assignments
            - deliveryMode 2 = Live workshops
        """
        url = f"{self.domain}/api/v4/{self.org_id}/course/{course_id}/sessions.json"
        
        response = requests.get(
            url,
            headers=self._get_headers()
        )
        response.raise_for_status()
        return response.json()
    
    def update_lesson(self, session_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update a lesson's properties.
        
        This method updates an existing lesson using HTTP PUT. Only the fields
        provided in the updates dictionary will be changed. Common use cases:
        - Rename a lesson
        - Update description
        - Change duration
        - Modify status (draft/active)
        
        Args:
            session_id (str): The lesson/session ID to update.
                Example: "4500000000003000022"
            
            updates (Dict[str, Any]): Fields to update. Can include:
                - name (str): New lesson title
                - description (str): New description
                - duration (int): Duration in minutes
                - status (str): "0"=active, "1"=draft, "2"=archived
                - Any other session fields
        
        Returns:
            Dict[str, Any]: API response with updated lesson:
                {
                    "session": {
                        "sessionId": str,
                        "name": str,  # Updated name
                        "description": str,  # Updated description
                        "lastUpdatedTime": str,  # New timestamp
                        ...
                    }
                }
        
        Raises:
            requests.HTTPError: If lesson not found, access denied, or invalid data
        
        Example:
            >>> lessons = TrainerCentralLessons(context)
            >>> result = lessons.update_lesson(
            ...     session_id="4500000000003000022",
            ...     updates={
            ...         "name": "Advanced Variable Concepts",
            ...         "description": "Deep dive into Python variables"
            ...     }
            ... )
            >>> print(result['session']['name'])
            'Advanced Variable Concepts'
        
        API Endpoint:
            PUT /api/v4/{orgId}/sessions/{sessionId}.json
        
        API Documentation:
            https://help.trainercentral.com/portal/en/kb/articles/edit-lesson-api
        
        HTTP Method:
            Uses PUT (full update). Only provided fields are updated;
            omitted fields retain their current values.
        
        Common Update Patterns:
            # Rename lesson
            update_lesson(id, {"name": "New Name"})
            
            # Mark as draft
            update_lesson(id, {"status": "1"})
            
            # Update multiple fields
            update_lesson(id, {
                "name": "New Name",
                "description": "New description",
                "duration": 45
            })
        
        Note:
            To update lesson CONTENT (HTML), use upload_content() instead.
            This method updates lesson METADATA only.
        """
        # TrainerCentral uses PUT for updates
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
        Delete a lesson permanently.
        
        WARNING: This permanently deletes the lesson and all its materials,
        including uploaded content, videos, and attachments. This action
        cannot be undone. Learner progress for this lesson will also be lost.
        
        Args:
            session_id (str): The lesson/session ID to delete.
                Example: "4500000000003000022"
        
        Returns:
            Dict[str, Any]: Success response:
                {
                    "success": True,
                    "message": "Lesson deleted successfully",
                    "sessionId": str  # ID of deleted lesson
                }
        
        Raises:
            requests.HTTPError: If lesson not found, access denied, or has dependencies
        
        Example:
            >>> lessons = TrainerCentralLessons(context)
            >>> result = lessons.delete_lesson("4500000000003000022")
            >>> print(result['message'])
            'Lesson deleted successfully'
        
        API Endpoint:
            DELETE /api/v4/{orgId}/sessions/{sessionId}.json
        
        API Documentation:
            https://help.trainercentral.com/portal/en/kb/articles/delete-lesson-live-workshop-assignment-api
        
        HTTP Status Codes:
            - 204 No Content: Deletion successful (no body returned)
            - 200 OK: Deletion successful (with response body)
            - 404 Not Found: Lesson doesn't exist
            - 403 Forbidden: No permission to delete
        
        What Gets Deleted:
            - The lesson itself
            - All uploaded materials (HTML, videos, files)
            - Learner progress and completion records
            - Associated tests and quizzes
            - Comments and discussions
        
        Best Practice:
            Before deleting, consider:
            1. Archiving instead (update status to "2")
            2. Downloading lesson materials as backup
            3. Notifying learners if lesson is in active use
        """
        url = f"{self.domain}/api/v4/{self.org_id}/sessions/{session_id}.json"
        
        response = requests.delete(
            url,
            headers=self._get_headers()
        )
        response.raise_for_status()
        
        # Return success message if no content (204 status)
        if response.status_code == 204:
            return {
                "success": True,
                "message": "Lesson deleted successfully",
                "sessionId": session_id
            }
        
        return response.json()
    
    def get_lesson_materials(self, session_id: str) -> Dict[str, Any]:
        """
        Get all materials attached to a lesson.
        
        Retrieves a list of all content materials attached to a lesson, including
        HTML content, videos, documents, and other files. Each material has metadata
        like type, size, and upload time.
        
        Args:
            session_id (str): The lesson/session ID.
                Example: "4500000000003000022"
        
        Returns:
            Dict[str, Any]: API response containing:
                {
                    "materials": [
                        {
                            "materialId": str,
                            "label": str,  # Display name
                            "viewType": str,  # Type of material
                            "fileSize": int,  # Size in bytes
                            "createdTime": str,
                            "url": str,  # Access URL (if available)
                            ...
                        },
                        ...
                    ]
                }
        
        Raises:
            requests.HTTPError: If session not found or access denied
        
        Example:
            >>> lessons = TrainerCentralLessons(context)
            >>> result = lessons.get_lesson_materials("4500000000003000022")
            >>> for material in result['materials']:
            ...     print(f"{material['label']} ({material['viewType']})")
            Lesson Content (4)
            Introduction Video (1)
        
        API Endpoint:
            GET /api/v4/{orgId}/sessions/{sessionId}/materials.json
        
        Material View Types:
            - "1" = Video
            - "2" = PDF document
            - "3" = Image
            - "4" = HTML content
            - "5" = Other files
        
        Use Cases:
            - List all content in a lesson
            - Check if lesson has materials
            - Download or backup lesson content
            - Audit uploaded files
        """
        url = f"{self.domain}/api/v4/{self.org_id}/sessions/{session_id}/materials.json"
        
        response = requests.get(
            url,
            headers=self._get_headers()
        )
        response.raise_for_status()
        return response.json()