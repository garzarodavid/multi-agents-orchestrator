import os
import unittest

from llm_client import PROVIDER_MODELS, create_llm_client, resolve_model, load_model_map


class ResolveModelTests(unittest.TestCase):
    def setUp(self) -> None:
        for key in list(os.environ.keys()):
            if key.startswith("LLM_MODEL_") or key in ("OPENAI_MODEL", "LLM_PROVIDER", "LLM_STRATEGY"):
                os.environ.pop(key, None)

    def test_strategy_defaults_to_balance(self) -> None:
        model = resolve_model("openai", requested=None, strategy="balance", default_model=None)
        self.assertEqual(model, PROVIDER_MODELS["openai"]["balance"])

    def test_env_override_takes_precedence(self) -> None:
        os.environ["LLM_MODEL_OPENAI"] = "custom-model"
        model = resolve_model("openai", requested=None, strategy="quality", default_model=None)
        self.assertEqual(model, "custom-model")

    def test_legacy_openai_model_used(self) -> None:
        os.environ["OPENAI_MODEL"] = "legacy-model"
        model = resolve_model("openai", requested=None, strategy="cost", default_model=None)
        self.assertEqual(model, "legacy-model")

    def test_requested_model_wins(self) -> None:
        model = resolve_model("gemini", requested="gemini-custom", strategy="balance", default_model=None)
        self.assertEqual(model, "gemini-custom")

    def test_falls_back_to_default_model_if_unknown_provider(self) -> None:
        model = resolve_model("unknown", requested=None, strategy="balance", default_model="fallback")
        self.assertEqual(model, "fallback")

    def test_resolves_from_map_per_agent(self) -> None:
        sample_map = {
            "openai": {
                "balance": {
                    "default": "gpt-4.1-mini",
                    "agent_dba": "custom-dba",
                }
            }
        }
        model = resolve_model("openai", requested=None, strategy="balance", default_model=None, model_map=sample_map, agent="dba")
        self.assertEqual(model, "custom-dba")


class FactoryTests(unittest.TestCase):
    def tearDown(self) -> None:
        for key in list(os.environ.keys()):
            if key.startswith("LLM_MODEL_") or key in ("OPENAI_MODEL", "LLM_PROVIDER", "LLM_STRATEGY"):
                os.environ.pop(key, None)

    def test_factory_raises_for_unknown_provider(self) -> None:
        os.environ["LLM_PROVIDER"] = "unknown-provider"
        with self.assertRaises(RuntimeError):
            create_llm_client()

    def test_load_model_map_returns_empty_when_missing(self) -> None:
        self.assertEqual(load_model_map("nao-existe.toml"), {})


if __name__ == "__main__":
    unittest.main()
