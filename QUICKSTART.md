# Quick Start Guide

Get up and running with the Grafana MCP Server in 5 minutes!

## Prerequisites

- Python 3.10 or higher
- UV package manager: `curl -LsSf https://astral.sh/uv/install.sh | sh`
- Access to a Grafana instance

## Step 1: Configure

Copy the environment template:

```bash
cp .env.example .env
```

Edit `.env` with your Grafana details:

```bash
GRAFANA_URL=http://localhost:3000
GRAFANA_API_KEY=your-api-key-here
```

To get a Grafana API key:
1. Log into Grafana
2. Go to Configuration → API Keys
3. Create a new API key with Editor or Admin role
4. Copy the key to your `.env` file

## Step 2: Install

Run the setup script:

```bash
chmod +x setup.sh
./setup.sh
```

Or manually:

```bash
uv pip install -e .
```

## Step 3: Test

Test the connection:

```bash
python examples/usage_example.py
```

This will:
- Check Grafana health
- List your dashboards
- List your datasources
- Create a test folder and annotation

## Step 4: Use with Claude Desktop

Add to your Claude Desktop config file:

**macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows:** `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "grafana": {
      "command": "uv",
      "args": [
        "--directory",
        "/absolute/path/to/grafana-mcp-server",
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

Restart Claude Desktop.

## Step 5: Try It Out!

In Claude Desktop, try these prompts:

- "List all my Grafana dashboards"
- "Show me the datasources I have configured"
- "Create a new folder called 'Production Monitoring'"
- "Add an annotation to mark this deployment"
- "What alerts are currently configured?"

## Available Commands

Run the MCP server:
```bash
grafana-mcp
# or
python -m grafana_mcp.server
# or
uv run python -m grafana_mcp.server
```

Run tests:
```bash
pytest
pytest --cov=grafana_mcp
```

Format code:
```bash
black src/ tests/
ruff check src/ tests/
```

## Troubleshooting

**"Connection refused"**
- Check that Grafana is running
- Verify GRAFANA_URL is correct

**"Unauthorized"**
- Verify your API key is valid
- Check API key permissions (needs Editor or Admin)

**"Tool not found"**
- Restart Claude Desktop after config changes
- Check that the path in config is absolute

## Next Steps

- Read the full [README.md](README.md)
- Check out [A2A Integration Guide](docs/A2A_INTEGRATION.md)
- Review [Contributing Guidelines](CONTRIBUTING.md)
- Explore the [example code](examples/usage_example.py)

## Common Use Cases

### Monitor dashboards
```
"Show me all dashboards related to CPU monitoring"
```

### Manage alerts
```
"List all active alerts and show me which ones are critical"
```

### Create annotations
```
"Mark this deployment in Grafana with a note about the new feature"
```

### Analyze datasources
```
"What datasources do I have? Which ones are Prometheus?"
```

Need help? Open an issue on GitHub!
