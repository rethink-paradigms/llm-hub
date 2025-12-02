"""
Unit tests for Spec API public functions.

Tests the public API exposed in llmhub_cli.spec module.
"""
import pytest
from pathlib import Path
from llmhub_cli.spec import (
    load_spec,
    validate_spec,
    ValidationResult,
    SpecConfig,
    SpecError,
)


@pytest.fixture
def fixtures_dir():
    """Return path to test fixtures directory."""
    return Path(__file__).parent.parent / "fixtures"


@pytest.fixture
def valid_spec_path(fixtures_dir):
    """Return path to valid spec fixture."""
    return fixtures_dir / "valid_spec.yaml"


@pytest.fixture
def invalid_spec_path(fixtures_dir):
    """Return path to invalid spec fixture."""
    return fixtures_dir / "invalid_spec.yaml"


@pytest.fixture
def malformed_spec_path(fixtures_dir):
    """Return path to malformed spec fixture."""
    return fixtures_dir / "malformed_spec.yaml"


class TestLoadSpec:
    """Tests for load_spec function."""
    
    def test_load_spec_success(self, valid_spec_path):
        """Test loading a valid spec file."""
        spec = load_spec(valid_spec_path)
        
        assert isinstance(spec, SpecConfig)
        assert spec.project == "test-project"
        assert spec.env == "dev"
        assert "openai" in spec.providers
        assert "llm.chat" in spec.roles
        assert len(spec.roles) == 3
    
    def test_load_spec_with_string_path(self, valid_spec_path):
        """Test load_spec accepts string path."""
        spec = load_spec(str(valid_spec_path))
        
        assert isinstance(spec, SpecConfig)
        assert spec.project == "test-project"
    
    def test_load_spec_with_path_object(self, valid_spec_path):
        """Test load_spec accepts Path object."""
        spec = load_spec(valid_spec_path)
        
        assert isinstance(spec, SpecConfig)
        assert spec.project == "test-project"
    
    def test_load_spec_missing_file(self, tmp_path):
        """Test load_spec raises error for missing file."""
        missing_path = tmp_path / "nonexistent.yaml"
        
        with pytest.raises(SpecError) as exc_info:
            load_spec(missing_path)
        
        assert "not found" in str(exc_info.value).lower() or "no such file" in str(exc_info.value).lower()
    
    def test_load_spec_malformed_yaml(self, malformed_spec_path):
        """Test load_spec raises error for malformed YAML."""
        with pytest.raises(SpecError):
            load_spec(malformed_spec_path)
    
    def test_load_spec_returns_correct_structure(self, valid_spec_path):
        """Test loaded spec has correct structure."""
        spec = load_spec(valid_spec_path)
        
        # Verify providers
        assert spec.providers["openai"].enabled is True
        assert spec.providers["openai"].env_key == "OPENAI_API_KEY"
        assert spec.providers["google"].enabled is False
        
        # Verify roles
        chat_role = spec.roles["llm.chat"]
        assert chat_role.description == "General purpose chat interface"
        assert "openai" in chat_role.preferences.providers
        
        # Verify defaults
        assert spec.defaults is not None
        assert "openai" in spec.defaults.providers


class TestValidateSpec:
    """Tests for validate_spec function."""
    
    def test_validate_spec_valid(self, valid_spec_path):
        """Test validating a valid spec returns success."""
        result = validate_spec(valid_spec_path)
        
        assert isinstance(result, ValidationResult)
        assert result.valid is True
        assert len(result.errors) == 0
    
    def test_validate_spec_from_path(self, valid_spec_path):
        """Test validate_spec accepts file path."""
        result = validate_spec(str(valid_spec_path))
        
        assert result.valid is True
    
    def test_validate_spec_from_object(self, valid_spec_path):
        """Test validate_spec accepts SpecConfig object."""
        spec = load_spec(valid_spec_path)
        result = validate_spec(spec)
        
        assert result.valid is True
    
    def test_validate_spec_missing_required_fields(self, invalid_spec_path):
        """Test validation detects missing required fields."""
        result = validate_spec(invalid_spec_path)
        
        assert result.valid is False
        assert len(result.errors) > 0
        # Should detect missing 'env' field
        assert any("env" in error.lower() for error in result.errors)
    
    def test_validate_spec_invalid_provider_reference(self, tmp_path):
        """Test validation detects invalid provider references."""
        spec_content = """
project: test
env: dev
providers:
  openai:
    enabled: true
    env_key: OPENAI_API_KEY
roles:
  llm.chat:
    kind: chat
    description: Test
    force_provider: nonexistent_provider
    preferences:
      cost: low
    mode_params: {}
"""
        spec_path = tmp_path / "spec.yaml"
        spec_path.write_text(spec_content)
        
        result = validate_spec(spec_path)
        
        assert result.valid is False
        assert any("unknown provider" in error.lower() for error in result.errors)
    
    def test_validate_spec_warnings(self, tmp_path):
        """Test validation generates appropriate warnings."""
        spec_content = """
project: test
env: dev
providers:
  openai:
    enabled: true
    env_key: OPENAI_API_KEY
  anthropic:
    enabled: false
    env_key: ANTHROPIC_API_KEY
roles:
  llm.chat:
    kind: chat
    description: Test
    force_provider: anthropic
    preferences:
      cost: low
    mode_params: {}
"""
        spec_path = tmp_path / "spec.yaml"
        spec_path.write_text(spec_content)
        
        result = validate_spec(spec_path)
        
        # Should have warning about forcing disabled provider
        assert len(result.warnings) > 0
        assert any("disabled provider" in warning.lower() for warning in result.warnings)
    
    def test_validate_spec_force_provider_without_model(self, tmp_path):
        """Test warning for force_provider without force_model."""
        spec_content = """
project: test
env: dev
providers:
  openai:
    enabled: true
    env_key: OPENAI_API_KEY
roles:
  llm.chat:
    kind: chat
    description: Test
    force_provider: openai
    preferences:
      cost: low
    mode_params: {}
"""
        spec_path = tmp_path / "spec.yaml"
        spec_path.write_text(spec_content)
        
        result = validate_spec(spec_path)
        
        # Should have warning
        assert len(result.warnings) > 0
        assert any("force_provider" in warning.lower() and "force_model" in warning.lower() 
                  for warning in result.warnings)
    
    def test_validate_spec_no_providers(self, tmp_path):
        """Test validation detects missing providers."""
        spec_content = """
project: test
env: dev
providers: {}
roles:
  llm.chat:
    kind: chat
    description: Test
    preferences:
      cost: low
    mode_params: {}
"""
        spec_path = tmp_path / "spec.yaml"
        spec_path.write_text(spec_content)
        
        result = validate_spec(spec_path)
        
        assert result.valid is False
        assert any("provider" in error.lower() for error in result.errors)
    
    def test_validate_spec_no_enabled_providers(self, tmp_path):
        """Test validation detects no enabled providers."""
        spec_content = """
project: test
env: dev
providers:
  openai:
    enabled: false
    env_key: OPENAI_API_KEY
roles:
  llm.chat:
    kind: chat
    description: Test
    preferences:
      cost: low
    mode_params: {}
"""
        spec_path = tmp_path / "spec.yaml"
        spec_path.write_text(spec_content)
        
        result = validate_spec(spec_path)
        
        assert result.valid is False
        assert any("enabled" in error.lower() for error in result.errors)
    
    def test_validate_spec_no_roles(self, tmp_path):
        """Test validation detects missing roles."""
        spec_content = """
project: test
env: dev
providers:
  openai:
    enabled: true
    env_key: OPENAI_API_KEY
roles: {}
"""
        spec_path = tmp_path / "spec.yaml"
        spec_path.write_text(spec_content)
        
        result = validate_spec(spec_path)
        
        assert result.valid is False
        assert any("role" in error.lower() for error in result.errors)
    
    def test_validate_spec_file_not_found(self, tmp_path):
        """Test validation handles missing file gracefully."""
        missing_path = tmp_path / "nonexistent.yaml"
        
        result = validate_spec(missing_path)
        
        assert result.valid is False
        assert len(result.errors) > 0
        assert any("failed to load" in error.lower() for error in result.errors)
    
    def test_validate_spec_invalid_type(self):
        """Test validation rejects invalid spec type."""
        result = validate_spec({"invalid": "dict"})
        
        assert result.valid is False
        assert any("invalid spec type" in error.lower() for error in result.errors)
