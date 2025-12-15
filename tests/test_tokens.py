import os
import unittest
from unittest import mock

from multiagents.tokens import get_token


class TokenTests(unittest.TestCase):
    def tearDown(self) -> None:
        for key in ("LLM_TOKEN_OPENAI", "OPENAI_API_KEY", "GOOGLE_API_KEY", "ANTHROPIC_API_KEY", "GITHUB_TOKEN", "AZURE_ACCESS_TOKEN", "PGPASSWORD"):
            os.environ.pop(key, None)

    def test_env_override_precedence(self) -> None:
        os.environ["LLM_TOKEN_OPENAI"] = "override"
        os.environ["OPENAI_API_KEY"] = "api"
        self.assertEqual(get_token("openai"), "override")

    def test_openai_env(self) -> None:
        os.environ["OPENAI_API_KEY"] = "api"
        self.assertEqual(get_token("openai"), "api")

    def test_github_env(self) -> None:
        os.environ["GITHUB_TOKEN"] = "gh"
        self.assertEqual(get_token("github"), "gh")

    def test_postgres_env(self) -> None:
        os.environ["PGPASSWORD"] = "pwd"
        self.assertEqual(get_token("postgres"), "pwd")

    def test_azure_cli_fallback(self) -> None:
        with mock.patch("subprocess.check_output") as chk:
            chk.return_value = '{"accessToken":"tok"}'
            os.environ.pop("AZURE_ACCESS_TOKEN", None)
            self.assertEqual(get_token("azure"), "tok")

    def test_github_cli_fallback(self) -> None:
        with mock.patch("subprocess.check_output") as chk:
            chk.return_value = "ghtoken\n"
            os.environ.pop("GITHUB_TOKEN", None)
            self.assertEqual(get_token("github"), "ghtoken")


if __name__ == "__main__":
    unittest.main()
