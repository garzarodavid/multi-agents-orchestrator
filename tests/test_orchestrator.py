import unittest

from orchestrator import Orchestrator


class ExtractTextTests(unittest.TestCase):
    def test_prefers_output_text_attribute(self) -> None:
        class FakeResponse:
            def __init__(self, text: str) -> None:
                self.output_text = text

        resp = FakeResponse("hello from attribute")
        self.assertEqual(Orchestrator._extract_text_from_response(resp), "hello from attribute")

    def test_parses_output_list_content_text(self) -> None:
        resp = {
            "output": [
                {
                    "content": [
                        {"text": "text inside nested structure"},
                    ]
                }
            ]
        }
        self.assertEqual(
            Orchestrator._extract_text_from_response(resp),
            "text inside nested structure",
        )

    def test_falls_back_to_str_on_unknown_shape(self) -> None:
        class OddResponse:
            def __str__(self) -> str:
                return "fallback to str"

        self.assertEqual(Orchestrator._extract_text_from_response(OddResponse()), "fallback to str")


class ChooseAgentTests(unittest.TestCase):
    def test_routes_to_dba_by_keyword(self) -> None:
        self.assertEqual(
            Orchestrator.choose_agent_for_message("Preciso rever um schema e indexes"),
            "dba",
        )

    def test_routes_to_devops_by_keyword(self) -> None:
        self.assertEqual(
            Orchestrator.choose_agent_for_message("Vamos revisar o pipeline de deploy e rollback"),
            "devops",
        )

    def test_routes_to_frontend_by_keyword(self) -> None:
        self.assertEqual(
            Orchestrator.choose_agent_for_message("Tenho uma duvida de frontend e UX"),
            "arquitetura_frontend",
        )

    def test_routes_to_dotnet_by_keyword(self) -> None:
        self.assertEqual(
            Orchestrator.choose_agent_for_message("Aplicacao desktop em C# e .NET 8"),
            "dotnet",
        )

    def test_routes_to_python_by_keyword(self) -> None:
        self.assertEqual(
            Orchestrator.choose_agent_for_message("Quero um script python para ETL"),
            "python",
        )

    def test_routes_to_default_architect(self) -> None:
        self.assertEqual(
            Orchestrator.choose_agent_for_message("Planejar portfolio de produto e roadmap"),
            "arquiteto",
        )


class MCPToolsTests(unittest.TestCase):
    class DummyLLM:
        def generate(self, messages, model=None, agent=None):
            return "ok"

    def test_marks_configured_and_missing_tools(self) -> None:
        orch = Orchestrator(llm_client=self.DummyLLM())
        orch._mcp_servers = {"postgres": {}, "azure": {}}
        line, missing = orch._build_tool_message(["mcp:postgres", "mcp:github"])
        self.assertIn("mcp:postgres", line)
        self.assertEqual(missing, ["mcp:github"])

    def test_no_tools_returns_empty(self) -> None:
        orch = Orchestrator(llm_client=self.DummyLLM())
        line, missing = orch._build_tool_message([])
        self.assertEqual(line, "")
        self.assertEqual(missing, [])


class MCPToolsTests(unittest.TestCase):
    def test_marks_configured_and_missing_tools(self) -> None:
        orch = Orchestrator(lambda: None)
        orch._mcp_servers = {"postgres": {}, "azure": {}}
        line, missing = orch._build_tool_message(["mcp:postgres", "mcp:github"])
        self.assertIn("mcp:postgres", line)
        self.assertEqual(missing, ["mcp:github"])

    def test_no_tools_returns_empty(self) -> None:
        orch = Orchestrator(lambda: None)
        line, missing = orch._build_tool_message([])
        self.assertEqual(line, "")
        self.assertEqual(missing, [])


if __name__ == "__main__":
    unittest.main()
