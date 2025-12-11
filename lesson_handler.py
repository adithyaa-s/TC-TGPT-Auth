# """
# FastMCP tools that expose TrainerCentral lesson (session) APIs.
# """

# from tools.mcp_registry import mcp
# from library.lessons import TrainerCentralLessons

# tc_lessons = TrainerCentralLessons()


# # @mcp.tool()
# # def tc_create_lesson(session_data: dict) -> dict:
# #     """
# #     Create a new lesson under a course/chapter.

# #     Syntax:
# #         tc_create_lesson({
# #             "name": "Lesson Title",
# #             "courseId": "3000094000002000004",
# #             "sectionId": "3200000000002000012",
# #             "deliveryMode": 4  # 4 = on-demand, 3 = live
# #         })

# #     Required OAuth scope:
# #         TrainerCentral.sessionapi.CREATE

# #     Args:
# #         session_data (dict): Fields required for the lesson.

# #     Returns:
# #         dict: API response for the created session.
# #     """
# #     return tc_lessons.create_lesson(session_data)

# @mcp.tool()
# def tc_create_lesson(
#     session_data: dict,
#     content_html: str,
#     content_filename: str = "Content"
# ) -> dict:
#     """
#     Create a lesson under a course/chapter, with full rich-text content.

#     Args:
#         session_data (dict): metadata for lesson (name, courseId, sectionId, deliveryMode, etc.)
#         content_html (str): full HTML/text body of lesson
#         content_filename (str, optional): title/filename for upload (default: "Content")

#     Returns:
#         dict: { "lesson": ..., "content": ... }
#     """
#     return tc_lessons.create_lesson_with_content(session_data, content_html, content_filename)

# @mcp.tool()
# def tc_update_lesson(session_id: str, updates: dict) -> dict:
#     """
#     Update an existing lesson in TrainerCentral.

#     Syntax:
#         tc_update_lesson(
#             "3300000000002000020",  # sessionId
#             {
#                 "name": "New Lesson Title",
#                 "description": "Updated description",
#                 "sectionId": "3200000000002000012",
#                 "sessionIndex": 1
#             }
#         )

#     Required OAuth scope:
#         TrainerCentral.sessionapi.UPDATE

#     Args:
#         session_id (str): ID of the session (lesson) to update.
#         updates (dict): Fields to update.

#     Returns:
#         dict: API response containing the updated session.
#     """
#     return tc_lessons.update_lesson(session_id, updates)


# @mcp.tool()
# def tc_delete_lesson(session_id: str) -> dict:
#     """
#     Delete a lesson (or live session) by session ID.

#     Syntax:
#         tc_delete_lesson("3300000000002000020")

#     Required OAuth scope:
#         TrainerCentral.sessionapi.DELETE

#     Args:
#         session_id (str): ID of the session to delete.

#     Returns:
#         dict: API response for the delete operation.
#     """
#     return tc_lessons.delete_lesson(session_id)


"""
Lesson handler for MCP tools.

This module defines MCP tool functions for lesson operations.
These are registered with FastMCP and exposed to ChatGPT.
"""

from tools.mcp_registry import mcp
from library.lessons import TrainerCentralLessons


@mcp.tool() if mcp else lambda f: f
def tc_create_lesson(session_data: dict, content_html: str, content_filename: str = "Content") -> dict:
    """
    Create a lesson with HTML content.
    
    Args:
        session_data: Dict with courseId, name, sectionId, deliveryMode
        content_html: HTML content for the lesson
        content_filename: Name for the content file
    
    Returns:
        Dict with created lesson details
    """
    pass


@mcp.tool() if mcp else lambda f: f
def tc_get_lesson(session_id: str) -> dict:
    """
    Get details of a specific lesson.
    
    Args:
        session_id: The lesson/session ID
    
    Returns:
        Dict with lesson details
    """
    pass


@mcp.tool() if mcp else lambda f: f
def tc_list_course_lessons(course_id: str) -> dict:
    """
    List all lessons in a course.
    
    Args:
        course_id: The course ID
    
    Returns:
        Dict with list of lessons
    """
    pass


@mcp.tool() if mcp else lambda f: f
def tc_update_lesson(session_id: str, updates: dict) -> dict:
    """
    Update a lesson.
    
    Args:
        session_id: The lesson ID to update
        updates: Dict with fields to update
    
    Returns:
        Dict with updated lesson details
    """
    pass


@mcp.tool() if mcp else lambda f: f
def tc_delete_lesson(session_id: str) -> dict:
    """
    Delete a lesson.
    
    Args:
        session_id: The lesson ID to delete
    
    Returns:
        Dict with deletion status
    """
    pass