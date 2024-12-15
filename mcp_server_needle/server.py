from typing import List, Optional, Dict, Any
from mcp_core import MCPServer, Resource, Tool
from needle.v1 import NeedleClient
from needle.v1.models import FileToAdd, Error as NeedleError
import os
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class NeedleMCPServer(MCPServer):
    """
    MCP server implementation for Needle RAG integration.
    Provides tools for document collection management and semantic search.
    """

    def __init__(self):
        super().__init__()
        self._setup_client()
        
    def _setup_client(self) -> None:
        """Initialize the Needle client with API key from environment."""
        api_key = os.getenv("NEEDLE_API_KEY")
        if not api_key:
            raise ValueError("NEEDLE_API_KEY environment variable must be set")
        self.client = NeedleClient(api_key=api_key)

    async def get_tools(self) -> List[Tool]:
        """Define the available tools for Claude to use based on Needle API capabilities."""
        return [
            Tool(
                name="list_collections",
                description="List all collections you have access to (owned, editor, or viewer)",
                parameters={
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            ),
            Tool(
                name="create_collection",
                description="Create a new collection in Needle for storing documents",
                parameters={
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
                parameters={
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
                parameters={
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
                parameters={
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
                parameters={
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
                parameters={
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

    async def invoke_tool(self, tool_name: str, parameters: dict) -> Dict[str, Any]:
        """Execute the requested tool with given parameters."""
        try:
            if tool_name == "list_collections":
                return await self._list_collections()
            elif tool_name == "create_collection":
                return await self._create_collection(parameters)
            elif tool_name == "get_collection_details":
                return await self._get_collection_details(parameters)
            elif tool_name == "get_collection_stats":
                return await self._get_collection_stats(parameters)
            elif tool_name == "list_collection_files":
                return await self._list_collection_files(parameters)
            elif tool_name == "add_file":
                return await self._add_file(parameters)
            elif tool_name == "search":
                return await self._search(parameters)
            else:
                raise ValueError(f"Unknown tool: {tool_name}")
        except NeedleError as e:
            logger.error(f"Needle API error: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error executing {tool_name}: {str(e)}")
            raise

    async def _list_collections(self) -> Dict[str, List[Dict[str, Any]]]:
        """List all collections the user has access to."""
        collections = self.client.collections.list()
        return {"collections": [{"id": c.id, "name": c.name} for c in collections]}

    async def _create_collection(self, parameters: dict) -> Dict[str, str]:
        """Create a new collection in Needle."""
        collection = self.client.collections.create(name=parameters["name"])
        return {"collection_id": collection.id}

    async def _get_collection_details(self, parameters: dict) -> Dict[str, Any]:
        """Get details about a specific collection."""
        collection = self.client.collections.get(parameters["collection_id"])
        return {"collection": collection}

    async def _get_collection_stats(self, parameters: dict) -> Dict[str, Any]:
        """Get statistics for a specific collection."""
        stats = self.client.collections.stats(parameters["collection_id"])
        return {"stats": stats}

    async def _list_collection_files(self, parameters: dict) -> Dict[str, List[Dict[str, Any]]]:
        """List files in a specific collection."""
        files = self.client.collections.files.list(parameters["collection_id"])
        return {"files": [{"id": f.id, "name": f.name} for f in files]}

    async def _add_file(self, parameters: dict) -> Dict[str, str]:
        """Add a file to an existing collection."""
        files = self.client.collections.files.add(
            collection_id=parameters["collection_id"],
            files=[
                FileToAdd(
                    name=parameters["name"],
                    url=parameters["url"]
                )
            ]
        )
        return {"file_id": files[0].id}

    async def _search(self, parameters: dict) -> List[Dict[str, Any]]:
        """Search for content within a collection."""
        results = self.client.collections.search(
            parameters["collection_id"], 
            text=parameters["query"]
        )
        return [{"content": r.content, "score": r.score} for r in results]

    async def get_resources(self) -> List[Resource]:
        """No static resources are provided by this server."""
        return [] 