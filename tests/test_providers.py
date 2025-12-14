import os
import sys
import types
import unittest

from providers.factory import create_provider_adapter


class ProvidersFactoryTests(unittest.TestCase):
    def tearDown(self) -> None:
        for key in ("LLM_PROVIDER", "LLM_STRATEGY", "LLM_MODEL_MAP_FILE"):
            os.environ.pop(key, None)
        for key in ("OPENAI_API_KEY", "GOOGLE_API_KEY", "ANTHROPIC_API_KEY"):
            os.environ.pop(key, None)
        for mod in ("google.generativeai", "anthropic"):
            if mod in sys.modules:
                sys.modules.pop(mod)

    def test_factory_returns_openai_adapter(self) -> None:
        os.environ["LLM_PROVIDER"] = "openai"
        os.environ["OPENAI_API_KEY"] = "test-key"
        adapter = create_provider_adapter(default_model="gpt-4.1-mini")
        self.assertEqual(getattr(adapter, "name", ""), "openai")

    def test_factory_errors_without_gemini_sdk(self) -> None:
        os.environ["LLM_PROVIDER"] = "gemini"
        with self.assertRaises(RuntimeError):
            create_provider_adapter(default_model="gemini-1.5-flash")

    def test_factory_errors_without_claude_sdk(self) -> None:
        os.environ["LLM_PROVIDER"] = "claude"
        with self.assertRaises(RuntimeError):
            create_provider_adapter(default_model="claude-3-haiku-20240307")

    def test_factory_accepts_mocked_gemini_sdk(self) -> None:
        os.environ["LLM_PROVIDER"] = "gemini"
        os.environ["GOOGLE_API_KEY"] = "test-key"
        fake = types.SimpleNamespace(configure=lambda api_key: None, GenerativeModel=lambda model_name: types.SimpleNamespace(generate_content=lambda msgs: "ok"))
        sys.modules["google"] = types.SimpleNamespace(generativeai=fake)
        sys.modules["google.generativeai"] = fake
        adapter = create_provider_adapter(default_model="gemini-1.5-flash")
        self.assertEqual(getattr(adapter, "name", ""), "gemini")

    def test_factory_accepts_mocked_claude_sdk(self) -> None:
        os.environ["LLM_PROVIDER"] = "claude"
        os.environ["ANTHROPIC_API_KEY"] = "test-key"
        class FakeAnthropicClient:
            def __init__(self, api_key=None): pass
            class messages:
                @staticmethod
                def create(model=None, system=None, messages=None, max_tokens=None):
                    return types.SimpleNamespace(content=[types.SimpleNamespace(text="ok")], usage={})
        sys.modules["anthropic"] = types.SimpleNamespace(Anthropic=FakeAnthropicClient)
        adapter = create_provider_adapter(default_model="claude-3-haiku-20240307")
        self.assertEqual(getattr(adapter, "name", ""), "claude")


if __name__ == "__main__":
    unittest.main()
