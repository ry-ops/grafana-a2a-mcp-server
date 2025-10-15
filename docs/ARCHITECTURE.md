# Architecture Overview

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    User / AI Agent Layer                     │
│                                                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Claude     │  │   Other      │  │   Custom     │      │
│  │   Desktop    │  │   MCP        │  │   Agent      │      │
│  │              │  │   Clients    │  │              │      │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘      │
│         │                 │                 │                │
└─────────┼─────────────────┼─────────────────┼────────────────┘
          │                 │                 │
          │   MCP Protocol  │                 │
          │   (stdio/JSON)  │                 │
          │                 │                 │
┌─────────┴─────────────────┴─────────────────┴────────────────┐
│                                                                │
│              Grafana MCP Server (This Package)                │
│                                                                │
│  ┌──────────────────────────────────────────────────────┐    │
│  │              MCP Server Component                     │    │
│  │  ┌────────────────────────────────────────────────┐  │    │
│  │  │           Tool Registry                        │  │    │
│  │  │                                                │  │    │
│  │  │  • grafana_list_dashboards                    │  │    │
│  │  │  • grafana_get_dashboard                      │  │    │
│  │  │  • grafana_create_dashboard                   │  │    │
│  │  │  • grafana_list_datasources                   │  │    │
│  │  │  • grafana_get_datasource                     │  │    │
│  │  │  • grafana_list_alerts                        │  │    │
│  │  │  • grafana_list_folders                       │  │    │
│  │  │  • grafana_create_folder                      │  │    │
│  │  │  • grafana_create_annotation                  │  │    │
│  │  │  • grafana_health_check                       │  │    │
│  │  │  • grafana_get_current_user                   │  │    │
│  │  └────────────────────────────────────────────────┘  │    │
│  │                           │                           │    │
│  │                           ↓                           │    │
│  │  ┌────────────────────────────────────────────────┐  │    │
│  │  │          Tool Execution Handler                │  │    │
│  │  │  - Parameter validation                        │  │    │
│  │  │  - Error handling                              │  │    │
│  │  │  - Response formatting                         │  │    │
│  │  └────────────────────────────────────────────────┘  │    │
│  └──────────────────────┬───────────────────────────────┘    │
│                         │                                     │
│                         ↓                                     │
│  ┌──────────────────────────────────────────────────────┐    │
│  │              Grafana API Client                       │    │
│  │  ┌────────────────────────────────────────────────┐  │    │
│  │  │           HTTP Client (httpx)                  │  │    │
│  │  │  - Async/await support                         │  │    │
│  │  │  - Connection pooling                          │  │    │
│  │  │  - Timeout handling                            │  │    │
│  │  └────────────────────────────────────────────────┘  │    │
│  │  ┌────────────────────────────────────────────────┐  │    │
│  │  │           Authentication Layer                 │  │    │
│  │  │  - API Key (Bearer token)                      │  │    │
│  │  │  - Basic Auth (username/password)              │  │    │
│  │  └────────────────────────────────────────────────┘  │    │
│  │  ┌────────────────────────────────────────────────┐  │    │
│  │  │           API Method Implementations           │  │    │
│  │  │  - Dashboard operations                        │  │    │
│  │  │  - Datasource operations                       │  │    │
│  │  │  - Alert operations                            │  │    │
│  │  │  - Folder operations                           │  │    │
│  │  │  - Annotation operations                       │  │    │
│  │  │  - System operations                           │  │    │
│  │  └────────────────────────────────────────────────┘  │    │
│  └──────────────────────┬───────────────────────────────┘    │
│                         │                                     │
└─────────────────────────┼─────────────────────────────────────┘
                          │
                          │ HTTPS/HTTP
                          │
┌─────────────────────────┴─────────────────────────────────────┐
│                                                                │
│                    Grafana HTTP API                           │
│                                                                │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐        │
│  │  Dashboards  │  │  Datasources │  │    Alerts    │        │
│  └──────────────┘  └──────────────┘  └──────────────┘        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐        │
│  │   Folders    │  │ Annotations  │  │     Users    │        │
│  └──────────────┘  └──────────────┘  └──────────────┘        │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

## Data Flow

### Example: Listing Dashboards

```
1. User Request:
   Claude Desktop: "List all my Grafana dashboards"

2. MCP Protocol:
   {
     "method": "tools/call",
     "params": {
       "name": "grafana_list_dashboards",
       "arguments": {"query": ""}
     }
   }

3. Tool Execution:
   MCP Server → GrafanaClient.list_dashboards()

4. HTTP Request:
   GET /api/search?type=dash-db
   Headers: Authorization: Bearer {api_key}

5. Grafana Response:
   [
     {"uid": "abc123", "title": "CPU Dashboard"},
     {"uid": "def456", "title": "Memory Dashboard"}
   ]

6. MCP Response:
   {
     "content": [
       {
         "type": "text",
         "text": "[{\"uid\":\"abc123\",...}]"
       }
     ]
   }

7. User Display:
   Claude Desktop: "I found 2 dashboards:
   - CPU Dashboard (uid: abc123)
   - Memory Dashboard (uid: def456)"
```

## Component Details

### MCP Server Component
- **Purpose**: Implements Model Context Protocol
- **Technology**: Python asyncio, MCP SDK
- **Responsibilities**:
  - Tool registration and discovery
  - Parameter validation
  - Protocol compliance
  - Error handling and formatting

### Grafana API Client
- **Purpose**: Interface with Grafana HTTP API
- **Technology**: httpx (async HTTP)
- **Responsibilities**:
  - HTTP request/response handling
  - Authentication management
  - API endpoint mapping
  - Response parsing

### Authentication Layer
- **API Key**: Preferred method, uses Bearer token
- **Basic Auth**: Fallback for username/password
- **Configuration**: Environment variables or config file

## A2A Communication Pattern

```
┌─────────────┐         ┌─────────────┐
│  Monitor    │         │  Analysis   │
│  Agent      │         │  Agent      │
└──────┬──────┘         └──────┬──────┘
       │                       │
       │ grafana_list_alerts() │
       └───────────┬────────────┘
                   │
                   ↓
         ┌─────────────────┐
         │  Grafana MCP    │
         │     Server      │
         └────────┬────────┘
                  │
       ┌──────────┴──────────┐
       │                     │
       ↓                     ↓
┌──────────────┐    ┌──────────────┐
│  Dashboard   │    │   Response   │
│  Agent       │    │   Agent      │
└──────┬───────┘    └──────┬───────┘
       │                   │
       │ get_dashboard()   │ create_annotation()
       └───────────┬───────┘
                   │
                   ↓
         ┌─────────────────┐
         │  Grafana API    │
         └─────────────────┘
```

## Security Considerations

1. **API Key Storage**: Environment variables, never in code
2. **HTTPS**: Always use HTTPS in production
3. **Permissions**: Use minimum required API key permissions
4. **Validation**: Input validation on all tool parameters
5. **Error Handling**: Never expose sensitive data in errors

## Performance Characteristics

- **Async I/O**: Non-blocking operations
- **Connection Pooling**: Reuse HTTP connections
- **Timeout**: 30-second default timeout
- **Rate Limiting**: Respect Grafana API limits
- **Caching**: No built-in caching (stateless design)

## Deployment Options

### Option 1: Local Development
```bash
python -m grafana_mcp.server
```

### Option 2: Claude Desktop
```json
{
  "mcpServers": {
    "grafana": {
      "command": "uv",
      "args": ["--directory", "/path", "run", "grafana-mcp"]
    }
  }
}
```

### Option 3: Docker (Future)
```bash
docker run -e GRAFANA_URL=... grafana-mcp-server
```

### Option 4: Cloud Service (Future)
```
Deploy as a service accessible to multiple agents
```

## Extension Points

1. **New Tools**: Add new Grafana API operations
2. **Custom Auth**: Implement OAuth or other auth methods
3. **Caching**: Add Redis or memory cache
4. **Events**: WebSocket support for real-time updates
5. **Bulk Operations**: Batch multiple API calls
6. **Plugins**: Support for Grafana plugin APIs

## Dependencies

```
Core:
- mcp >= 1.0.0          (MCP protocol)
- httpx >= 0.27.0       (HTTP client)
- pydantic >= 2.0.0     (Data validation)

Development:
- pytest >= 8.0.0       (Testing)
- black >= 24.0.0       (Formatting)
- ruff >= 0.3.0         (Linting)

Runtime:
- Python 3.10+
- Grafana 9.0+ (API compatibility)
```

## Future Architecture

```
┌─────────────────────────────────────┐
│      Load Balancer / API Gateway    │
└─────────────┬───────────────────────┘
              │
     ┌────────┴────────┐
     │                 │
┌────▼─────┐    ┌─────▼────┐
│ MCP      │    │  MCP     │
│ Server 1 │    │ Server 2 │
└────┬─────┘    └─────┬────┘
     │                │
     └────────┬───────┘
              │
     ┌────────▼──────────┐
     │   Redis Cache     │
     └────────┬──────────┘
              │
     ┌────────▼──────────┐
     │   Grafana API     │
     └───────────────────┘
```
