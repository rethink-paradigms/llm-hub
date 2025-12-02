"""
Unit tests for Runtime API public functions.

Tests the public API exposed in llmhub_cli.runtime module.
"""
import pytest
from pathlib import Path
from llmhub_cli.runtime import (
    load_runtime,
    save_runtime,
    RuntimeConfig,
    RuntimeError,
)


@pytest.fixture
def fixtures_dir():
    """Return path to test fixtures directory."""
    return Path(__file__).parent.parent / "fixtures"


@pytest.fixture
def valid_runtime_path(fixtures_dir):
    """Return path to valid runtime fixture."""
    return fixtures_dir / "valid_runtime.yaml"


class TestLoadRuntime:
    """Tests for load_runtime function."""
    
    def test_load_runtime_success(self, valid_runtime_path):
        """Test loading a valid runtime file."""
        runtime = load_runtime(valid_runtime_path)
        
        assert isinstance(runtime, RuntimeConfig)
        assert runtime.project == "test-project"
        assert runtime.env == "dev"
        assert "openai" in runtime.providers
        assert "llm.chat" in runtime.roles
        assert len(runtime.roles) == 3
    
    def test_load_runtime_with_string_path(self, valid_runtime_path):
        """Test load_runtime accepts string path."""
        runtime = load_runtime(str(valid_runtime_path))
        
        assert isinstance(runtime, RuntimeConfig)
        assert runtime.project == "test-project"
    
    def test_load_runtime_with_path_object(self, valid_runtime_path):
        """Test load_runtime accepts Path object."""
        runtime = load_runtime(valid_runtime_path)
        
        assert isinstance(runtime, RuntimeConfig)
        assert runtime.project == "test-project"
    
    def test_load_runtime_missing_file(self, tmp_path):
        """Test load_runtime raises error for missing file."""
        missing_path = tmp_path / "nonexistent.yaml"
        
        with pytest.raises(RuntimeError) as exc_info:
            load_runtime(missing_path)
        
        assert "not found" in str(exc_info.value).lower() or "no such file" in str(exc_info.value).lower()
    
    def test_load_runtime_invalid_yaml(self, tmp_path):
        """Test load_runtime raises error for malformed YAML."""
        bad_yaml = tmp_path / "bad.yaml"
        bad_yaml.write_text("project: test\nunclosed: 'quote")
        
        with pytest.raises(RuntimeError):
            load_runtime(bad_yaml)
    
    def test_load_runtime_returns_correct_structure(self, valid_runtime_path):
        """Test loaded runtime has correct structure."""
        runtime = load_runtime(valid_runtime_path)
        
        # Verify providers
        assert "openai" in runtime.providers
        assert runtime.providers["openai"].env_key == "OPENAI_API_KEY"
        
        # Verify roles
        assert runtime.roles["llm.chat"].provider == "openai"
        assert runtime.roles["llm.chat"].model == "gpt-4o-mini"
        assert runtime.roles["llm.chat"].mode == "chat"
        
        # Verify params
        assert runtime.roles["llm.chat"].params.get("temperature") == 0.7
        
        # Verify defaults
        assert runtime.defaults is not None
        assert runtime.defaults.provider == "openai"


class TestSaveRuntime:
    """Tests for save_runtime function."""
    
    def test_save_runtime_success(self, valid_runtime_path, tmp_path):
        """Test saving a runtime configuration."""
        # Load runtime
        runtime = load_runtime(valid_runtime_path)
        
        # Save to new location
        output_path = tmp_path / "output.yaml"
        save_runtime(output_path, runtime)
        
        # Verify file exists
        assert output_path.exists()
        
        # Verify content is valid by loading it back
        loaded = load_runtime(output_path)
        assert loaded.project == runtime.project
        assert loaded.env == runtime.env
    
    def test_save_runtime_with_string_path(self, valid_runtime_path, tmp_path):
        """Test save_runtime accepts string path."""
        runtime = load_runtime(valid_runtime_path)
        output_path = tmp_path / "output.yaml"
        
        save_runtime(str(output_path), runtime)
        
        assert output_path.exists()
    
    def test_save_runtime_with_path_object(self, valid_runtime_path, tmp_path):
        """Test save_runtime accepts Path object."""
        runtime = load_runtime(valid_runtime_path)
        output_path = tmp_path / "output.yaml"
        
        save_runtime(output_path, runtime)
        
        assert output_path.exists()
    
    def test_save_runtime_creates_directory(self, valid_runtime_path, tmp_path):
        """Test save_runtime creates parent directories if needed."""
        runtime = load_runtime(valid_runtime_path)
        
        # Create path with non-existent parent directory
        output_path = tmp_path / "subdir" / "nested" / "output.yaml"
        
        save_runtime(output_path, runtime)
        
        assert output_path.exists()
        assert output_path.parent.exists()
    
    def test_save_runtime_overwrites_existing(self, valid_runtime_path, tmp_path):
        """Test save_runtime overwrites existing file."""
        runtime = load_runtime(valid_runtime_path)
        output_path = tmp_path / "output.yaml"
        
        # Write initial content
        output_path.write_text("old content")
        
        # Save runtime
        save_runtime(output_path, runtime)
        
        # Verify file was overwritten
        content = output_path.read_text()
        assert "old content" not in content
        assert "test-project" in content
    
    def test_save_load_roundtrip(self, valid_runtime_path, tmp_path):
        """Test save then load maintains data consistency."""
        # Load original
        original = load_runtime(valid_runtime_path)
        
        # Save to new location
        output_path = tmp_path / "roundtrip.yaml"
        save_runtime(output_path, original)
        
        # Load back
        loaded = load_runtime(output_path)
        
        # Verify all fields match
        assert loaded.project == original.project
        assert loaded.env == original.env
        assert loaded.providers.keys() == original.providers.keys()
        assert loaded.roles.keys() == original.roles.keys()
        
        # Verify role details
        for role_name in original.roles.keys():
            assert loaded.roles[role_name].provider == original.roles[role_name].provider
            assert loaded.roles[role_name].model == original.roles[role_name].model
            assert loaded.roles[role_name].mode == original.roles[role_name].mode
    
    def test_save_runtime_preserves_structure(self, valid_runtime_path, tmp_path):
        """Test saved YAML has correct structure."""
        runtime = load_runtime(valid_runtime_path)
        output_path = tmp_path / "output.yaml"
        
        save_runtime(output_path, runtime)
        
        # Read as text and verify structure
        content = output_path.read_text()
        assert "project:" in content
        assert "env:" in content
        assert "providers:" in content
        assert "roles:" in content
        assert "llm.chat:" in content


class TestRuntimeConfigModel:
    """Tests for RuntimeConfig model usage."""
    
    def test_runtime_config_from_dict(self):
        """Test creating RuntimeConfig from dictionary."""
        data = {
            "project": "test",
            "env": "dev",
            "providers": {
                "openai": {
                    "env_key": "OPENAI_API_KEY"
                }
            },
            "roles": {
                "llm.chat": {
                    "provider": "openai",
                    "model": "gpt-4o-mini",
                    "mode": "chat",
                    "params": {}
                }
            }
        }
        
        runtime = RuntimeConfig(**data)
        
        assert runtime.project == "test"
        assert runtime.env == "dev"
        assert "openai" in runtime.providers
        assert "llm.chat" in runtime.roles
    
    def test_runtime_config_to_dict(self, valid_runtime_path):
        """Test converting RuntimeConfig to dictionary."""
        runtime = load_runtime(valid_runtime_path)
        
        # Convert to dict
        data = runtime.model_dump()
        
        assert isinstance(data, dict)
        assert data["project"] == "test-project"
        assert data["env"] == "dev"
        assert "providers" in data
        assert "roles" in data
