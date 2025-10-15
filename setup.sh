#!/bin/bash
# Setup script for Grafana MCP Server

set -e

echo "🚀 Setting up Grafana MCP Server..."

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "❌ uv is not installed. Please install it first:"
    echo "   curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

echo "✅ uv is installed"

# Check if .env file exists
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please edit .env file with your Grafana configuration"
else
    echo "✅ .env file already exists"
fi

# Install dependencies
echo "📦 Installing dependencies..."
uv pip install -e .

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your Grafana URL and credentials"
echo "2. Run the server with: grafana-mcp"
echo "3. Or test the client with: python examples/usage_example.py"
echo ""
echo "For Claude Desktop integration, add this to your config:"
echo '{
  "mcpServers": {
    "grafana": {
      "command": "uv",
      "args": ["--directory", "'$(pwd)'", "run", "grafana-mcp"],
      "env": {
        "GRAFANA_URL": "http://localhost:3000",
        "GRAFANA_API_KEY": "your-api-key-here"
      }
    }
  }
}'
