import os
import tempfile
import unittest

from mcp_config import load_mcp_servers


class McpConfigTests(unittest.TestCase):
    def test_returns_empty_when_no_env_or_path(self) -> None:
        os.environ.pop("MCP_SERVERS_FILE", None)
        servers, warning = load_mcp_servers()
        self.assertEqual(servers, {})
        self.assertIsNone(warning)

    def test_loads_servers_from_toml(self) -> None:
        content = b"[servers.postgres]\ncommand = \"psql\"\n"
        with tempfile.NamedTemporaryFile(suffix=".toml", delete=False) as tmp:
            tmp.write(content)
            tmp_path = tmp.name

        os.environ["MCP_SERVERS_FILE"] = tmp_path
        try:
            servers, warning = load_mcp_servers()
        finally:
            os.environ.pop("MCP_SERVERS_FILE", None)
            os.remove(tmp_path)

        self.assertIsNone(warning)
        self.assertIn("postgres", servers)
        self.assertEqual(servers["postgres"].get("command"), "psql")

    def test_missing_file_returns_warning(self) -> None:
        os.environ["MCP_SERVERS_FILE"] = "C:/tmp/nao-existe.toml"
        try:
            servers, warning = load_mcp_servers()
        finally:
            os.environ.pop("MCP_SERVERS_FILE", None)
        self.assertEqual(servers, {})
        self.assertIsNotNone(warning)


if __name__ == "__main__":
    unittest.main()
