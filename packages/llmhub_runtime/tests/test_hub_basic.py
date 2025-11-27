import os
import pytest
from unittest.mock import MagicMock, patch
from llmhub_runtime.hub import LLMHub
from llmhub_runtime.models import RuntimeConfig, ProviderConfig, RoleConfig, LLMMode
from llmhub_runtime.errors import EnvVarMissingError

FIXTURE_PATH = "tests/fixtures/llmhub.yaml"

@pytest.fixture
def mock_any_llm():
    with patch("llmhub_runtime.hub.any_llm") as mock:
        yield mock

def test_llmhub_init_file():
    hub = LLMHub(config_path=FIXTURE_PATH)
    assert hub.config.project == "memory"

def test_llmhub_init_object():
    config = RuntimeConfig(
        project="test", env="dev", providers={}, roles={}, defaults=None
    )
    hub = LLMHub(config_obj=config)
    assert hub.config.project == "test"

def test_llmhub_env_validation():
    config = RuntimeConfig(
        project="test", env="dev",
        providers={"openai": ProviderConfig(env_key="MISSING_KEY")},
        roles={}, defaults=None
    )
    # Should raise error if key is missing and strict_env is True
    with pytest.raises(EnvVarMissingError):
        LLMHub(config_obj=config, strict_env=True)

    # Should not raise if strict_env is False
    LLMHub(config_obj=config, strict_env=False)

def test_completion_call(mock_any_llm):
    mock_any_llm.completion.return_value = "response"

    hub = LLMHub(config_path=FIXTURE_PATH)
    response = hub.completion("llm.inference", messages=[{"role": "user", "content": "hi"}])

    assert response == "response"
    mock_any_llm.completion.assert_called_once()
    call_args = mock_any_llm.completion.call_args[1]
    assert call_args["provider"] == "openai"
    assert call_args["model"] == "gpt-4"
    assert "messages" in call_args

def test_embedding_call(mock_any_llm):
    mock_any_llm.embedding.return_value = "embedding_result"

    hub = LLMHub(config_path=FIXTURE_PATH)
    response = hub.embedding("llm.embedding", input="hello")

    assert response == "embedding_result"
    mock_any_llm.embedding.assert_called_once()
    call_args = mock_any_llm.embedding.call_args[1]
    assert call_args["provider"] == "openai"
    assert call_args["inputs"] == "hello"

def test_hooks(mock_any_llm):
    before_hook = MagicMock()
    after_hook = MagicMock()

    hub = LLMHub(
        config_path=FIXTURE_PATH,
        on_before_call=before_hook,
        on_after_call=after_hook
    )

    hub.completion("llm.inference", messages=[])

    before_hook.assert_called_once()
    after_hook.assert_called_once()
