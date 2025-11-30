"""Tests for SP1 - Spec Schema."""
import pytest
from llmhub_cli.generator.spec import (
    ProjectSpec,
    RoleSpec,
    Preferences,
    parse_project_spec,
    SpecSchemaError,
)


def test_parse_minimal_spec():
    """Test parsing minimal valid spec."""
    raw = {
        "project": "test-app",
        "env": "dev",
        "roles": {
            "analyst": {
                "kind": "chat",
                "description": "Analyze data"
            }
        }
    }
    
    spec = parse_project_spec(raw)
    
    assert spec.project == "test-app"
    assert spec.env == "dev"
    assert "analyst" in spec.roles
    assert spec.roles["analyst"].kind == "chat"
    assert spec.roles["analyst"].description == "Analyze data"


def test_parse_spec_with_preferences():
    """Test parsing spec with preferences."""
    raw = {
        "project": "test-app",
        "env": "production",
        "roles": {
            "writer": {
                "kind": "chat",
                "description": "Write content",
                "preferences": {
                    "quality": "high",
                    "cost": "medium",
                    "providers": ["openai", "anthropic"]
                }
            }
        }
    }
    
    spec = parse_project_spec(raw)
    
    assert spec.roles["writer"].preferences.quality == "high"
    assert spec.roles["writer"].preferences.cost == "medium"
    assert spec.roles["writer"].preferences.providers == ["openai", "anthropic"]


def test_parse_spec_with_defaults():
    """Test parsing spec with default preferences."""
    raw = {
        "project": "test-app",
        "env": "dev",
        "defaults": {
            "providers": ["openai"],
            "quality": "medium"
        },
        "roles": {
            "analyst": {
                "kind": "chat",
                "description": "Analyze data"
            }
        }
    }
    
    spec = parse_project_spec(raw)
    
    assert spec.defaults is not None
    assert spec.defaults.providers == ["openai"]
    assert spec.defaults.quality == "medium"


def test_parse_spec_missing_required_field():
    """Test parsing spec with missing required field."""
    raw = {
        "project": "test-app",
        # Missing "env"
        "roles": {
            "analyst": {
                "kind": "chat",
                "description": "Analyze data"
            }
        }
    }
    
    with pytest.raises(SpecSchemaError):
        parse_project_spec(raw)


def test_parse_spec_extra_fields_allowed():
    """Test that extra fields are allowed (forward compatibility)."""
    raw = {
        "project": "test-app",
        "env": "dev",
        "extra_field": "ignored",
        "roles": {
            "analyst": {
                "kind": "chat",
                "description": "Analyze data",
                "future_field": "also ignored"
            }
        }
    }
    
    # Should not raise
    spec = parse_project_spec(raw)
    assert spec.project == "test-app"


def test_force_provider_and_model():
    """Test force_provider and force_model fields."""
    raw = {
        "project": "test-app",
        "env": "dev",
        "roles": {
            "analyst": {
                "kind": "chat",
                "description": "Analyze data",
                "force_provider": "openai",
                "force_model": "gpt-4"
            }
        }
    }
    
    spec = parse_project_spec(raw)
    
    assert spec.roles["analyst"].force_provider == "openai"
    assert spec.roles["analyst"].force_model == "gpt-4"
