"""
FastMCP tools that expose TrainerCentral course APIs.
"""

from library.courses import TrainerCentralCourses
from tools.mcp_registry import mcp 

tc = TrainerCentralCourses()


@mcp.tool()
def tc_create_course(course_data: dict) -> dict:
    """
    Create a new course in TrainerCentral.

    Syntax:
        tc_create_course({
            "courseName": "My Course",
            "subTitle": "Catchy Subtitle",
            "description": "Detailed description",
            "courseCategories": [
                {"categoryName": "Business"},
                {"categoryName": "Software"}
            ]
        })

    This will call the TrainerCentral Create Course API with a body like:
        {
            "course": {
                "courseName": "My Course",
                "subTitle": "Catchy Subtitle",
                "description": "Detailed description",
                "courseCategories": [
                    {"categoryName": "Business"},
                    {"categoryName": "Software"}
                ]
            }
        }

    Required OAuth scope:
        TrainerCentral.courseapi.CREATE

    Returns:
        dict: API response, including:
            - ticket
            - course
            - courseCategories
    """
    return tc.post_course(course_data)


@mcp.tool()
def tc_get_course(course_id: str) -> dict:
    """
    Retrieve a course by its ID.

    Syntax:
        tc_get_course("3000094000002000004")

    This will call the TrainerCentral Get Course API:
        GET /api/v4/{orgId}/courses/{courseId}.json

    Required OAuth scope:
        TrainerCentral.courseapi.READ

    Returns:
        dict containing:
            - courseId
            - courseName
            - description
            - subTitle
            - links to sessions, tickets, etc.
    """
    return tc.get_course(course_id)


@mcp.tool()
def tc_list_courses(limit: int = None, si: int = None) -> dict:
    """
    List all courses (or a paginated subset).

    Syntax:
        tc_list_courses()
        tc_list_courses(limit=30)
        tc_list_courses(limit=20, si=10)

    Note:
        TrainerCentral uses `limit` and `si` as query parameters.
        Current implementation returns all courses — pagination support
        can be added later.

    Required OAuth scope:
        TrainerCentral.courseapi.READ

    Returns:
        dict with:
            - courses []
            - courseCategories []
            - meta { totalCourseCount }
    """
    return tc.list_courses()


@mcp.tool()
def tc_update_course(course_id: str, updates: dict) -> dict:
    """
    Update an existing course.

    Syntax:
        tc_update_course(
            "3000094000002000004",
            {
                "courseName": "New Name",
                "subTitle": "New Subtitle",
                "description": "Updated detail",
                "courseCategories": [
                    {"categoryName": "Business"},
                    {"categoryName": "Leadership"}
                ]
            }
        )

    This will call the TrainerCentral Update Course API with:
        {
            "course": {
                "courseName": "New Name",
                "subTitle": "New Subtitle",
                "description": "Updated detail",
                "courseCategories": [...]
            }
        }

    Required OAuth scope:
        TrainerCentral.courseapi.UPDATE

    Returns:
        dict: Updated course object.
    """
    return tc.update_course(course_id, updates)


@mcp.tool()
def tc_delete_course(course_id: str) -> dict:
    """
    Delete a course permanently.

    Syntax:
        tc_delete_course("3000094000002000004")

    This will call the TrainerCentral Delete Course API:
        DELETE /api/v4/{orgId}/courses/{courseId}.json

    Required OAuth scope:
        TrainerCentral.courseapi.DELETE

    Returns:
        dict: API delete response.
    """
    return tc.delete_course(course_id)
