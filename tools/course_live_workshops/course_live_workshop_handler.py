"""
FastMCP tools that expose TrainerCentral live workshop / session inside the course APIs.
"""

from tools.mcp_registry import mcp
from library.course_live_workshops import TrainerCentralLiveWorkshops

tc_live = TrainerCentralLiveWorkshops()



@mcp.tool()
def tc_create_course_live_session(
    course_id: str,
    name: str,
    description_html: str,
    start_time: str,
    end_time: str
):
    """
    Create a LIVE WORKSHOP inside a course.

    Required date format:
        "DD-MM-YYYY HH:MMAM/PM"

    The system automatically converts start_time and end_time using DateConverter.
    """

    return tc_live.create_course_live_workshop(
        course_id=course_id,
        name=name,
        description_html=description_html,
        start_time_str=start_time,
        end_time_str=end_time
    )

@mcp.tool()
def tc_list_course_live_sessions(filter_type: int = 5, limit: int = 50, si: int = 0) -> dict:
    """
    List upcoming live workshop sessions, inside the course alone.

    Syntax:
        tc_list_live_sessions(filter_type=5, limit=50, si=0)

    Required OAuth scope:
        TrainerCentral.talkapi.READ

    Args:
        filter_type (int): Filter for sessions (e.g., 1=your upcoming, 5=all upcoming).
        limit (int): Number of sessions to fetch.
        si (int): Start index for pagination.

    Returns:
        dict: API response with sessions list.
    """
    return tc_live.list_upcoming_live_sessions(filter_type, limit, si)


@mcp.tool()
def tc_delete_course_live_session(session_id: str) -> dict:
    """
    Delete a live workshop session by session ID.

    Syntax:
        tc_delete_live_session("3300000000002000040")

    Required OAuth scope:
        TrainerCentral.sessionapi.DELETE

    Args:
        session_id (str): ID of the live session to delete.

    Returns:
        dict: API response for the delete operation.
    """
    return tc_live.delete_live_session(session_id)


@mcp.tool()
def invite_learner_to_course_or_course_live_session(
    email: str,
    first_name: str,
    last_name: str,
    course_id: str = None,
    session_id: str = None,
    is_access_granted: bool = True,
    expiry_time: int = None,
    expiry_duration: str = None
) -> dict:
    """
    Invite a learner to a Course OR Course Live Workshop.

    Body format required by TrainerCentral:
    {
        "courseAttendee": {
            "email": "...",
            "courseId" OR "sessionId": "...",
            "firstName": "...",
            "lastName": "...",
            "isAccessGranted": true
        }
    }
    """
    return tc_live.invite_learner_to_course_or_course_live_session(
        email=email,
        first_name=first_name,
        last_name=last_name,
        course_id=course_id,
        session_id=session_id,
        is_access_granted=is_access_granted,
        expiry_time=expiry_time,
        expiry_duration=expiry_duration
    )
