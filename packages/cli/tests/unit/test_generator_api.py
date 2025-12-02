"""
Unit tests for Generator API public functions.

Tests the public API exposed in llmhub_cli.generator module.
"""
import pytest
from pathlib import Path
from unittest.mock import Mock, patch
from llmhub_cli.generator import (
    generate_runtime_from_spec,
    GeneratorOptions,
    GenerationResult,
)
from llmhub_cli.spec import load_spec
from llmhub_runtime.models import RuntimeConfig


@pytest.fixture
def fixtures_dir():
    """Return path to test fixtures directory."""
    return Path(__file__).parent.parent / "fixtures"


@pytest.fixture
def valid_spec_path(fixtures_dir):
    """Return path to valid spec fixture."""
    return fixtures_dir / "valid_spec.yaml"


@pytest.fixture
def valid_spec(valid_spec_path):
    """Return loaded valid spec."""
    return load_spec(valid_spec_path)


class TestGenerateRuntimeFromSpec:
    """Tests for generate_runtime_from_spec function."""
    
    @pytest.mark.skip(reason="Requires catalog and LLM access - run in integration tests")
    def test_generate_runtime_success(self, valid_spec):
        """Test basic runtime generation from spec."""
        result = generate_runtime_from_spec(valid_spec)
        
        assert isinstance(result, GenerationResult)
        assert isinstance(result.runtime, RuntimeConfig)
        assert result.runtime.project == valid_spec.project
        assert result.runtime.env == valid_spec.env
        assert len(result.runtime.roles) > 0
    
    def test_generate_runtime_returns_generation_result(self, valid_spec):
        """Test that function returns GenerationResult type."""
        with patch('llmhub_cli.generator_hook.generate_runtime') as mock_gen:
            # Mock the return value
            mock_runtime = Mock(spec=RuntimeConfig)
            mock_runtime.project = "test"
            mock_runtime.env = "dev"
            mock_gen.return_value = GenerationResult(
                runtime=mock_runtime,
                explanations={}
            )
            
            result = generate_runtime_from_spec(valid_spec)
            
            assert isinstance(result, GenerationResult)
            assert hasattr(result, 'runtime')
            assert hasattr(result, 'explanations')
    
    def test_generate_runtime_with_default_options(self, valid_spec):
        """Test generation with default options (no options passed)."""
        with patch('llmhub_cli.generator_hook.generate_runtime') as mock_gen:
            mock_runtime = Mock(spec=RuntimeConfig)
            mock_gen.return_value = GenerationResult(
                runtime=mock_runtime,
                explanations={}
            )
            
            result = generate_runtime_from_spec(valid_spec)
            
            # Should call with None options
            mock_gen.assert_called_once_with(valid_spec, None)
    
    def test_generate_runtime_with_custom_options(self, valid_spec):
        """Test generation with custom options."""
        with patch('llmhub_cli.generator_hook.generate_runtime') as mock_gen:
            mock_runtime = Mock(spec=RuntimeConfig)
            mock_gen.return_value = GenerationResult(
                runtime=mock_runtime,
                explanations={}
            )
            
            options = GeneratorOptions(no_llm=True, explain=False)
            result = generate_runtime_from_spec(valid_spec, options)
            
            # Should pass options through
            mock_gen.assert_called_once_with(valid_spec, options)
    
    @pytest.mark.skip(reason="Requires catalog access - run in integration tests")
    def test_generate_runtime_with_explanations(self, valid_spec):
        """Test generation with explanations enabled."""
        options = GeneratorOptions(explain=True)
        result = generate_runtime_from_spec(valid_spec, options)
        
        assert isinstance(result.explanations, dict)
        # Should have explanations for each role
        assert len(result.explanations) > 0
    
    @pytest.mark.skip(reason="Requires catalog access - run in integration tests")
    def test_generate_runtime_no_llm_mode(self, valid_spec):
        """Test generation in heuristic-only mode (no LLM)."""
        options = GeneratorOptions(no_llm=True)
        result = generate_runtime_from_spec(valid_spec, options)
        
        assert isinstance(result, GenerationResult)
        assert isinstance(result.runtime, RuntimeConfig)
        # Should still generate valid runtime without LLM
        assert len(result.runtime.roles) > 0
    
    def test_generate_runtime_preserves_spec_metadata(self, valid_spec):
        """Test that generated runtime preserves spec metadata."""
        with patch('llmhub_cli.generator_hook.generate_runtime') as mock_gen:
            # Create mock runtime with spec metadata
            mock_runtime = Mock(spec=RuntimeConfig)
            mock_runtime.project = valid_spec.project
            mock_runtime.env = valid_spec.env
            mock_runtime.providers = {}
            mock_runtime.roles = {}
            
            mock_gen.return_value = GenerationResult(
                runtime=mock_runtime,
                explanations={}
            )
            
            result = generate_runtime_from_spec(valid_spec)
            
            assert result.runtime.project == valid_spec.project
            assert result.runtime.env == valid_spec.env


class TestGeneratorOptions:
    """Tests for GeneratorOptions model."""
    
    def test_generator_options_defaults(self):
        """Test GeneratorOptions default values."""
        options = GeneratorOptions()
        
        assert options.no_llm is False
        assert options.explain is False
    
    def test_generator_options_with_no_llm(self):
        """Test creating options with no_llm=True."""
        options = GeneratorOptions(no_llm=True)
        
        assert options.no_llm is True
        assert options.explain is False
    
    def test_generator_options_with_explain(self):
        """Test creating options with explain=True."""
        options = GeneratorOptions(explain=True)
        
        assert options.no_llm is False
        assert options.explain is True
    
    def test_generator_options_with_both(self):
        """Test creating options with both flags."""
        options = GeneratorOptions(no_llm=True, explain=True)
        
        assert options.no_llm is True
        assert options.explain is True


class TestGenerationResult:
    """Tests for GenerationResult model."""
    
    def test_generation_result_structure(self):
        """Test GenerationResult has expected structure."""
        mock_runtime = Mock(spec=RuntimeConfig)
        result = GenerationResult(
            runtime=mock_runtime,
            explanations={"role1": "explanation1"}
        )
        
        assert hasattr(result, 'runtime')
        assert hasattr(result, 'explanations')
        assert result.runtime == mock_runtime
        assert result.explanations == {"role1": "explanation1"}
    
    def test_generation_result_empty_explanations(self):
        """Test GenerationResult with empty explanations."""
        mock_runtime = Mock(spec=RuntimeConfig)
        result = GenerationResult(
            runtime=mock_runtime,
            explanations={}
        )
        
        assert result.runtime == mock_runtime
        assert result.explanations == {}
        assert isinstance(result.explanations, dict)
    
    def test_generation_result_with_multiple_explanations(self):
        """Test GenerationResult with multiple role explanations."""
        mock_runtime = Mock(spec=RuntimeConfig)
        explanations = {
            "llm.chat": "Selected gpt-4o-mini for cost efficiency",
            "llm.reasoning": "Selected o1-mini for reasoning capability",
            "llm.embedding": "Selected text-embedding-3-small for low cost"
        }
        
        result = GenerationResult(
            runtime=mock_runtime,
            explanations=explanations
        )
        
        assert len(result.explanations) == 3
        assert "llm.chat" in result.explanations
        assert "gpt-4o-mini" in result.explanations["llm.chat"]


class TestGeneratorAPIDocumentation:
    """Tests for API documentation completeness."""
    
    def test_generate_runtime_from_spec_has_docstring(self):
        """Test that generate_runtime_from_spec has docstring."""
        assert generate_runtime_from_spec.__doc__ is not None
        assert len(generate_runtime_from_spec.__doc__) > 0
    
    def test_docstring_contains_examples(self):
        """Test that docstring contains usage examples."""
        docstring = generate_runtime_from_spec.__doc__
        assert "Example:" in docstring or "example" in docstring.lower()
    
    def test_docstring_describes_parameters(self):
        """Test that docstring describes parameters."""
        docstring = generate_runtime_from_spec.__doc__
        assert "spec" in docstring.lower()
        assert "options" in docstring.lower()
    
    def test_docstring_describes_return_value(self):
        """Test that docstring describes return value."""
        docstring = generate_runtime_from_spec.__doc__
        assert "return" in docstring.lower()
        assert "GenerationResult" in docstring
