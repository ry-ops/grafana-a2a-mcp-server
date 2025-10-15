"""
Grafana MCP Server

An MCP server that provides integration with the Grafana API, enabling
Claude AI and other a2a-compatible agents to interact with Grafana dashboards,
datasources, alerts, and more.
"""

import asyncio
import os
from typing import Any, Optional
from urllib.parse import urljoin

import httpx
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent, ImageContent, EmbeddedResource
from pydantic import BaseModel, Field


class GrafanaConfig(BaseModel):
    """Configuration for Grafana API connection"""

    base_url: str = Field(..., description="Grafana instance base URL")
    api_key: Optional[str] = Field(None, description="Grafana API key for authentication")
    username: Optional[str] = Field(None, description="Username for basic auth")
    password: Optional[str] = Field(None, description="Password for basic auth")


class GrafanaClient:
    """Client for interacting with Grafana API"""

    def __init__(self, config: GrafanaConfig):
        self.config = config
        self.base_url = config.base_url.rstrip("/")

        # Setup authentication headers
        headers = {"Content-Type": "application/json"}
        if config.api_key:
            headers["Authorization"] = f"Bearer {config.api_key}"

        # Setup HTTP client with authentication
        auth = None
        if config.username and config.password:
            auth = (config.username, config.password)

        self.client = httpx.AsyncClient(
            base_url=self.base_url, headers=headers, auth=auth, timeout=30.0
        )

    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()

    async def _request(
        self, method: str, endpoint: str, **kwargs
    ) -> dict[str, Any] | list[Any]:
        """Make an authenticated request to Grafana API"""
        url = f"/api/{endpoint.lstrip('/')}"
        response = await self.client.request(method, url, **kwargs)
        response.raise_for_status()
        return response.json()

    # Dashboard operations
    async def list_dashboards(self, query: str = "") -> list[dict[str, Any]]:
        """Search for dashboards"""
        params = {"type": "dash-db"}
        if query:
            params["query"] = query
        return await self._request("GET", "search", params=params)

    async def get_dashboard(self, uid: str) -> dict[str, Any]:
        """Get dashboard by UID"""
        return await self._request("GET", f"dashboards/uid/{uid}")

    async def create_dashboard(self, dashboard: dict[str, Any]) -> dict[str, Any]:
        """Create a new dashboard"""
        return await self._request("POST", "dashboards/db", json=dashboard)

    async def update_dashboard(self, dashboard: dict[str, Any]) -> dict[str, Any]:
        """Update an existing dashboard"""
        return await self._request("POST", "dashboards/db", json=dashboard)

    async def delete_dashboard(self, uid: str) -> dict[str, Any]:
        """Delete dashboard by UID"""
        return await self._request("DELETE", f"dashboards/uid/{uid}")

    # Datasource operations
    async def list_datasources(self) -> list[dict[str, Any]]:
        """List all datasources"""
        return await self._request("GET", "datasources")

    async def get_datasource(self, uid: str) -> dict[str, Any]:
        """Get datasource by UID"""
        return await self._request("GET", f"datasources/uid/{uid}")

    # Alert operations
    async def list_alerts(self) -> list[dict[str, Any]]:
        """List all alert rules"""
        return await self._request("GET", "ruler/grafana/api/v1/rules")

    async def get_alert_rule(self, uid: str) -> dict[str, Any]:
        """Get alert rule by UID"""
        return await self._request("GET", f"v1/provisioning/alert-rules/{uid}")

    # Folder operations
    async def list_folders(self) -> list[dict[str, Any]]:
        """List all folders"""
        return await self._request("GET", "folders")

    async def create_folder(self, title: str, uid: Optional[str] = None) -> dict[str, Any]:
        """Create a new folder"""
        data = {"title": title}
        if uid:
            data["uid"] = uid
        return await self._request("POST", "folders", json=data)

    # Annotation operations
    async def create_annotation(
        self,
        text: str,
        tags: list[str],
        time: Optional[int] = None,
        time_end: Optional[int] = None,
    ) -> dict[str, Any]:
        """Create an annotation"""
        data = {"text": text, "tags": tags}
        if time:
            data["time"] = time
        if time_end:
            data["timeEnd"] = time_end
        return await self._request("POST", "annotations", json=data)

    # Organization operations
    async def get_current_org(self) -> dict[str, Any]:
        """Get current organization"""
        return await self._request("GET", "org")

    # User operations
    async def get_current_user(self) -> dict[str, Any]:
        """Get current user"""
        return await self._request("GET", "user")

    # Health check
    async def health_check(self) -> dict[str, Any]:
        """Check Grafana API health"""
        return await self._request("GET", "health")


class GrafanaMCPServer:
    """MCP Server for Grafana API integration"""

    def __init__(self):
        self.server = Server("grafana-mcp-server")
        self.grafana_client: Optional[GrafanaClient] = None
        self._setup_handlers()

    def _setup_handlers(self):
        """Setup MCP protocol handlers"""

        @self.server.list_tools()
        async def list_tools() -> list[Tool]:
            """List available Grafana tools"""
            return [
                Tool(
                    name="grafana_list_dashboards",
                    description="Search and list Grafana dashboards. Optionally filter by search query.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Optional search query to filter dashboards",
                            }
                        },
                    },
                ),
                Tool(
                    name="grafana_get_dashboard",
                    description="Get detailed information about a specific Grafana dashboard by UID",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "uid": {
                                "type": "string",
                                "description": "The unique identifier (UID) of the dashboard",
                            }
                        },
                        "required": ["uid"],
                    },
                ),
                Tool(
                    name="grafana_create_dashboard",
                    description="Create a new Grafana dashboard",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "title": {"type": "string", "description": "Dashboard title"},
                            "tags": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Dashboard tags",
                            },
                            "folder_uid": {
                                "type": "string",
                                "description": "UID of folder to place dashboard in",
                            },
                        },
                        "required": ["title"],
                    },
                ),
                Tool(
                    name="grafana_list_datasources",
                    description="List all configured Grafana datasources",
                    inputSchema={"type": "object", "properties": {}},
                ),
                Tool(
                    name="grafana_get_datasource",
                    description="Get detailed information about a specific datasource by UID",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "uid": {
                                "type": "string",
                                "description": "The unique identifier (UID) of the datasource",
                            }
                        },
                        "required": ["uid"],
                    },
                ),
                Tool(
                    name="grafana_list_alerts",
                    description="List all alert rules in Grafana",
                    inputSchema={"type": "object", "properties": {}},
                ),
                Tool(
                    name="grafana_list_folders",
                    description="List all folders in Grafana",
                    inputSchema={"type": "object", "properties": {}},
                ),
                Tool(
                    name="grafana_create_folder",
                    description="Create a new folder in Grafana",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "title": {"type": "string", "description": "Folder title"},
                            "uid": {
                                "type": "string",
                                "description": "Optional UID for the folder",
                            },
                        },
                        "required": ["title"],
                    },
                ),
                Tool(
                    name="grafana_create_annotation",
                    description="Create an annotation in Grafana to mark events on dashboards",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "text": {
                                "type": "string",
                                "description": "Annotation text/description",
                            },
                            "tags": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Tags for the annotation",
                            },
                            "time": {
                                "type": "integer",
                                "description": "Start time in milliseconds since epoch",
                            },
                            "time_end": {
                                "type": "integer",
                                "description": "End time in milliseconds since epoch",
                            },
                        },
                        "required": ["text", "tags"],
                    },
                ),
                Tool(
                    name="grafana_health_check",
                    description="Check the health status of the Grafana API connection",
                    inputSchema={"type": "object", "properties": {}},
                ),
                Tool(
                    name="grafana_get_current_user",
                    description="Get information about the currently authenticated user",
                    inputSchema={"type": "object", "properties": {}},
                ),
            ]

        @self.server.call_tool()
        async def call_tool(name: str, arguments: Any) -> list[TextContent]:
            """Handle tool calls"""
            if not self.grafana_client:
                return [
                    TextContent(
                        type="text",
                        text="Error: Grafana client not initialized. Please check configuration.",
                    )
                ]

            try:
                result = await self._execute_tool(name, arguments)
                import json

                return [TextContent(type="text", text=json.dumps(result, indent=2))]
            except httpx.HTTPStatusError as e:
                return [
                    TextContent(
                        type="text",
                        text=f"Grafana API error: {e.response.status_code} - {e.response.text}",
                    )
                ]
            except Exception as e:
                return [TextContent(type="text", text=f"Error executing tool: {str(e)}")]

    async def _execute_tool(self, name: str, arguments: dict[str, Any]) -> Any:
        """Execute the requested tool"""
        if name == "grafana_list_dashboards":
            query = arguments.get("query", "")
            return await self.grafana_client.list_dashboards(query)

        elif name == "grafana_get_dashboard":
            return await self.grafana_client.get_dashboard(arguments["uid"])

        elif name == "grafana_create_dashboard":
            dashboard_data = {
                "dashboard": {
                    "title": arguments["title"],
                    "tags": arguments.get("tags", []),
                    "timezone": "browser",
                    "schemaVersion": 16,
                    "version": 0,
                },
                "folderUid": arguments.get("folder_uid"),
                "overwrite": False,
            }
            return await self.grafana_client.create_dashboard(dashboard_data)

        elif name == "grafana_list_datasources":
            return await self.grafana_client.list_datasources()

        elif name == "grafana_get_datasource":
            return await self.grafana_client.get_datasource(arguments["uid"])

        elif name == "grafana_list_alerts":
            return await self.grafana_client.list_alerts()

        elif name == "grafana_list_folders":
            return await self.grafana_client.list_folders()

        elif name == "grafana_create_folder":
            return await self.grafana_client.create_folder(
                arguments["title"], arguments.get("uid")
            )

        elif name == "grafana_create_annotation":
            return await self.grafana_client.create_annotation(
                text=arguments["text"],
                tags=arguments["tags"],
                time=arguments.get("time"),
                time_end=arguments.get("time_end"),
            )

        elif name == "grafana_health_check":
            return await self.grafana_client.health_check()

        elif name == "grafana_get_current_user":
            return await self.grafana_client.get_current_user()

        else:
            raise ValueError(f"Unknown tool: {name}")

    async def run(self):
        """Run the MCP server"""
        # Initialize Grafana client from environment
        config = GrafanaConfig(
            base_url=os.getenv("GRAFANA_URL", "http://localhost:3000"),
            api_key=os.getenv("GRAFANA_API_KEY"),
            username=os.getenv("GRAFANA_USERNAME"),
            password=os.getenv("GRAFANA_PASSWORD"),
        )

        self.grafana_client = GrafanaClient(config)

        # Run the server
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(read_stream, write_stream, self.server.create_initialization_options())


def main():
    """Main entry point"""
    server = GrafanaMCPServer()
    asyncio.run(server.run())


if __name__ == "__main__":
    main()
