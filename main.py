from concurrent.futures import ThreadPoolExecutor

from tools.mcp_registry import get_mcp
import tools.courses.course_handler
import tools.chapters.chapter_handler
import tools.lessons.lesson_handler
import tools.live_workshops.live_workshop_handler
import tools.assignments.assignment_handler
import tools.tests.test_handler
import tools.course_live_workshops.course_live_workshop_handler


def start_metadata_server():
    """
    Runs the FastAPI metadata server in a background thread so MCP can run
    simultaneously. The server exposes the well-known OAuth endpoints required
    by ChatGPT Apps SDK.
    """
    import uvicorn
    from server import app

    port = int(os.getenv("METADATA_PORT", "8000"))
    host = os.getenv("METADATA_HOST", "0.0.0.0")
    uvicorn.run(app, host=host, port=port, log_level="info")


def main():
    mcp = get_mcp()

    # Start metadata server in background
    executor = ThreadPoolExecutor(max_workers=2)
    executor.submit(start_metadata_server)

    # Run MCP (blocking)
    mcp.run()


if __name__ == "__main__":
    import os

    main()
