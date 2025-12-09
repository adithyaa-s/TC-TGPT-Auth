from tools.mcp_registry import get_mcp
import tools.courses.course_handler
import tools.chapters.chapter_handler
import tools.lessons.lesson_handler
import tools.live_workshops.live_workshop_handler
import tools.assignments.assignment_handler
import tools.tests.test_handler
import tools.course_live_workshops.course_live_workshop_handler

def main():
    mcp = get_mcp()
    mcp.run()
#     mcp.run(
#     transport="http",
#     host="0.0.0.0",
#     port=8000
# )

if __name__ == "__main__":
    main()
