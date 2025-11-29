"""Tests for SP3 - Needs Schema."""
import pytest
from llmhub.generator.sp3_needs_schema import (
    RoleNeed,
    parse_role_needs,
    NeedsSchemaError,
)


def test_minimal_role_need():
    """Test creating minimal RoleNeed."""
    need = RoleNeed(id="test")
    
    assert need.id == "test"
    assert need.task_kind == "general"
    assert need.importance == "medium"
    assert need.quality_bias == 0.5
    assert need.cost_bias == 0.5


def test_full_role_need():
    """Test creating RoleNeed with all fields."""
    need = RoleNeed(
        id="analyst",
        task_kind="reasoning",
        importance="high",
        quality_bias=0.8,
        cost_bias=0.3,
        latency_sensitivity=0.6,
        reasoning_required=True,
        tools_required=False,
        structured_output_required=True,
        context_min=100000,
        modalities_in=["text"],
        modalities_out=["text"],
        provider_allowlist=["openai", "anthropic"],
        provider_blocklist=["google"],
        model_denylist=["gpt-3.5"],
        reasoning_tier_pref=1,
        creative_tier_pref=3,
        notes="High quality reasoning required"
    )
    
    assert need.id == "analyst"
    assert need.task_kind == "reasoning"
    assert need.importance == "high"
    assert need.quality_bias == 0.8
    assert need.reasoning_required is True
    assert need.context_min == 100000
    assert need.reasoning_tier_pref == 1


def test_parse_role_needs_valid():
    """Test parsing list of role needs."""
    raw = [
        {
            "id": "analyst",
            "task_kind": "reasoning",
            "importance": "high"
        },
        {
            "id": "writer",
            "task_kind": "creative",
            "importance": "medium"
        }
    ]
    
    needs = parse_role_needs(raw)
    
    assert len(needs) == 2
    assert needs[0].id == "analyst"
    assert needs[1].id == "writer"


def test_parse_role_needs_invalid():
    """Test parsing invalid role needs."""
    raw = [
        {
            # Missing "id"
            "task_kind": "reasoning"
        }
    ]
    
    with pytest.raises(NeedsSchemaError):
        parse_role_needs(raw)


def test_bias_validation():
    """Test that biases are clamped to [0, 1]."""
    need = RoleNeed(
        id="test",
        quality_bias=0.9,  # Valid
        cost_bias=0.1      # Valid
    )
    
    assert 0.0 <= need.quality_bias <= 1.0
    assert 0.0 <= need.cost_bias <= 1.0


def test_tier_pref_validation():
    """Test tier preference validation."""
    need = RoleNeed(
        id="test",
        reasoning_tier_pref=1,  # Valid
        creative_tier_pref=5    # Valid
    )
    
    assert 1 <= need.reasoning_tier_pref <= 5
    assert 1 <= need.creative_tier_pref <= 5
