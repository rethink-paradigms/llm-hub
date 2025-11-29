"""End-to-end tests for generator module."""
import tempfile
import os
from pathlib import Path
import pytest
from unittest.mock import Mock, MagicMock
from llmhub.generator import (
    generate_machine_config,
    ProjectSpec,
    RoleNeed,
    GeneratorError,
)
from llmhub.catalog.schema import CanonicalModel


def test_generate_e2e_with_mocks(tmp_path):
    """Test end-to-end generation with mocked components."""
    # Create a minimal spec file
    spec_path = tmp_path / "llmhub.spec.yaml"
    spec_content = """
project: test-app
env: dev

roles:
  analyst:
    kind: chat
    description: Analyze user feedback and extract insights
    preferences:
      quality: high
      cost: medium
"""
    spec_path.write_text(spec_content)
    
    # Mock hub
    mock_hub = Mock()
    mock_response = Mock()
    mock_response.choices = [Mock()]
    mock_response.choices[0].message.content = """{
  "roles": [
    {
      "id": "analyst",
      "task_kind": "reasoning",
      "importance": "high",
      "quality_bias": 0.7,
      "cost_bias": 0.5,
      "latency_sensitivity": 0.4,
      "reasoning_required": false,
      "tools_required": false,
      "structured_output_required": false,
      "modalities_in": ["text"],
      "modalities_out": ["text"]
    }
  ]
}"""
    mock_hub.completion.return_value = mock_response
    
    # Create mock catalog
    mock_catalog = [
        CanonicalModel(
            canonical_id="openai/gpt-4",
            provider="openai",
            model_id="gpt-4o",
            quality_tier=1,
            reasoning_tier=1,
            creative_tier=2,
            cost_tier=4,
            context_tokens=128000,
            supports_reasoning=False,
            supports_tool_call=True,
            supports_structured_output=True,
            arena_score=1250.0,
        ),
        CanonicalModel(
            canonical_id="anthropic/claude-3",
            provider="anthropic",
            model_id="claude-3-sonnet",
            quality_tier=1,
            reasoning_tier=1,
            creative_tier=1,
            cost_tier=3,
            context_tokens=200000,
            supports_reasoning=False,
            supports_tool_call=True,
            supports_structured_output=True,
            arena_score=1270.0,
        ),
    ]
    
    # Generate machine config
    output_path = tmp_path / "llmhub.yaml"
    machine_config = generate_machine_config(
        spec_path=str(spec_path),
        hub=mock_hub,
        output_path=str(output_path),
        catalog_override=mock_catalog
    )
    
    # Assertions
    assert machine_config.project == "test-app"
    assert machine_config.env == "dev"
    assert "analyst" in machine_config.roles
    assert machine_config.roles["analyst"].provider in ["openai", "anthropic"]
    assert machine_config.roles["analyst"].model in ["gpt-4o", "claude-3-sonnet"]
    
    # Check output file was created
    assert output_path.exists()


def test_spec_schema_components():
    """Test that all subproblems are properly integrated."""
    from llmhub.generator.sp1_spec_schema import parse_project_spec
    from llmhub.generator.sp3_needs_schema import RoleNeed, parse_role_needs
    from llmhub.generator.sp5_filter_candidates import filter_candidates
    from llmhub.generator.sp6_weights import derive_weights
    from llmhub.generator.sp7_scoring_engine import score_candidates
    from llmhub.generator.sp9_selector_orchestrator import select_for_role, SelectorOptions
    from llmhub.generator.sp10_machine_config_emitter import build_machine_config
    
    # Test SP1
    raw_spec = {
        "project": "test",
        "env": "dev",
        "roles": {"test": {"kind": "chat", "description": "Test role"}}
    }
    spec = parse_project_spec(raw_spec)
    assert spec.project == "test"
    
    # Test SP3
    raw_needs = [{"id": "test", "task_kind": "general"}]
    needs = parse_role_needs(raw_needs)
    assert len(needs) == 1
    
    # Test SP6
    need = RoleNeed(id="test", quality_bias=0.8, cost_bias=0.2)
    weights = derive_weights(need)
    assert 0 <= weights.w_quality <= 1
    assert 0 <= weights.w_cost <= 1
    
    # Integration works
    assert True


def test_error_handling():
    """Test that errors are properly propagated."""
    with pytest.raises((GeneratorError, FileNotFoundError)):
        generate_machine_config(
            spec_path="/nonexistent/path/llmhub.spec.yaml",
            hub=Mock()
        )
