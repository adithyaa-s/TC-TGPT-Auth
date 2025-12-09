"""
FastMCP tools for assignment creation / deletion (with instructions support).
"""

from tools.mcp_registry import mcp
from library.assignments import TrainerCentralAssignments

tc_assignments = TrainerCentralAssignments()


@mcp.tool()
def tc_create_assignment(assignment_data: dict,
                         instruction_html: str,
                         instruction_filename: str = "Instructions",
                         view_type: int = 4) -> dict:
    """
    Create an assignment under a course/chapter and attach instructions (rich-text) to it.

    This does the following under the hood:
      1. POST /sessions.json → create assignment (deliveryMode=7)
      2. POST /session/{sessionId}/createTextFile.json → attach instructions text

    Syntax:
        tc_create_assignment(
            {  # assignment_data
              "name": "...",
              "courseId": "...",
              "sectionId": "...",
              "deliveryMode": 7,
              "sessionSettings": { ... }
            },
            "<h2>Instructions here...</h2>",
            "Instructions",  # optional filename/title
            4                # optional viewType
        )

    Required OAuth scopes:
      - TrainerCentral.sessionapi.CREATE  (create assignment)
      - plus whatever scope is required for text-material upload (should be same or compatible)

    Args:
      assignment_data (dict): assignment details.
      instruction_html (str): HTML content for instructions.
      instruction_filename (str, optional): Title for the instructions. Defaults to "Instructions".
      view_type (int, optional): view type as seen in UI. Defaults to 4.

    Returns:
      dict: {
        "assignment": <response from create assignment>,
        "instructions": <response from instructions upload>
      }
    """
    return tc_assignments.create_assignment_with_instructions(
        assignment_data,
        instruction_html,
        instruction_filename,
        view_type
    )


@mcp.tool()
def tc_delete_assignment(session_id: str) -> dict:
    """
    Delete an existing assignment (or session) by session ID.

    Syntax:
        tc_delete_assignment("3300000000002000030")

    Required OAuth scope:
      TrainerCentral.sessionapi.DELETE

    Args:
        session_id (str): The ID of the assignment/session to delete.

    Returns:
        dict: API response from the delete call.
    """
    return tc_assignments.delete_assignment(session_id)
