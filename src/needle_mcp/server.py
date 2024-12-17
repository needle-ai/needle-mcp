import os
import json
import logging
import asyncio
from datetime import datetime
from typing import Any, Sequence, Dict, Optional
from functools import wraps
from urllib.parse import urlparse
from dataclasses import dataclass

from dotenv import load_dotenv
from mcp.server import Server
from mcp.types import (
    Tool,
    TextContent,
    EmptyResult,
)
from needle.v1 import NeedleClient
from needle.v1.models import FileToAdd, Error as NeedleError

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("needle_mcp")

API_KEY = os.getenv("NEEDLE_API_KEY")
if not API_KEY:
    raise ValueError("NEEDLE_API_KEY environment variable must be set")

# Initialize Needle client
client = NeedleClient(api_key=API_KEY)

# Create the MCP server instance
server = Server("needle_mcp")

@dataclass
class NeedleResponse:
    success: bool
    data: Optional[Dict] = None
    error: Optional[str] = None

def rate_limit(calls: int, period: float):
    """Simple rate limiting decorator to avoid overloading the API."""
    def decorator(func):
        last_reset = datetime.now()
        calls_made = 0

        @wraps(func)
        async def wrapper(*args, **kwargs):
            nonlocal last_reset, calls_made
            now = datetime.now()

            # Reset the counter if the period has passed
            if (now - last_reset).total_seconds() > period:
                calls_made = 0
                last_reset = now

            # If we've hit the limit, wait until period resets
            if calls_made >= calls:
                wait_time = period - (now - last_reset).total_seconds()
                if wait_time > 0:
                    await asyncio.sleep(wait_time)
                    last_reset = datetime.now()
                    calls_made = 0

            calls_made += 1
            return await func(*args, **kwargs)
        return wrapper
    return decorator

def validate_collection_id(collection_id: str) -> bool:
    """Validate collection ID format. Adjust as needed."""
    return bool(collection_id and isinstance(collection_id, str))

def validate_url(url: str) -> bool:
    """Validate URL format."""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False

@server.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools for interacting with Needle."""
    return [
        Tool(
            name="list_collections",
            description="List all collections you have access to",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="create_collection",
            description="Create a new collection in Needle for storing documents",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Name of the collection"
                    }
                },
                "required": ["name"]
            }
        ),
        Tool(
            name="get_collection_details",
            description="Get detailed information about a specific collection",
            inputSchema={
                "type": "object",
                "properties": {
                    "collection_id": {
                        "type": "string",
                        "description": "ID of the collection to get details for"
                    }
                },
                "required": ["collection_id"]
            }
        ),
        Tool(
            name="get_collection_stats",
            description="Get statistics for a specific collection",
            inputSchema={
                "type": "object",
                "properties": {
                    "collection_id": {
                        "type": "string",
                        "description": "ID of the collection to get stats for"
                    }
                },
                "required": ["collection_id"]
            }
        ),
        Tool(
            name="list_collection_files",
            description="List all files in a specific collection",
            inputSchema={
                "type": "object",
                "properties": {
                    "collection_id": {
                        "type": "string",
                        "description": "ID of the collection to list files from"
                    }
                },
                "required": ["collection_id"]
            }
        ),
        Tool(
            name="add_file",
            description="Add a file to an existing collection by URL",
            inputSchema={
                "type": "object",
                "properties": {
                    "collection_id": {
                        "type": "string",
                        "description": "ID of the collection to add the file to"
                    },
                    "name": {
                        "type": "string",
                        "description": "Name of the file"
                    },
                    "url": {
                        "type": "string",
                        "description": "URL where the file can be downloaded from"
                    }
                },
                "required": ["collection_id", "name", "url"]
            }
        ),
        Tool(
            name="search",
            description="Search for relevant content within a collection",
            inputSchema={
                "type": "object",
                "properties": {
                    "collection_id": {
                        "type": "string",
                        "description": "ID of the collection to search in"
                    },
                    "query": {
                        "type": "string",
                        "description": "Search query in natural language"
                    }
                },
                "required": ["collection_id", "query"]
            }
        )
    ]

@server.call_tool()
@rate_limit(calls=10, period=1.0)  # Adjust if needed
async def call_tool(name: str, arguments: Any) -> Sequence[TextContent]:
    """Handle tool calls for Needle operations."""
    try:
        if name == "list_collections":
            collections = client.collections.list()
            result = {"collections": [{"id": c.id, "name": c.name, "created_at": str(c.created_at)} for c in collections]}
            
        elif name == "create_collection":
            if not isinstance(arguments, dict) or "name" not in arguments:
                raise ValueError("Missing required parameter: 'name'")
            collection = client.collections.create(name=arguments["name"])
            result = {"collection_id": collection.id}
            
        elif name == "get_collection_details":
            if not isinstance(arguments, dict) or "collection_id" not in arguments:
                raise ValueError("Missing required parameter: 'collection_id'")
            collection = client.collections.get(arguments["collection_id"])
            # collection is likely a model, so let's convert it to a dict for printing
            result = {
                "collection": {
                    "id": collection.id,
                    "name": collection.name,
                    "created_at": str(collection.created_at)
                }
            }
            
        elif name == "get_collection_stats":
            if not isinstance(arguments, dict) or "collection_id" not in arguments:
                raise ValueError("Missing required parameter: 'collection_id'")
            stats = client.collections.stats(arguments["collection_id"])
            # stats is likely a dict already
            result = {"stats": stats}
            
        elif name == "list_collection_files":
            if not isinstance(arguments, dict) or "collection_id" not in arguments:
                raise ValueError("Missing required parameter: 'collection_id'")
            files = client.collections.files.list(arguments["collection_id"])
            result = {"files": [{"id": f.id, "name": f.name, "status": f.status} for f in files]}
            
        elif name == "add_file":
            if not isinstance(arguments, dict) or not all(k in arguments for k in ["collection_id", "name", "url"]):
                raise ValueError("Missing required parameters")
            if not validate_collection_id(arguments["collection_id"]):
                raise ValueError("Invalid collection ID format")
            if not validate_url(arguments["url"]):
                raise ValueError("Invalid URL format")
            files = client.collections.files.add(
                collection_id=arguments["collection_id"],
                files=[FileToAdd(name=arguments["name"], url=arguments["url"])]
            )
            result = {"file_id": files[0].id}
            
        elif name == "search":
            if not isinstance(arguments, dict) or not all(k in arguments for k in ["collection_id", "query"]):
                raise ValueError("Missing required parameters")
            results = client.collections.search(arguments["collection_id"], text=arguments["query"])
            # results is a list of matches, convert to a dict
            result = [{
                "content": r.content,
                "score": r.score
            } for r in results]

        else:
            raise ValueError(f"Unknown tool: {name}")
        
        return [TextContent(
            type="text",
            text=json.dumps(result, indent=2, default=str)
        )]
        
    except NeedleError as e:
        error_message = f"Needle API error: {str(e)}"
        logger.error(error_message)
        return [TextContent(type="error", text=error_message)]
    except Exception as e:
        error_message = f"Error executing {name}: {str(e)}"
        logger.error(error_message)
        return [TextContent(type="error", text=error_message)]

async def main():
    import mcp
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options(),
        )

if __name__ == "__main__":
    asyncio.run(main())
