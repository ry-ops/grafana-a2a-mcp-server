# Grafana MCP Server

A Model Context Protocol (MCP) server that provides seamless integration between Claude AI and Grafana's HTTP API. This server enables AI agents to interact with Grafana dashboards, datasources, alerts, and more through a standardized protocol, with built-in support for agent-to-agent (a2a) communication patterns.

## Features

- 🔌 **Complete Grafana API Coverage**: Dashboards, datasources, alerts, folders, annotations, and more
- 🤖 **MCP Protocol Compliant**: Works seamlessly with Claude Desktop and other MCP clients
- 🔄 **A2A Protocol Ready**: Designed for agent-to-agent communication workflows
- 🔐 **Flexible Authentication**: Support for API keys and basic auth
- ⚡ **Async/Await**: Built on modern async Python for optimal performance
- 📦 **UV Compatible**: Fast dependency management with uv

## Installation

### Prerequisites

- Python 3.10 or higher
- [uv](https://github.com/astral-sh/uv) package manager (recommended)
- Access to a Grafana instance

### Using UV (Recommended)

```bash
# Clone or navigate to the project directory
cd grafana-mcp-server

# Install dependencies
uv pip install -e .

# Or install in development mode
uv pip install -e ".[dev]"
```

### Using pip

```bash
pip install -e .
```

## Configuration

The server uses environment variables for configuration. Create a `.env` file or set these variables:

```bash
# Required: Grafana instance URL
GRAFANA_URL=http://localhost:3000

# Option 1: API Key authentication (recommended)
GRAFANA_API_KEY=your-api-key-here

# Option 2: Basic authentication
GRAFANA_USERNAME=admin
GRAFANA_PASSWORD=admin
```

### Generating a Grafana API Key

1. Log into your Grafana instance
2. Navigate to **Configuration** → **API Keys**
3. Click **New API Key**
4. Set a name and role (Editor or Admin recommended)
5. Copy the generated key to your `.env` file

## Usage

### Running the Server

```bash
# Using the installed script
grafana-mcp

# Or directly with Python
python -m grafana_mcp.server

# Or with uv
uv run python -m grafana_mcp.server
```

### Integrating with Claude Desktop

Add this configuration to your Claude Desktop config file:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "grafana": {
      "command": "uv",
      "args": [
        "--directory",
        "/path/to/grafana-mcp-server",
        "run",
        "grafana-mcp"
      ],
      "env": {
        "GRAFANA_URL": "http://localhost:3000",
        "GRAFANA_API_KEY": "your-api-key-here"
      }
    }
  }
}
```

### Using with Other MCP Clients

The server communicates via stdio and follows the MCP specification. Any MCP-compatible client can connect to it.

## Available Tools

The server exposes the following tools to Claude and other AI agents:

### Dashboard Operations

- **grafana_list_dashboards**: Search and list dashboards
  ```json
  { "query": "optional search term" }
  ```

- **grafana_get_dashboard**: Get detailed dashboard information
  ```json
  { "uid": "dashboard-uid" }
  ```

- **grafana_create_dashboard**: Create a new dashboard
  ```json
  {
    "title": "My Dashboard",
    "tags": ["monitoring", "prod"],
    "folder_uid": "optional-folder-uid"
  }
  ```

### Datasource Operations

- **grafana_list_datasources**: List all configured datasources
- **grafana_get_datasource**: Get datasource details
  ```json
  { "uid": "datasource-uid" }
  ```

### Alert Operations

- **grafana_list_alerts**: List all alert rules

### Folder Operations

- **grafana_list_folders**: List all folders
- **grafana_create_folder**: Create a new folder
  ```json
  {
    "title": "My Folder",
    "uid": "optional-custom-uid"
  }
  ```

### Annotation Operations

- **grafana_create_annotation**: Create dashboard annotations
  ```json
  {
    "text": "Deployment completed",
    "tags": ["deployment", "production"],
    "time": 1234567890000,
    "time_end": 1234567899000
  }
  ```

### System Operations

- **grafana_health_check**: Check API connectivity
- **grafana_get_current_user**: Get authenticated user info

## Agent-to-Agent (A2A) Protocol Support

This MCP server is designed with a2a communication in mind:

### A2A Communication Patterns

1. **Tool Exposure**: All Grafana operations are exposed as standardized MCP tools that any agent can discover and invoke

2. **Stateless Design**: Each tool call is independent, making it ideal for distributed agent systems

3. **JSON-Based Communication**: All inputs and outputs use JSON, facilitating easy serialization for agent communication

4. **Error Handling**: Comprehensive error responses help agents recover gracefully from failures

### Example A2A Workflow

```python
# Agent 1 (Monitoring Agent) creates an alert
{
  "tool": "grafana_create_annotation",
  "arguments": {
    "text": "High CPU detected on server-01",
    "tags": ["alert", "cpu", "server-01"]
  }
}

# Agent 2 (Dashboard Agent) queries for recent alerts
{
  "tool": "grafana_list_dashboards",
  "arguments": {
    "query": "alerts"
  }
}

# Agent 3 (Reporting Agent) generates a report
{
  "tool": "grafana_get_dashboard",
  "arguments": {
    "uid": "system-overview"
  }
}
```

## Architecture

```
┌─────────────────┐
│   Claude AI     │
│  (MCP Client)   │
└────────┬────────┘
         │ MCP Protocol (stdio)
         ↓
┌─────────────────┐
│ Grafana MCP     │
│     Server      │
│  ┌───────────┐  │
│  │  Tools    │  │
│  │ Registry  │  │
│  └─────┬─────┘  │
│        ↓        │
│  ┌───────────┐  │
│  │ Grafana   │  │
│  │  Client   │  │
│  └─────┬─────┘  │
└────────┼────────┘
         │ HTTPS
         ↓
┌─────────────────┐
│   Grafana API   │
│  (HTTP Server)  │
└─────────────────┘
```

## Development

### Running Tests

```bash
# Install dev dependencies
uv pip install -e ".[dev]"

# Run tests
pytest

# Run with coverage
pytest --cov=grafana_mcp
```

### Code Formatting

```bash
# Format code
black src/

# Lint code
ruff src/
```

### Project Structure

```
grafana-mcp-server/
├── src/
│   └── grafana_mcp/
│       ├── __init__.py
│       └── server.py          # Main server implementation
├── tests/
│   └── test_server.py
├── pyproject.toml             # Project configuration
├── README.md
└── .env.example
```

## API Reference

### GrafanaConfig

Configuration model for the Grafana client.

```python
class GrafanaConfig:
    base_url: str              # Grafana instance URL
    api_key: Optional[str]     # API key for authentication
    username: Optional[str]    # Username for basic auth
    password: Optional[str]    # Password for basic auth
```

### GrafanaClient

Async HTTP client for Grafana API operations.

```python
client = GrafanaClient(config)
await client.list_dashboards(query="monitoring")
await client.get_dashboard(uid="abc123")
await client.create_annotation(text="Event", tags=["deploy"])
await client.close()
```

## Troubleshooting

### Connection Issues

1. Verify Grafana URL is correct and accessible
2. Check that API key has sufficient permissions
3. Ensure firewall allows connections to Grafana

### Authentication Errors

- Verify API key is valid and not expired
- Check that user has necessary role (Editor/Admin)
- Ensure credentials in `.env` are correct

### Tool Execution Failures

- Check Grafana logs for API errors
- Verify the resource (dashboard, folder, etc.) exists
- Ensure input parameters match required schema

## Contributing

Contributions are welcome! Please feel free to submit issues and pull requests.

## License

MIT License - see LICENSE file for details

## Resources

- [Grafana HTTP API Documentation](https://grafana.com/docs/grafana/latest/developers/http_api/)
- [Model Context Protocol Specification](https://spec.modelcontextprotocol.io/)
- [UV Package Manager](https://github.com/astral-sh/uv)
- [Claude AI](https://www.anthropic.com/claude)

## Support

For issues and questions:
- Open an issue on GitHub
- Check Grafana API documentation
- Review MCP specification

---

Built with ❤️ for the AI and DevOps communities
