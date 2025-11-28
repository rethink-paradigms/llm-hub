import pytest
from pathlib import Path
from llmhub.spec_models import (
    SpecConfig, SpecProviderConfig, RoleSpec, RoleKind,
    Preferences, PreferenceLevel, SpecDefaults,
    load_spec, save_spec, SpecError
)


def test_spec_config_creation():
    """Test creating a minimal SpecConfig."""
    spec = SpecConfig(
        project="test",
        env="dev",
        providers={"openai": SpecProviderConfig(enabled=True, env_key="OPENAI_API_KEY")},
        roles={
            "llm.test": RoleSpec(
                kind=RoleKind.chat,
                description="Test role"
            )
        }
    )
    
    assert spec.project == "test"
    assert spec.env == "dev"
    assert "openai" in spec.providers
    assert "llm.test" in spec.roles


def test_spec_with_preferences():
    """Test spec with role preferences."""
    prefs = Preferences(
        cost=PreferenceLevel.low,
        latency=PreferenceLevel.medium,
        quality=PreferenceLevel.high,
        providers=["openai", "anthropic"]
    )
    
    role = RoleSpec(
        kind=RoleKind.chat,
        description="Test",
        preferences=prefs
    )
    
    assert role.preferences.cost == PreferenceLevel.low
    assert role.preferences.quality == PreferenceLevel.high
    assert "openai" in role.preferences.providers


def test_save_and_load_spec(tmp_path):
    """Test saving and loading spec."""
    spec_path = tmp_path / "test.spec.yaml"
    
    spec = SpecConfig(
        project="test-project",
        env="dev",
        providers={
            "openai": SpecProviderConfig(enabled=True, env_key="OPENAI_API_KEY"),
            "anthropic": SpecProviderConfig(enabled=False, env_key="ANTHROPIC_API_KEY")
        },
        roles={
            "llm.inference": RoleSpec(
                kind=RoleKind.chat,
                description="Main inference role",
                preferences=Preferences(
                    cost=PreferenceLevel.medium,
                    quality=PreferenceLevel.high,
                    providers=["openai"]
                )
            )
        },
        defaults=SpecDefaults(providers=["openai"])
    )
    
    # Save
    save_spec(spec_path, spec)
    assert spec_path.exists()
    
    # Load
    loaded = load_spec(spec_path)
    assert loaded.project == "test-project"
    assert loaded.env == "dev"
    assert "openai" in loaded.providers
    assert "llm.inference" in loaded.roles
    assert loaded.roles["llm.inference"].kind == RoleKind.chat
    assert loaded.defaults.providers == ["openai"]


def test_load_spec_missing_file(tmp_path):
    """Test loading non-existent spec file."""
    spec_path = tmp_path / "missing.yaml"
    
    with pytest.raises(SpecError, match="not found"):
        load_spec(spec_path)


def test_spec_role_kinds():
    """Test all role kinds."""
    for kind in [RoleKind.chat, RoleKind.embedding, RoleKind.image, 
                 RoleKind.audio, RoleKind.tool, RoleKind.other]:
        role = RoleSpec(kind=kind, description="Test")
        assert role.kind == kind


def test_spec_with_mode_params():
    """Test role with mode_params."""
    role = RoleSpec(
        kind=RoleKind.chat,
        description="Test",
        mode_params={"temperature": 0.7, "max_tokens": 1000}
    )
    
    assert role.mode_params["temperature"] == 0.7
    assert role.mode_params["max_tokens"] == 1000


def test_spec_with_force_model():
    """Test role with forced provider and model."""
    role = RoleSpec(
        kind=RoleKind.chat,
        description="Test",
        force_provider="openai",
        force_model="gpt-4"
    )
    
    assert role.force_provider == "openai"
    assert role.force_model == "gpt-4"
