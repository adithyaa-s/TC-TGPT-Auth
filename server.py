"""
Lightweight HTTP server to expose the well-known OAuth metadata required by
ChatGPT Apps SDK / MCP authorization spec. This does NOT implement Zoho OAuth;
it simply advertises metadata so ChatGPT can complete the OAuth flow against
Zoho and then call this MCP server with the bearer token.

Also serves the MCP server over HTTP/JSON-RPC at /mcp endpoint.
"""

import os
import json
from typing import Dict, List, Any

from fastapi import FastAPI, Response, Request
from fastapi.responses import JSONResponse

# Base URL where this MCP server is reachable by ChatGPT (Render public URL)
RESOURCE_BASE_URL = os.getenv("RESOURCE_BASE_URL", "https://tc-tgpt-auth.onrender.com").rstrip("/")

# Zoho accounts base (region-specific)
ZOHO_ACCOUNTS_URL = os.getenv("ZOHO_ACCOUNTS_URL", "https://accounts.zoho.in").rstrip("/")

# Scopes we want to request from ChatGPT for TrainerCentral
DEFAULT_SCOPES: List[str] = [
    "TrainerCentral.courseapi.ALL",
    "TrainerCentral.sessionapi.ALL",
    "TrainerCentral.sectionapi.ALL",
    "TrainerCentral.talkapi.ALL",
    "TrainerCentral.userapi.ALL",
    "TrainerCentral.portalapi.ALL",
]

app = FastAPI()


def resource_metadata() -> Dict:
    """
    Metadata for this protected resource, per RFC 9728 / Apps SDK guide.
    """
    return {
        "resource": RESOURCE_BASE_URL,
        "authorization_servers": [ZOHO_ACCOUNTS_URL],
        "scopes_supported": DEFAULT_SCOPES,
        "resource_documentation": f"{RESOURCE_BASE_URL}/docs",
    }


def oauth_authorization_server_metadata() -> Dict:
    """
    Static OAuth authorization-server metadata. Since we cannot modify Zoho's
    well-known, we mirror the essential fields here and point to Zoho endpoints.
    """
    return {
        "issuer": ZOHO_ACCOUNTS_URL,
        "authorization_endpoint": f"{ZOHO_ACCOUNTS_URL}/oauth/v2/auth",
        "token_endpoint": f"{ZOHO_ACCOUNTS_URL}/oauth/v2/token",
        # ChatGPT uses PKCE (S256)
        "code_challenge_methods_supported": ["S256"],
        # dynamic client registration is not available for Zoho; ChatGPT can skip if not provided
        # "registration_endpoint": "<optional-if-you-host-a-proxy>",
        "scopes_supported": DEFAULT_SCOPES,
    }


@app.get("/.well-known/oauth-protected-resource")
async def well_known_oauth_protected_resource():
    return resource_metadata()


@app.get("/.well-known/oauth-authorization-server")
async def well_known_oauth_authorization_server():
    return oauth_authorization_server_metadata()


@app.get("/.well-known/openid-configuration")
async def well_known_openid_configuration():
    # Mirror the same data for clients that probe OIDC discovery
    return oauth_authorization_server_metadata()


@app.get("/healthz")
async def healthz():
    return {"status": "ok"}


def make_unauthorized_response(scope: str | None = None) -> Response:
    """
    Helper to emit a WWW-Authenticate challenge. This can be used by
    MCP tool handlers when a token is missing/invalid to prompt ChatGPT
    to show the OAuth UI.
    """
    challenge = f'Bearer resource_metadata="{RESOURCE_BASE_URL}/.well-known/oauth-protected-resource"'
    if scope:
        challenge += f', scope="{scope}"'
    headers = {"WWW-Authenticate": challenge}
    return Response(status_code=401, headers=headers)


@app.post("/mcp")
@app.post("/mcp/")
async def mcp_endpoint(request: Request):
    """
    HTTP endpoint for MCP JSON-RPC 2.0 requests. ChatGPT sends POST requests
    here with JSON-RPC payloads. We route them to the FastMCP instance.
    """
    try:
        # Parse JSON-RPC request
        body = await request.json()
        
        # Import here to avoid circular imports
        from tools.mcp_registry import get_mcp
        
        mcp = get_mcp()
        
        # FastMCP handles JSON-RPC internally via its transport.
        # For HTTP, we need to manually process the request.
        # FastMCP's run() method expects stdio, so we'll use its internal handlers.
        
        # Extract JSON-RPC fields
        method = body.get("method")
        params = body.get("params", {})
        request_id = body.get("id")
        jsonrpc = body.get("jsonrpc", "2.0")
        
        # Handle MCP protocol methods
        if method == "initialize":
            # Return server capabilities
            result = {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {},
                },
                "serverInfo": {
                    "name": "trainercentral-mcp",
                    "version": "1.0.0",
                },
            }
            return JSONResponse({
                "jsonrpc": jsonrpc,
                "id": request_id,
                "result": result,
            })
        
        elif method == "tools/list":
            # List all registered tools with proper MCP format
            # Try to get tools from FastMCP if possible, otherwise use static list
            tools_list = []
            
            # Try to access FastMCP's internal tool registry
            try:
                # FastMCP may store tools in _tools or similar attribute
                if hasattr(mcp, '_tools'):
                    tools_dict = mcp._tools
                    for tool_name, tool_info in tools_dict.items():
                        tools_list.append({
                            "name": tool_name,
                            "description": getattr(tool_info, 'description', ''),
                            "inputSchema": getattr(tool_info, 'inputSchema', {"type": "object", "properties": {}}),
                        })
                elif hasattr(mcp, 'tools'):
                    # Alternative attribute name
                    tools_dict = mcp.tools
                    for tool_name, tool_info in tools_dict.items():
                        tools_list.append({
                            "name": tool_name,
                            "description": getattr(tool_info, 'description', ''),
                            "inputSchema": getattr(tool_info, 'inputSchema', {"type": "object", "properties": {}}),
                        })
            except:
                pass  # Fall back to static list
            
            # If we couldn't get tools from FastMCP, use static list
            if not tools_list:
                # Static list with basic info (will be improved)
                tools_list = [
                    {
                        "name": "tc_create_course",
                        "description": "Create a new course in TrainerCentral",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "course_data": {
                                    "type": "object",
                                    "description": "Course data including courseName, subTitle, description, courseCategories"
                                }
                            },
                            "required": ["course_data"]
                        },
                    },
                    {
                        "name": "tc_get_course",
                        "description": "Retrieve a course by its ID",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "course_id": {"type": "string", "description": "Course ID"}
                            },
                            "required": ["course_id"]
                        },
                    },
                    {
                        "name": "tc_list_courses",
                        "description": "List all courses",
                        "inputSchema": {"type": "object", "properties": {}},
                    },
                    {
                        "name": "tc_update_course",
                        "description": "Update an existing course",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "course_id": {"type": "string"},
                                "updates": {"type": "object"}
                            },
                            "required": ["course_id", "updates"]
                        },
                    },
                    {
                        "name": "tc_delete_course",
                        "description": "Delete a course permanently",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "course_id": {"type": "string"}
                            },
                            "required": ["course_id"]
                        },
                    },
                    {
                        "name": "tc_create_chapter",
                        "description": "Create a new chapter (section) under a course",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "section_data": {"type": "object"}
                            },
                            "required": ["section_data"]
                        },
                    },
                    {
                        "name": "tc_update_chapter",
                        "description": "Update an existing chapter's name and/or position",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "course_id": {"type": "string"},
                                "section_id": {"type": "string"},
                                "updates": {"type": "object"}
                            },
                            "required": ["course_id", "section_id", "updates"]
                        },
                    },
                    {
                        "name": "tc_delete_chapter",
                        "description": "Delete a chapter from a course",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "course_id": {"type": "string"},
                                "section_id": {"type": "string"}
                            },
                            "required": ["course_id", "section_id"]
                        },
                    },
                    {
                        "name": "tc_create_lesson",
                        "description": "Create a lesson under a course/chapter with content",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "session_data": {"type": "object"},
                                "content_html": {"type": "string"},
                                "content_filename": {"type": "string"}
                            },
                            "required": ["session_data", "content_html"]
                        },
                    },
                    {
                        "name": "tc_update_lesson",
                        "description": "Update an existing lesson",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "session_id": {"type": "string"},
                                "updates": {"type": "object"}
                            },
                            "required": ["session_id", "updates"]
                        },
                    },
                    {
                        "name": "tc_delete_lesson",
                        "description": "Delete a lesson by session ID",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "session_id": {"type": "string"}
                            },
                            "required": ["session_id"]
                        },
                    },
                    {
                        "name": "tc_create_assignment",
                        "description": "Create an assignment with instructions",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "assignment_data": {"type": "object"},
                                "instruction_html": {"type": "string"}
                            },
                            "required": ["assignment_data", "instruction_html"]
                        },
                    },
                    {
                        "name": "tc_delete_assignment",
                        "description": "Delete an assignment by session ID",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "session_id": {"type": "string"}
                            },
                            "required": ["session_id"]
                        },
                    },
                    {
                        "name": "tc_create_full_test",
                        "description": "Create a complete test under a lesson",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "session_id": {"type": "string"},
                                "name": {"type": "string"},
                                "description_html": {"type": "string"},
                                "questions": {"type": "object"}
                            },
                            "required": ["session_id", "name", "description_html", "questions"]
                        },
                    },
                    {
                        "name": "tc_create_test_form",
                        "description": "Create only the test form",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "session_id": {"type": "string"},
                                "name": {"type": "string"},
                                "description_html": {"type": "string"}
                            },
                            "required": ["session_id", "name", "description_html"]
                        },
                    },
                    {
                        "name": "tc_add_test_questions",
                        "description": "Add questions to an existing test form",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "session_id": {"type": "string"},
                                "form_id_value": {"type": "string"},
                                "questions": {"type": "object"}
                            },
                            "required": ["session_id", "form_id_value", "questions"]
                        },
                    },
                    {
                        "name": "tc_get_course_sessions",
                        "description": "Fetch all sessions of a given course",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "course_id": {"type": "string"}
                            },
                            "required": ["course_id"]
                        },
                    },
                    {
                        "name": "tc_create_workshop",
                        "description": "Create a GLOBAL Live Workshop",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "session_data": {"type": "object"}
                            },
                            "required": ["session_data"]
                        },
                    },
                    {
                        "name": "tc_update_workshop",
                        "description": "Update an existing global workshop",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "session_id": {"type": "string"},
                                "updates": {"type": "object"}
                            },
                            "required": ["session_id", "updates"]
                        },
                    },
                    {
                        "name": "tc_create_workshop_occurrence",
                        "description": "Create a new occurrence (talk) for a workshop",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "talk_data": {"type": "object"}
                            },
                            "required": ["talk_data"]
                        },
                    },
                    {
                        "name": "tc_update_workshop_occurrence",
                        "description": "Update a workshop occurrence",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "talk_id": {"type": "string"},
                                "updates": {"type": "object"}
                            },
                            "required": ["talk_id", "updates"]
                        },
                    },
                    {
                        "name": "tc_list_all_global_workshops",
                        "description": "List upcoming global live workshops",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "filter_type": {"type": "integer"},
                                "limit": {"type": "integer"},
                                "si": {"type": "integer"}
                            }
                        },
                    },
                    {
                        "name": "tc_invite_user_to_session",
                        "description": "Invite an existing user to a course-linked live workshop session",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "session_id": {"type": "string"},
                                "email": {"type": "string"},
                                "role": {"type": "integer"},
                                "source": {"type": "integer"}
                            },
                            "required": ["session_id", "email"]
                        },
                    },
                    {
                        "name": "tc_create_course_live_session",
                        "description": "Create a LIVE WORKSHOP inside a course",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "course_id": {"type": "string"},
                                "name": {"type": "string"},
                                "description_html": {"type": "string"},
                                "start_time": {"type": "string"},
                                "end_time": {"type": "string"}
                            },
                            "required": ["course_id", "name", "description_html", "start_time", "end_time"]
                        },
                    },
                    {
                        "name": "tc_list_course_live_sessions",
                        "description": "List upcoming live workshop sessions inside the course",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "filter_type": {"type": "integer"},
                                "limit": {"type": "integer"},
                                "si": {"type": "integer"}
                            }
                        },
                    },
                    {
                        "name": "tc_delete_course_live_session",
                        "description": "Delete a live workshop session by session ID",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "session_id": {"type": "string"}
                            },
                            "required": ["session_id"]
                        },
                    },
                    {
                        "name": "invite_learner_to_course_or_course_live_session",
                        "description": "Invite a learner to a Course OR Course Live Workshop",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "email": {"type": "string"},
                                "first_name": {"type": "string"},
                                "last_name": {"type": "string"},
                                "course_id": {"type": "string"},
                                "session_id": {"type": "string"}
                            },
                            "required": ["email", "first_name", "last_name"]
                        },
                    },
                ]
            
            return JSONResponse({
                "jsonrpc": jsonrpc,
                "id": request_id,
                "result": {"tools": tools_list},
            })
        
        elif method == "tools/call":
            # Call a tool
            tool_name = params.get("name")
            arguments = params.get("arguments", {})
            
            # Import tool handlers dynamically
            import importlib
            tool_module_map = {
                "tc_create_course": ("tools.courses.course_handler", "tc_create_course"),
                "tc_get_course": ("tools.courses.course_handler", "tc_get_course"),
                "tc_list_courses": ("tools.courses.course_handler", "tc_list_courses"),
                "tc_update_course": ("tools.courses.course_handler", "tc_update_course"),
                "tc_delete_course": ("tools.courses.course_handler", "tc_delete_course"),
                "tc_create_chapter": ("tools.chapters.chapter_handler", "tc_create_chapter"),
                "tc_update_chapter": ("tools.chapters.chapter_handler", "tc_update_chapter"),
                "tc_delete_chapter": ("tools.chapters.chapter_handler", "tc_delete_chapter"),
                "tc_create_lesson": ("tools.lessons.lesson_handler", "tc_create_lesson"),
                "tc_update_lesson": ("tools.lessons.lesson_handler", "tc_update_lesson"),
                "tc_delete_lesson": ("tools.lessons.lesson_handler", "tc_delete_lesson"),
                "tc_create_assignment": ("tools.assignments.assignment_handler", "tc_create_assignment"),
                "tc_delete_assignment": ("tools.assignments.assignment_handler", "tc_delete_assignment"),
                "tc_create_full_test": ("tools.tests.test_handler", "tc_create_full_test"),
                "tc_create_test_form": ("tools.tests.test_handler", "tc_create_test_form"),
                "tc_add_test_questions": ("tools.tests.test_handler", "tc_add_test_questions"),
                "tc_get_course_sessions": ("tools.tests.test_handler", "tc_get_course_sessions"),
                "tc_create_workshop": ("tools.live_workshops.live_workshop_handler", "tc_create_workshop"),
                "tc_update_workshop": ("tools.live_workshops.live_workshop_handler", "tc_update_workshop"),
                "tc_create_workshop_occurrence": ("tools.live_workshops.live_workshop_handler", "tc_create_workshop_occurrence"),
                "tc_update_workshop_occurrence": ("tools.live_workshops.live_workshop_handler", "tc_update_workshop_occurrence"),
                "tc_list_all_global_workshops": ("tools.live_workshops.live_workshop_handler", "tc_list_all_global_workshops"),
                "tc_invite_user_to_session": ("tools.live_workshops.live_workshop_handler", "tc_invite_user_to_session"),
                "tc_create_course_live_session": ("tools.course_live_workshops.course_live_workshop_handler", "tc_create_course_live_session"),
                "tc_list_course_live_sessions": ("tools.course_live_workshops.course_live_workshop_handler", "tc_list_course_live_sessions"),
                "tc_delete_course_live_session": ("tools.course_live_workshops.course_live_workshop_handler", "tc_delete_course_live_session"),
                "invite_learner_to_course_or_course_live_session": ("tools.course_live_workshops.course_live_workshop_handler", "invite_learner_to_course_or_course_live_session"),
            }
            
            if tool_name not in tool_module_map:
                return JSONResponse({
                    "jsonrpc": jsonrpc,
                    "id": request_id,
                    "error": {
                        "code": -32601,
                        "message": f"Method not found: {tool_name}",
                    },
                }, status_code=200)
            
            module_path, func_name = tool_module_map[tool_name]
            module = importlib.import_module(module_path)
            tool_func = getattr(module, func_name)
            
            # Call the tool function
            try:
                # Convert arguments dict to function parameters
                result = tool_func(**arguments)
                
                return JSONResponse({
                    "jsonrpc": jsonrpc,
                    "id": request_id,
                    "result": {
                        "content": [
                            {
                                "type": "text",
                                "text": json.dumps(result, indent=2),
                            }
                        ],
                    },
                })
            except Exception as e:
                return JSONResponse({
                    "jsonrpc": jsonrpc,
                    "id": request_id,
                    "error": {
                        "code": -32000,
                        "message": str(e),
                    },
                }, status_code=200)
        
        else:
            # Unknown method
            return JSONResponse({
                "jsonrpc": jsonrpc,
                "id": request_id,
                "error": {
                    "code": -32601,
                    "message": f"Method not found: {method}",
                },
            }, status_code=200)
    
    except json.JSONDecodeError:
        return JSONResponse({
            "jsonrpc": "2.0",
            "id": None,
            "error": {
                "code": -32700,
                "message": "Parse error",
            },
        }, status_code=200)
    except Exception as e:
        return JSONResponse({
            "jsonrpc": "2.0",
            "id": None,
            "error": {
                "code": -32603,
                "message": f"Internal error: {str(e)}",
            },
        }, status_code=200)


@app.get("/mcp")
async def mcp_get():
    """
    GET endpoint for health checks. Returns basic info.
    """
    return JSONResponse({
        "status": "ok",
        "protocol": "mcp",
        "version": "2024-11-05",
    })

