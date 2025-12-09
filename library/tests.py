
import requests

from .common_utils import TrainerCentralContext, get_trainercentral_context


class TrainerCentralTests:
    """
    Handles creating tests under a session (lesson) in TrainerCentral.

    Step 1 → Create Test Form  
        POST /api/v4/<orgId>/session/<sessionId>/forms.json?type=3

        - The response indicates the successful creation of a test and contains the value "formIdValue", which is required for adding questions.

    Step 2 → Add Questions to Form  
        POST /api/v4/<orgId>/session/<sessionId>/form/<formIdValue>/fields.json?type=3

        - This adds MCQ / True-False / Fill-Blanks / Essay questions.
        - The request body follows the TrainerCentral question schema.
    """

    def __init__(self, context: TrainerCentralContext | None = None):
        self.context = context or get_trainercentral_context()
        self.base_url = self.context.base_url
        self.oauth = self.context.oauth
        self.domain = self.context.domain

    def create_test_form(self, session_id: str, name: str, description_html: str) -> dict:
        """
        STEP 1 — Create a test form.

        API:
            POST /session/<sessionId>/forms.json?type=3

        Args:
            session_id (str): Lesson/session ID where the test is created.
            name (str): Name/title of the test (form).
            description_html (str): HTML instructions or test description.

        Returns:
            dict: API response containing:
                {
                  "form": {
                     "formIdValue": "xxxx-xxxx-xxxx",
                     "name": "...",
                     ...
                  }
                }

        NOTE:
        - The correct identifier for adding questions is "form.formIdValue".
        - NOT "id" or "formId".
        """
        url = f"{self.base_url}/session/{session_id}/forms.json?type=3"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.oauth.get_access_token()}",
        }

        body = {
            "form": {
                "name": name,
                "description": description_html,
                "sessionId": session_id,
                "type": 3  # Test
            }
        }

        return requests.post(url, json=body, headers=headers).json()

    def add_questions(self, session_id: str, form_id_value: str, questions_body: dict) -> dict:
        """
        STEP 2 — Add questions to the test form.

        API:
            POST /session/<sessionId>/form/<formIdValue>/fields.json?type=3

        Args:
            session_id (str): Lesson/session ID.
            form_id_value (str): The formIdValue returned by create_test_form().
            questions_body (dict): A dict following the schema:
                {
                  "field": [
                     {
                       "fieldType": 2,
                       "label": "<div>Question text</div>",
                       "score": 1,
                       "multipleChoice": {...} / "fillInBlank": {...} / "essay": {...}
                     }
                  ]
                }

        Returns:
            dict: API response for created questions.
        """
        url = f"{self.base_url}/session/{session_id}/form/{form_id_value}/fields.json?type=3"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.oauth.get_access_token()}",
        }

        return requests.post(url, json=questions_body, headers=headers).json()

    def create_full_test(self, session_id: str, name: str, description_html: str, questions_body: dict) -> dict:
        """
        HIGH-LEVEL FUNCTION
        Creates a complete test in ONE call for MCP.

        Steps performed:
            1. Create the form
            2. Extract formIdValue
            3. Add questions using fields.json

        Args:
            session_id (str): Lesson/session ID.
            name (str): Test name/title.
            description_html (str): Test instructions in HTML.
            questions_body (dict): Full "field" question JSON.

        Returns:
            dict:
            {
               "form": <response from form creation>,
               "questions": <response from question upload>
            }
        """

        form_resp = self.create_test_form(session_id, name, description_html)
        form_obj = form_resp.get("form", {})
        form_id_value = form_obj.get("formIdValue")

        if not form_id_value:
            raise RuntimeError(
                f"Could not extract formIdValue from form response: {form_resp}"
            )

        questions_resp = self.add_questions(session_id, form_id_value, questions_body)

        return {
            "form": form_resp,
            "questions": questions_resp
        }

    def get_course_sessions(self, course_id: str) -> dict:
      """
      Fetch all sessions (lessons) under a course.

      Steps:
          1. GET /courses/<courseId>.json
              → extract links.sessions
          2. GET the sessions URL
              → return array of sessions with LLM-friendly fields

      Returns:
          {
            "course": {
                "courseId": "...",
                "name": "..."
            },
            "sessions": [
                {
                  "sessionId": "...",
                  "name": "...",
                  "description": "...",
                  "testsLink": "...",
                  "raw": { ... }
                }
            ],
            "raw": <full sessions response>
          }
      """

      headers = {
          "Authorization": f"Bearer {self.oauth.get_access_token()}"
      }

      # IMPORTANT: correct endpoint uses `courses` (plural)
      course_url = f"{self.base_url}/courses/{course_id}.json"
      course_res = requests.get(course_url, headers=headers).json()

      # Validate structure
      if "course" not in course_res:
          return {
              "error": "'course' key missing in response",
              "raw": course_res
          }

      course_obj = course_res["course"]

      # Extract sessions link safely
      sessions_link = course_obj.get("links", {}).get("sessions")
      if not sessions_link:
          return {
              "error": "sessions link missing for this course",
              "course": course_obj,
              "raw": course_res
          }

      # Build full sessions URL using DOMAIN
      sessions_url = f"{self.domain}{sessions_link}"

      sessions_res = requests.get(sessions_url, headers=headers).json()

      sessions_list = []
      for s in sessions_res.get("sessions", []):
          sessions_list.append({
              "sessionId": s.get("sessionId"),
              "name": s.get("name"),
              "description": s.get("description"),
              "testsLink": s.get("links", {}).get("tests"),
              "raw": s
          })

      return {
          "course": {
              "courseId": course_obj.get("courseId"),
              "name": course_obj.get("courseName")
          },
          "sessions": sessions_list,
          "raw": sessions_res
      }
