"""
Tests for Grafana MCP Server
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from grafana_mcp import GrafanaClient, GrafanaConfig, GrafanaMCPServer


@pytest.fixture
def grafana_config():
    """Create a test Grafana configuration"""
    return GrafanaConfig(
        base_url="http://localhost:3000",
        api_key="test-api-key",
    )


@pytest.fixture
def grafana_client(grafana_config):
    """Create a test Grafana client"""
    return GrafanaClient(grafana_config)


class TestGrafanaClient:
    """Tests for GrafanaClient"""

    @pytest.mark.asyncio
    async def test_health_check(self, grafana_client):
        """Test health check endpoint"""
        with patch.object(grafana_client, "_request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = {
                "commit": "abc123",
                "database": "ok",
                "version": "9.0.0",
            }

            result = await grafana_client.health_check()

            mock_request.assert_called_once_with("GET", "health")
            assert result["database"] == "ok"

    @pytest.mark.asyncio
    async def test_list_dashboards(self, grafana_client):
        """Test listing dashboards"""
        with patch.object(grafana_client, "_request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = [
                {"uid": "abc123", "title": "Test Dashboard", "type": "dash-db"},
                {"uid": "def456", "title": "Another Dashboard", "type": "dash-db"},
            ]

            result = await grafana_client.list_dashboards()

            mock_request.assert_called_once()
            assert len(result) == 2
            assert result[0]["title"] == "Test Dashboard"

    @pytest.mark.asyncio
    async def test_list_dashboards_with_query(self, grafana_client):
        """Test listing dashboards with search query"""
        with patch.object(grafana_client, "_request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = [
                {"uid": "abc123", "title": "CPU Dashboard", "type": "dash-db"}
            ]

            result = await grafana_client.list_dashboards(query="CPU")

            mock_request.assert_called_once_with(
                "GET", "search", params={"type": "dash-db", "query": "CPU"}
            )
            assert len(result) == 1

    @pytest.mark.asyncio
    async def test_get_dashboard(self, grafana_client):
        """Test getting a specific dashboard"""
        with patch.object(grafana_client, "_request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = {
                "dashboard": {
                    "uid": "abc123",
                    "title": "Test Dashboard",
                    "panels": [],
                },
                "meta": {"slug": "test-dashboard"},
            }

            result = await grafana_client.get_dashboard("abc123")

            mock_request.assert_called_once_with("GET", "dashboards/uid/abc123")
            assert result["dashboard"]["uid"] == "abc123"

    @pytest.mark.asyncio
    async def test_create_dashboard(self, grafana_client):
        """Test creating a dashboard"""
        with patch.object(grafana_client, "_request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = {
                "id": 1,
                "uid": "new123",
                "status": "success",
            }

            dashboard_data = {
                "dashboard": {"title": "New Dashboard", "tags": ["test"]},
                "overwrite": False,
            }

            result = await grafana_client.create_dashboard(dashboard_data)

            mock_request.assert_called_once_with("POST", "dashboards/db", json=dashboard_data)
            assert result["uid"] == "new123"

    @pytest.mark.asyncio
    async def test_list_datasources(self, grafana_client):
        """Test listing datasources"""
        with patch.object(grafana_client, "_request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = [
                {"uid": "ds1", "name": "Prometheus", "type": "prometheus"},
                {"uid": "ds2", "name": "MySQL", "type": "mysql"},
            ]

            result = await grafana_client.list_datasources()

            mock_request.assert_called_once_with("GET", "datasources")
            assert len(result) == 2
            assert result[0]["name"] == "Prometheus"

    @pytest.mark.asyncio
    async def test_create_folder(self, grafana_client):
        """Test creating a folder"""
        with patch.object(grafana_client, "_request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = {
                "id": 1,
                "uid": "folder123",
                "title": "Test Folder",
            }

            result = await grafana_client.create_folder("Test Folder", uid="folder123")

            mock_request.assert_called_once_with(
                "POST", "folders", json={"title": "Test Folder", "uid": "folder123"}
            )
            assert result["title"] == "Test Folder"

    @pytest.mark.asyncio
    async def test_create_annotation(self, grafana_client):
        """Test creating an annotation"""
        with patch.object(grafana_client, "_request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = {
                "id": 1,
                "message": "Annotation created",
            }

            result = await grafana_client.create_annotation(
                text="Deployment", tags=["deploy", "prod"], time=1234567890000
            )

            expected_data = {
                "text": "Deployment",
                "tags": ["deploy", "prod"],
                "time": 1234567890000,
            }
            mock_request.assert_called_once_with("POST", "annotations", json=expected_data)
            assert result["id"] == 1


class TestGrafanaMCPServer:
    """Tests for GrafanaMCPServer"""

    @pytest.fixture
    def mcp_server(self):
        """Create a test MCP server"""
        return GrafanaMCPServer()

    @pytest.mark.asyncio
    async def test_execute_tool_list_dashboards(self, mcp_server):
        """Test executing list_dashboards tool"""
        mock_client = AsyncMock()
        mock_client.list_dashboards.return_value = [
            {"uid": "abc123", "title": "Test Dashboard"}
        ]
        mcp_server.grafana_client = mock_client

        result = await mcp_server._execute_tool("grafana_list_dashboards", {})

        mock_client.list_dashboards.assert_called_once_with("")
        assert len(result) == 1
        assert result[0]["title"] == "Test Dashboard"

    @pytest.mark.asyncio
    async def test_execute_tool_health_check(self, mcp_server):
        """Test executing health_check tool"""
        mock_client = AsyncMock()
        mock_client.health_check.return_value = {"database": "ok"}
        mcp_server.grafana_client = mock_client

        result = await mcp_server._execute_tool("grafana_health_check", {})

        mock_client.health_check.assert_called_once()
        assert result["database"] == "ok"

    @pytest.mark.asyncio
    async def test_execute_tool_create_folder(self, mcp_server):
        """Test executing create_folder tool"""
        mock_client = AsyncMock()
        mock_client.create_folder.return_value = {"uid": "folder123", "title": "New Folder"}
        mcp_server.grafana_client = mock_client

        result = await mcp_server._execute_tool(
            "grafana_create_folder", {"title": "New Folder", "uid": "folder123"}
        )

        mock_client.create_folder.assert_called_once_with("New Folder", "folder123")
        assert result["title"] == "New Folder"

    @pytest.mark.asyncio
    async def test_execute_tool_unknown(self, mcp_server):
        """Test executing unknown tool raises error"""
        mock_client = AsyncMock()
        mcp_server.grafana_client = mock_client

        with pytest.raises(ValueError, match="Unknown tool"):
            await mcp_server._execute_tool("unknown_tool", {})


def test_grafana_config_with_api_key():
    """Test GrafanaConfig with API key"""
    config = GrafanaConfig(base_url="http://localhost:3000", api_key="test-key")

    assert config.base_url == "http://localhost:3000"
    assert config.api_key == "test-key"
    assert config.username is None
    assert config.password is None


def test_grafana_config_with_basic_auth():
    """Test GrafanaConfig with basic auth"""
    config = GrafanaConfig(
        base_url="http://localhost:3000", username="admin", password="admin"
    )

    assert config.base_url == "http://localhost:3000"
    assert config.username == "admin"
    assert config.password == "admin"
    assert config.api_key is None
