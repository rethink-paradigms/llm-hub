import pytest
from llmhub_runtime.resolver import resolve_role
from llmhub_runtime.models import RuntimeConfig, RoleConfig, ProviderConfig, LLMMode, RoleDefaultsConfig
from llmhub_runtime.errors import UnknownRoleError, UnknownProviderError

@pytest.fixture
def mock_config():
    return RuntimeConfig(
        project="test",
        env="dev",
        providers={
            "openai": ProviderConfig(env_key="OPENAI_API_KEY"),
            "anthropic": ProviderConfig(env_key="ANTHROPIC_API_KEY")
        },
        roles={
            "test_role": RoleConfig(
                provider="openai",
                model="gpt-4",
                mode=LLMMode.chat,
                params={"temperature": 0.5}
            ),
             "bad_provider_role": RoleConfig(
                provider="missing_provider",
                model="gpt-4",
                mode=LLMMode.chat,
                params={}
            )
        },
        defaults=RoleDefaultsConfig(
            provider="openai",
            model="gpt-3.5-turbo",
            mode=LLMMode.chat,
            params={"max_tokens": 100}
        )
    )

def test_resolve_role_success(mock_config):
    resolved = resolve_role(mock_config, "test_role")
    assert resolved.role == "test_role"
    assert resolved.provider == "openai"
    assert resolved.model == "gpt-4"
    assert resolved.params["temperature"] == 0.5

def test_resolve_role_override(mock_config):
    resolved = resolve_role(mock_config, "test_role", params_override={"temperature": 0.9})
    assert resolved.params["temperature"] == 0.9

def test_resolve_role_defaults(mock_config):
    resolved = resolve_role(mock_config, "non_existent_role")
    assert resolved.role == "non_existent_role"
    assert resolved.provider == "openai" # From defaults
    assert resolved.model == "gpt-3.5-turbo"

def test_resolve_role_unknown_no_defaults():
    config = RuntimeConfig(
        project="test", env="dev", providers={}, roles={}, defaults=None
    )
    with pytest.raises(UnknownRoleError):
        resolve_role(config, "missing_role")

def test_resolve_role_unknown_provider(mock_config):
    with pytest.raises(UnknownProviderError):
        resolve_role(mock_config, "bad_provider_role")
