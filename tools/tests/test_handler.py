from tools.mcp_registry import mcp
from library.tests import TrainerCentralTests

tc_tests = TrainerCentralTests()


@mcp.tool()
def tc_create_full_test(session_id: str, name: str, description_html: str, questions: dict) -> dict:
    """
    Create a COMPLETE test under a lesson (session).

    This tool automatically performs the ENTIRE process:
        1. Create the test FORM:
            POST /session/<sessionId>/forms.json?type=3
            → returns "formIdValue"
        2. Upload QUESTIONS to the form:
            POST /session/<sessionId>/form/<formIdValue>/fields.json?type=3

    ----------------------------------------------------------------------
    QUESTION FORMAT RULES (IMPORTANT FOR LLM)
    ----------------------------------------------------------------------
    ALL questions must be wrapped inside:
        {
            "field": [ { question1 }, { question2 }, ... ]
        }

    Supported question types:

    1. **Single Choice**
        fieldType = 2
        selectionType = 0
        - One correct option

    2. **True / False**
        fieldType = 7
        selectionType = 0
        - Two options: True / False
        feedback.type = 1 → ["Correct", "Wrong"]

    3. **Fill In The Blanks**
        fieldType = 8
        - Uses fillInBlank → fieldOptions (text answers)

    4. **Multiple Choice (multi-select)**
        fieldType = 2
        selectionType = 1
        - Multiple correct options

    5. **Essay**
        fieldType = 16
        - Uses essay → fieldOptions
        - No correctness flags

    Feedback rules:
        enableFeedback: true/false
        feedback.type:
            0 → generic feedback (one message)
            1 → correct/incorrect (two messages)

    ----------------------------------------------------------------------
    MINIMAL TEMPLATES FOR LLM
    ----------------------------------------------------------------------

    Single Choice example:
        {
          "field": [{
            "fieldType": 2,
            "score": 1,
            "label": "<div>Which is largest?</div>",
            "multipleChoice": {
              "selectionType": 0,
              "fieldOptions": [
                {"orderIndex": 0, "optionText": "Asia", "correctAnswer": true},
                {"orderIndex": 1, "optionText": "America", "correctAnswer": false}
              ]
            }
          }]
        }

    True/False example:
        {
          "field": [{
            "fieldType": 7,
            "score": 1,
            "label": "<div>Sky is blue.</div>",
            "multipleChoice": {
              "selectionType": 0,
              "fieldOptions": [
                {"orderIndex": 0, "optionText": "True", "correctAnswer": true},
                {"orderIndex": 1, "optionText": "False", "correctAnswer": false}
              ]
            },
            "enableFeedback": true,
            "feedback": {
              "type": 1,
              "dataList": ["<div>Correct</div>", "<div>Wrong</div>"]
            }
          }]
        }

    The `questions` argument MUST follow these patterns.

    ----------------------------------------------------------------------
    Args:
        session_id (str):
            Lesson/session ID where the test will be placed.

        name (str):
            Name/title of the test.

        description_html (str):
            Test description/instructions in HTML.

        questions (dict):
            The question block following the above schema.

    ----------------------------------------------------------------------
    Returns:
        {
            "form": {... includes formIdValue ...},
            "questions": {... question creation response ...}
        }
    """
    return tc_tests.create_full_test(session_id, name, description_html, questions)


@mcp.tool()
def tc_create_test_form(session_id: str, name: str, description_html: str) -> dict:
    """
    Create ONLY the test form (step 1 of test creation).

    Internally calls:
        POST /session/<sessionId>/forms.json?type=3

    Args:
        session_id (str): Lesson/session ID.
        name (str): Test name.
        description_html (str): HTML description/instructions.

    Returns:
        dict containing:
            {
               "form": {
                   "formIdValue": "<uuid>",
                   ...
               }
            }

    Use this when you want to manually create the form first,
    and add questions later using tc_add_test_questions().
    """
    return tc_tests.create_test_form(session_id, name, description_html)


@mcp.tool()
def tc_add_test_questions(session_id: str, form_id_value: str, questions: dict) -> dict:
    """
    Add questions to an EXISTING form.

    Internally calls:
        POST /session/<sessionId>/form/<formIdValue>/fields.json?type=3

    IMPORTANT RULES FOR LLM:
        - Wrap ALL questions in:
            { "field": [ ... ] }
        - Use valid fieldType / selectionType per question type:
            Single Choice → fieldType 2, selectionType 0
            True/False → fieldType 7, selectionType 0
            Fill In Blanks → fieldType 8
            Multi-Select MCQ → fieldType 2, selectionType 1
            Essay → fieldType 16
        - fieldOptions MUST include orderIndex (0,1,2,...)

    Args:
        session_id (str): Lesson/session ID
        form_id_value (str): Returned from create_test_form() → form.formIdValue
        questions (dict): Valid TC test-question JSON

    Returns:
        dict: API response for question creation.
    """
    return tc_tests.add_questions(session_id, form_id_value, questions)


@mcp.tool()
def tc_get_course_sessions(course_id: str) -> dict:
    """
    Fetch all sessions of a given course.

    This is required BEFORE creating tests, because test creation needs
    a valid `session_id` (lesson/chapter ID), and TrainerCentral does NOT
    provide a direct API to list sessions globally.

    This tool performs:
        1. GET /api/v4/<orgId>/course/<courseId>.json
           → extracts `links.sessions`

        2. GET the sessions URL
           → returns list of sessions

    Returned structure (LLM-friendly):

        {
          "course": {
             "id": "19208000000009003",
             "name": "Python Mastery"
          },
          "sessions": [
              {
                 "sessionId": "19208000000017003",
                 "name": "Error Handling Basics",
                 "description": "<div>Learn the fundamentals...</div>",
                 "testsLink": "/api/v4/<orgId>/session/<sessionId>/tests.json",
                 "raw": { ... full session data ... }
              },
              ...
          ]
        }

    The LLM can now select a `sessionId` and use:
        - tc_create_test_form()
        - tc_add_test_questions()
        - tc_create_full_test()

    Args:
        course_id (str):
            The courseId returned from getCourse.

    Returns:
        dict: sessions list and course info.
    """
    return tc_tests.get_course_sessions(course_id)
