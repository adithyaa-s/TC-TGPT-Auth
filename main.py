"""
Main entry point for the TrainerCentral MCP server.

This server runs over HTTP (FastAPI) instead of stdio, so ChatGPT can connect
via POST requests to /mcp. The server also exposes OAuth metadata endpoints
required by the ChatGPT Apps SDK.
"""

import os

# Import all tool handlers to register them with FastMCP
import tools.courses.course_handler
import tools.chapters.chapter_handler
import tools.lessons.lesson_handler
import tools.live_workshops.live_workshop_handler
import tools.assignments.assignment_handler
import tools.tests.test_handler
import tools.course_live_workshops.course_live_workshop_handler

# Import MCP registry to ensure tools are registered
from tools.mcp_registry import get_mcp


def main():
    """
    Start the FastAPI server which serves both:
    1. OAuth metadata endpoints (/.well-known/*)
    2. MCP JSON-RPC endpoint (/mcp)
    """
    import uvicorn
    from server import app

    # Prefer Render's PORT if present, else METADATA_PORT, else 8000.
    port = int(os.getenv("PORT") or os.getenv("METADATA_PORT") or "8000")
    host = os.getenv("METADATA_HOST", "0.0.0.0")
    
    # Ensure tools are registered (side effect of imports above)
    get_mcp()
    
    # Run FastAPI server (blocking)
    uvicorn.run(app, host=host, port=port, log_level="info")


if __name__ == "__main__":
    main()
