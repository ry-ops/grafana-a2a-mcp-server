# Contributing to Grafana MCP Server

Thank you for your interest in contributing to the Grafana MCP Server! This document provides guidelines for contributing to the project.

## Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/YOUR-USERNAME/grafana-mcp-server.git
   cd grafana-mcp-server
   ```
3. **Install UV** (if not already installed):
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```
4. **Set up the development environment**:
   ```bash
   ./setup.sh
   uv pip install -e ".[dev]"
   ```

## Development Workflow

### 1. Create a Branch

Create a new branch for your feature or bugfix:

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/your-bugfix-name
```

### 2. Make Your Changes

- Write clear, concise commit messages
- Follow the existing code style
- Add tests for new features
- Update documentation as needed

### 3. Run Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=grafana_mcp

# Run specific test file
pytest tests/test_server.py
```

### 4. Format Code

```bash
# Format with Black
black src/ tests/

# Lint with Ruff
ruff check src/ tests/

# Fix auto-fixable issues
ruff check --fix src/ tests/
```

### 5. Commit Your Changes

```bash
git add .
git commit -m "feat: add new dashboard template feature"
```

#### Commit Message Format

Follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation changes
- `test:` - Adding or updating tests
- `refactor:` - Code refactoring
- `perf:` - Performance improvements
- `chore:` - Maintenance tasks

### 6. Push and Create Pull Request

```bash
git push origin feature/your-feature-name
```

Then create a pull request on GitHub.

## Code Style Guidelines

### Python Style

- Follow [PEP 8](https://pep8.org/)
- Use type hints for function signatures
- Maximum line length: 100 characters
- Use `black` for formatting
- Use `ruff` for linting

### Example

```python
async def create_dashboard(
    self,
    title: str,
    tags: list[str],
    folder_uid: Optional[str] = None
) -> dict[str, Any]:
    """
    Create a new Grafana dashboard.
    
    Args:
        title: Dashboard title
        tags: List of tags
        folder_uid: Optional folder UID
        
    Returns:
        Created dashboard data
        
    Raises:
        HTTPStatusError: If API request fails
    """
    dashboard_data = {
        "dashboard": {
            "title": title,
            "tags": tags,
        },
        "folderUid": folder_uid,
    }
    return await self._request("POST", "dashboards/db", json=dashboard_data)
```

### Documentation

- Use Google-style docstrings
- Document all public functions and classes
- Include examples where helpful
- Update README.md for user-facing changes

## Testing Guidelines

### Writing Tests

- Use `pytest` for testing
- Use `pytest-asyncio` for async tests
- Mock external API calls
- Aim for >80% code coverage

### Test Structure

```python
class TestGrafanaClient:
    """Tests for GrafanaClient"""
    
    @pytest.fixture
    def client(self):
        """Create test client"""
        config = GrafanaConfig(
            base_url="http://localhost:3000",
            api_key="test-key"
        )
        return GrafanaClient(config)
    
    @pytest.mark.asyncio
    async def test_list_dashboards(self, client):
        """Test listing dashboards"""
        with patch.object(client, '_request', new_callable=AsyncMock) as mock:
            mock.return_value = [{"uid": "test", "title": "Test"}]
            
            result = await client.list_dashboards()
            
            assert len(result) == 1
            assert result[0]["title"] == "Test"
```

## Adding New Features

### Adding a New Tool

1. **Add API method to GrafanaClient**:
   ```python
   async def get_teams(self) -> list[dict[str, Any]]:
       """List all teams"""
       return await self._request("GET", "teams")
   ```

2. **Register tool in list_tools handler**:
   ```python
   Tool(
       name="grafana_list_teams",
       description="List all teams in Grafana",
       inputSchema={"type": "object", "properties": {}}
   )
   ```

3. **Handle tool execution**:
   ```python
   elif name == "grafana_list_teams":
       return await self.grafana_client.get_teams()
   ```

4. **Add tests**:
   ```python
   @pytest.mark.asyncio
   async def test_list_teams(self, grafana_client):
       """Test listing teams"""
       # ... test implementation
   ```

5. **Update documentation**:
   - Add to README.md
   - Update CHANGELOG.md

## Pull Request Process

1. **Update Documentation**: Ensure README and other docs are updated
2. **Add Tests**: New features must include tests
3. **Update CHANGELOG**: Add entry to CHANGELOG.md
4. **Code Review**: Address all review comments
5. **CI Checks**: Ensure all CI checks pass

### Pull Request Checklist

- [ ] Code follows project style guidelines
- [ ] Tests added and passing
- [ ] Documentation updated
- [ ] CHANGELOG.md updated
- [ ] Commit messages follow convention
- [ ] No merge conflicts

## Bug Reports

When filing a bug report, please include:

1. **Description**: Clear description of the bug
2. **Steps to Reproduce**: Detailed steps to reproduce
3. **Expected Behavior**: What you expected to happen
4. **Actual Behavior**: What actually happened
5. **Environment**:
   - Python version
   - Grafana version
   - OS
6. **Logs**: Relevant error messages or logs

## Feature Requests

When requesting a feature:

1. **Use Case**: Describe the use case
2. **Proposed Solution**: Suggest implementation if possible
3. **Alternatives**: Consider alternative solutions
4. **Additional Context**: Any other relevant information

## Code of Conduct

### Our Pledge

We pledge to make participation in our project a harassment-free experience for everyone, regardless of age, body size, disability, ethnicity, gender identity and expression, level of experience, nationality, personal appearance, race, religion, or sexual identity and orientation.

### Our Standards

- Be respectful and inclusive
- Accept constructive criticism gracefully
- Focus on what's best for the community
- Show empathy towards others

### Enforcement

Project maintainers have the right to remove, edit, or reject comments, commits, code, issues, and other contributions that don't align with this Code of Conduct.

## Questions?

Feel free to:
- Open an issue for discussion
- Ask questions in pull requests
- Reach out to maintainers

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to Grafana MCP Server! 🎉
