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
            name="needle_list_collections",
            description="""List Needle collections. Returns maximum of 20 results. Get more results by increasing the offset.
            Returns detailed information including collection IDs, names, and creation dates. Use this tool when you need to:
            - Get an overview of available document collections
            - Find collection IDs for subsequent operations
            - Verify collection existence before performing operations
            The response includes metadata that's required for other Needle operations.""",
            inputSchema={
                "type": "object",
                "properties": {
                    "offset": {
                        "type": "number",
                        "description": "The offset to start listing from. Default is 0.",
                        "default": 0
                    }
                },
                "required": []
            }
        ),
        Tool(
            name="needle_create_collection",
            description="""Create a new document collection in Needle for organizing and searching documents. 
            A collection acts as a container for related documents and enables semantic search across its contents.
            Use this tool when you need to:
            - Start a new document organization
            - Group related documents together
            - Set up a searchable document repository
            Returns a collection ID that's required for subsequent operations. Choose a descriptive name that 
            reflects the collection's purpose for better organization.""",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "A clear, descriptive name for the collection that reflects its purpose and contents"
                    }
                },
                "required": ["name"]
            }
        ),
        Tool(
            name="needle_get_collection_details",
            description="""Fetch comprehensive metadata about a specific Needle collection. 
            Provides detailed information about the collection's configuration, creation date, and current status.
            Use this tool when you need to:
            - Verify a collection's existence and configuration
            - Check collection metadata before operations
            - Get creation date and other attributes
            Requires a valid collection ID and returns detailed collection metadata. Will error if collection doesn't exist.""",
            inputSchema={
                "type": "object",
                "properties": {
                    "collection_id": {
                        "type": "string",
                        "description": "The unique collection identifier returned from needle_create_collection or needle_list_collections"
                    }
                },
                "required": ["collection_id"]
            }
        ),
        Tool(
            name="needle_get_collection_stats",
            description="""Retrieve detailed statistical information about a Needle collection's contents and status.
            Provides metrics including:
            - Total number of documents
            - Processing status of documents
            - Storage usage and limits
            - Index status and health
            Use this tool to:
            - Monitor collection size and growth
            - Verify processing completion
            - Check collection health before operations
            Essential for ensuring collection readiness before performing searches.""",
            inputSchema={
                "type": "object",
                "properties": {
                    "collection_id": {
                        "type": "string",
                        "description": "The unique collection identifier to get statistics for"
                    }
                },
                "required": ["collection_id"]
            }
        ),
        Tool(
            name="needle_list_files",
            description="""List all documents stored within a specific Needle collection with their current status.
            Returns detailed information about each file including:
            - File ID and name
            - Processing status (pending, processing, complete, error)
            - Upload date and metadata
            Use this tool when you need to:
            - Inventory available documents
            - Check processing status of uploads
            - Get file IDs for reference
            - Verify document availability before searching
            Essential for monitoring document processing completion before performing searches.""",
            inputSchema={
                "type": "object",
                "properties": {
                    "collection_id": {
                        "type": "string",
                        "description": "The unique collection identifier to list files from"
                    }
                },
                "required": ["collection_id"]
            }
        ),
        Tool(
            name="needle_add_file",
            description="""Add a new document to a Needle collection by providing a URL for download.
            Supports multiple file formats including:
            - PDF documents
            - Microsoft Word files (DOC, DOCX)
            - Plain text files (TXT)
            - Web pages (HTML)
            
            The document will be:
            1. Downloaded from the provided URL
            2. Processed for text extraction
            3. Indexed for semantic search
            
            Use this tool when you need to:
            - Add new documents to a collection
            - Make documents searchable
            - Expand your knowledge base
            
            Important: Documents require processing time before they're searchable.
            Check processing status using needle_list_files before searching new content.""",
            inputSchema={
                "type": "object",
                "properties": {
                    "collection_id": {
                        "type": "string",
                        "description": "The unique collection identifier where the file will be added"
                    },
                    "name": {
                        "type": "string",
                        "description": "A descriptive filename that will help identify this document in results"
                    },
                    "url": {
                        "type": "string",
                        "description": "Public URL where the document can be downloaded from"
                    }
                },
                "required": ["collection_id", "name", "url"]
            }
        ),
        Tool(
            name="needle_search",
            description="""Perform intelligent semantic search across documents in a Needle collection.
            This tool uses advanced embedding technology to find relevant content based on meaning,
            not just keywords. The search:
            - Understands natural language queries
            - Finds conceptually related content
            - Returns relevant text passages with source information
            - Ranks results by semantic relevance
            
            Use this tool when you need to:
            - Find specific information within documents
            - Answer questions from document content
            - Research topics across multiple documents
            - Locate relevant passages and their sources
            
            More effective than traditional keyword search for:
            - Natural language questions
            - Conceptual queries
            - Finding related content
            
            Returns matching text passages with their source file IDs.""",
            inputSchema={
                "type": "object",
                "properties": {
                    "collection_id": {
                        "type": "string",
                        "description": "The unique collection identifier to search within"
                    },
                    "query": {
                        "type": "string",
                        "description": "Natural language query describing the information you're looking for"
                    }
                },
                "required": ["collection_id", "query"]
            }
        )
    ]

@server.call_tool()
@rate_limit(calls=10, period=1.0)
async def call_tool(name: str, arguments: Any) -> Sequence[TextContent]:
    """Handle tool calls for Needle operations."""
    try:
        if name == "needle_list_collections":
            offset = 0
            if isinstance(arguments, dict) and "offset" in arguments:
                offset = int(arguments["offset"])
            
            collections = client.collections.list()
            collection_data = [{"id": c.id, "name": c.name, "created_at": str(c.created_at)} for c in collections]
            
            # Apply pagination
            paginated_collections = collection_data[offset:offset + 20]
            result = {"collections": paginated_collections}
            
        elif name == "needle_create_collection":
            if not isinstance(arguments, dict) or "name" not in arguments:
                raise ValueError("Missing required parameter: 'name'")
            collection = client.collections.create(name=arguments["name"])
            result = {"collection_id": collection.id}
            
        elif name == "needle_get_collection_details":
            if not isinstance(arguments, dict) or "collection_id" not in arguments:
                raise ValueError("Missing required parameter: 'collection_id'")
            collection = client.collections.get(arguments["collection_id"])
            result = {
                "collection": {
                    "id": collection.id,
                    "name": collection.name,
                    "created_at": str(collection.created_at)
                }
            }
            
        elif name == "needle_get_collection_stats":
            if not isinstance(arguments, dict) or "collection_id" not in arguments:
                raise ValueError("Missing required parameter: 'collection_id'")
            stats = client.collections.stats(arguments["collection_id"])
            result = {"stats": stats}
            
        elif name == "needle_list_files":
            if not isinstance(arguments, dict) or "collection_id" not in arguments:
                raise ValueError("Missing required parameter: 'collection_id'")
            files = client.collections.files.list(arguments["collection_id"])
            result = {"files": [{"id": f.id, "name": f.name, "status": f.status} for f in files]}
            
        elif name == "needle_add_file":
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
            
        elif name == "needle_search":
            if not isinstance(arguments, dict) or not all(k in arguments for k in ["collection_id", "query"]):
                raise ValueError("Missing required parameters")
            
            results = client.collections.search(
                collection_id=arguments["collection_id"],
                text=arguments["query"],
                # Optionally add these parameters if needed:
                # max_distance=0.8,  # Adjust threshold as needed
                # top_k=5  # Adjust number of results as needed
            )
            
            result = [{
                "content": r.content,
                "file_id": r.file_id,
            } for r in results]

            return [TextContent(
                type="text",
                text=json.dumps(result, indent=2, default=str)
            )]

        else:
            raise ValueError(f"Unknown tool: {name}")
        
        return [TextContent(
            type="text",
            text=json.dumps(result, indent=2, default=str)
        )]
        
    except NeedleError as e:
        error_message = f"Needle API error: {str(e)}"
        logger.error(error_message)
        return [TextContent(
            type="text",
            text=error_message
        )]
    except Exception as e:
        error_message = f"Error executing {name}: {str(e)}"
        logger.error(error_message)
        return [TextContent(
            type="text",
            text=error_message
        )]

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
