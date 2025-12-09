"""
Central FastMCP instance and tool registration.
"""

from fastmcp import FastMCP

mcp = FastMCP()

def get_mcp() -> FastMCP:
    """
    Return the shared MCP instance with all tools registered.
    """
    return mcp
