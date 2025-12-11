# """
# FastMCP tools that expose TrainerCentral chapter (section) APIs.
# """

# from library.chapters import TrainerCentralChapters
# from tools.mcp_registry import mcp  

# tc = TrainerCentralChapters()


# @mcp.tool()
# def tc_create_chapter(section_data: dict) -> dict:
#     """
#     Create a new chapter (section) under a course in TrainerCentral.

#     Syntax:
#         tc_create_chapter({
#             "courseId": "3000094000002000004",
#             "name": "Introduction"
#         })

#     This will call the TrainerCentral Sections API with a body like:
#         {
#             "section": {
#                 "courseId": "3000094000002000004",
#                 "name": "Introduction"
#             }
#         }

#     Required OAuth scope:
#         TrainerCentral.sectionapi.CREATE

#     Args:
#         section_data (dict):
#             - "courseId" (str): ID of the course under which to create the chapter.
#             - "name" (str): Name/title of the chapter.

#     Returns:
#         dict: API response, including:
#             - id / sectionId
#             - name / sectionName
#             - sectionIndex
#             - createdTime
#             - lastUpdatedTime
#             - status
#     """
#     return tc.create_chapter(section_data)


# @mcp.tool()
# def tc_update_chapter(course_id: str, section_id: str, updates: dict) -> dict:
#     """
#     Update an existing chapter's name and/or position in a course.

#     Syntax:
#         tc_update_chapter(
#             "3000094000002000004",  # courseId
#             "3200000000002000012",  # sectionId
#             {
#                 "name": "Updated Introduction",
#                 "sectionIndex": 1      # optional, only when reordering
#             }
#         )

#     This will call the TrainerCentral Edit Chapter API with a body like:
#         {
#             "section": {
#                 "name": "Updated Introduction",
#                 "sectionIndex": 1
#             }
#         }

#     Required OAuth scope:
#         TrainerCentral.sectionapi.UPDATE

#     Args:
#         course_id (str):
#             The ID of the course that owns the chapter.
#         section_id (str):
#             The ID of the chapter (section) to update.
#         updates (dict):
#             Fields to update, e.g.:
#                 - "name" (str): New chapter name.
#                 - "sectionIndex" (int): New 0-based position of the chapter in the course.

#     Returns:
#         dict: API response containing the updated chapter (section) object.
#     """
#     return tc.update_chapter(course_id, section_id, updates)


# @mcp.tool()
# def tc_delete_chapter(course_id: str, section_id: str) -> dict:
#     """
#     Delete a chapter from a course in TrainerCentral.

#     Syntax:
#         tc_delete_chapter(
#             "3000094000002000004",  # courseId
#             "3200000000002000012"   # sectionId
#         )

#     This will call the TrainerCentral Delete Chapter API:
#         DELETE /api/v4/{orgId}/course/{courseId}/sections/{sectionId}.json

#     Required OAuth scope:
#         TrainerCentral.sectionapi.DELETE

#     Args:
#         course_id (str):
#             The ID of the course that owns the chapter.
#         section_id (str):
#             The ID of the chapter (section) to delete.

#     Returns:
#         dict: API delete response (may be an empty object or status details,
#               depending on TrainerCentral's response format).
#     """
#     return tc.delete_chapter(course_id, section_id)


"""
Chapter handler for MCP tools.

This module defines MCP tool functions for chapter operations.
These are registered with FastMCP and exposed to ChatGPT.
"""

from tools.mcp_registry import mcp
from library.chapters import TrainerCentralChapters


@mcp.tool() if mcp else lambda f: f
def tc_create_chapter(section_data: dict) -> dict:
    """
    Create a new chapter in a course.
    
    Args:
        section_data: Dict containing courseId and name
    
    Returns:
        Dict with created chapter details including sectionId
    """
    # Note: Actual implementation is in server.py which creates context
    # This is just the tool definition for FastMCP registration
    pass


@mcp.tool() if mcp else lambda f: f
def tc_get_chapter(section_id: str) -> dict:
    """
    Get details of a specific chapter including its name.
    
    Args:
        section_id: The section/chapter ID
    
    Returns:
        Dict with chapter details including sectionName
    """
    pass


@mcp.tool() if mcp else lambda f: f
def tc_list_course_chapters(course_id: str) -> list:
    """
    List all chapters in a course with their names.
    
    Args:
        course_id: The course ID
    
    Returns:
        List of chapter details with names
    """
    pass


@mcp.tool() if mcp else lambda f: f
def tc_update_chapter(course_id: str, section_id: str, updates: dict) -> dict:
    """
    Update a chapter.
    
    Args:
        course_id: The course ID
        section_id: The chapter ID to update
        updates: Dict with fields to update
    
    Returns:
        Dict with updated chapter details
    """
    pass


@mcp.tool() if mcp else lambda f: f
def tc_delete_chapter(course_id: str, section_id: str) -> dict:
    """
    Delete a chapter.
    
    Args:
        course_id: The course ID
        section_id: The chapter ID to delete
    
    Returns:
        Dict with deletion status
    """
    pass