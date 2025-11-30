"""Tests for SP5 - Filter Candidates."""
import pytest
from llmhub_cli.generator.needs import RoleNeed
from llmhub_cli.generator.selection import filter_candidates
from llmhub_cli.catalog.schema import CanonicalModel


def create_mock_model(
    canonical_id: str = "openai/gpt-4",
    provider: str = "openai",
    model_id: str = "gpt-4",
    supports_reasoning: bool = False,
    supports_tool_call: bool = False,
    supports_structured_output: bool = False,
    context_tokens: int = 8000,
    input_modalities: list = None,
    output_modalities: list = None
) -> CanonicalModel:
    """Create a mock CanonicalModel for testing."""
    return CanonicalModel(
        canonical_id=canonical_id,
        provider=provider,
        model_id=model_id,
        supports_reasoning=supports_reasoning,
        supports_tool_call=supports_tool_call,
        supports_structured_output=supports_structured_output,
        context_tokens=context_tokens,
        input_modalities=input_modalities or ["text"],
        output_modalities=output_modalities or ["text"],
        quality_tier=2,
        reasoning_tier=2,
        creative_tier=2,
        cost_tier=3
    )


def test_filter_no_constraints():
    """Test filtering with no constraints returns all models."""
    role = RoleNeed(id="test")
    models = [
        create_mock_model("openai/gpt-4", "openai", "gpt-4"),
        create_mock_model("anthropic/claude-3", "anthropic", "claude-3"),
    ]
    
    filtered = filter_candidates(role, models)
    
    assert len(filtered) == 2


def test_filter_provider_allowlist():
    """Test filtering by provider allowlist."""
    role = RoleNeed(
        id="test",
        provider_allowlist=["openai"]
    )
    models = [
        create_mock_model("openai/gpt-4", "openai", "gpt-4"),
        create_mock_model("anthropic/claude-3", "anthropic", "claude-3"),
        create_mock_model("openai/gpt-3.5", "openai", "gpt-3.5-turbo"),
    ]
    
    filtered = filter_candidates(role, models)
    
    assert len(filtered) == 2
    assert all(m.provider == "openai" for m in filtered)


def test_filter_provider_blocklist():
    """Test filtering by provider blocklist."""
    role = RoleNeed(
        id="test",
        provider_blocklist=["google"]
    )
    models = [
        create_mock_model("openai/gpt-4", "openai", "gpt-4"),
        create_mock_model("google/gemini", "google", "gemini-pro"),
        create_mock_model("anthropic/claude-3", "anthropic", "claude-3"),
    ]
    
    filtered = filter_candidates(role, models)
    
    assert len(filtered) == 2
    assert all(m.provider != "google" for m in filtered)


def test_filter_model_denylist():
    """Test filtering by model denylist."""
    role = RoleNeed(
        id="test",
        model_denylist=["gpt-3.5-turbo"]
    )
    models = [
        create_mock_model("openai/gpt-4", "openai", "gpt-4"),
        create_mock_model("openai/gpt-3.5", "openai", "gpt-3.5-turbo"),
    ]
    
    filtered = filter_candidates(role, models)
    
    assert len(filtered) == 1
    assert filtered[0].model_id == "gpt-4"


def test_filter_reasoning_required():
    """Test filtering by reasoning requirement."""
    role = RoleNeed(
        id="test",
        reasoning_required=True
    )
    models = [
        create_mock_model("openai/gpt-4", "openai", "gpt-4", supports_reasoning=True),
        create_mock_model("openai/gpt-3.5", "openai", "gpt-3.5-turbo", supports_reasoning=False),
    ]
    
    filtered = filter_candidates(role, models)
    
    assert len(filtered) == 1
    assert filtered[0].model_id == "gpt-4"


def test_filter_tools_required():
    """Test filtering by tools requirement."""
    role = RoleNeed(
        id="test",
        tools_required=True
    )
    models = [
        create_mock_model("openai/gpt-4", "openai", "gpt-4", supports_tool_call=True),
        create_mock_model("openai/gpt-3.5", "openai", "gpt-3.5-turbo", supports_tool_call=False),
    ]
    
    filtered = filter_candidates(role, models)
    
    assert len(filtered) == 1
    assert filtered[0].supports_tool_call is True


def test_filter_context_min():
    """Test filtering by minimum context requirement."""
    role = RoleNeed(
        id="test",
        context_min=10000
    )
    models = [
        create_mock_model("openai/gpt-4", "openai", "gpt-4", context_tokens=128000),
        create_mock_model("openai/gpt-3.5", "openai", "gpt-3.5-turbo", context_tokens=4000),
    ]
    
    filtered = filter_candidates(role, models)
    
    assert len(filtered) == 1
    assert filtered[0].context_tokens >= 10000


def test_filter_combined_constraints():
    """Test filtering with multiple constraints."""
    role = RoleNeed(
        id="test",
        provider_allowlist=["openai"],
        reasoning_required=True,
        context_min=50000
    )
    models = [
        create_mock_model("openai/gpt-4", "openai", "gpt-4", 
                         supports_reasoning=True, context_tokens=128000),
        create_mock_model("openai/gpt-3.5", "openai", "gpt-3.5-turbo",
                         supports_reasoning=True, context_tokens=4000),
        create_mock_model("anthropic/claude-3", "anthropic", "claude-3",
                         supports_reasoning=True, context_tokens=200000),
    ]
    
    filtered = filter_candidates(role, models)
    
    assert len(filtered) == 1
    assert filtered[0].model_id == "gpt-4"
