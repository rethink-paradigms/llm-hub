"""
Integration tests for end-to-end workflows.

Tests complete workflows using the public APIs together.
"""
import pytest
from pathlib import Path
from llmhub_cli import (
    load_spec,
    generate_runtime_from_spec,
    save_runtime,
    load_runtime,
    build_catalog,
)
from llmhub_cli.spec import validate_spec
from llmhub_cli.generator import GeneratorOptions


@pytest.fixture
def fixtures_dir():
    """Return path to test fixtures directory."""
    return Path(__file__).parent.parent / "fixtures"


@pytest.fixture
def valid_spec_path(fixtures_dir):
    """Return path to valid spec fixture."""
    return fixtures_dir / "valid_spec.yaml"


class TestSpecToRuntimeWorkflow:
    """Tests for complete spec to runtime workflow."""
    
    @pytest.mark.skip(reason="Requires catalog and may require LLM - manual integration test")
    def test_full_spec_to_runtime_workflow(self, valid_spec_path, tmp_path):
        """Test complete workflow: load spec → generate → save → load runtime."""
        # Step 1: Load spec
        spec = load_spec(valid_spec_path)
        assert spec.project == "test-project"
        
        # Step 2: Generate runtime
        result = generate_runtime_from_spec(spec)
        assert result.runtime is not None
        
        # Step 3: Save runtime
        runtime_path = tmp_path / "generated_runtime.yaml"
        save_runtime(runtime_path, result.runtime)
        assert runtime_path.exists()
        
        # Step 4: Load runtime back
        loaded_runtime = load_runtime(runtime_path)
        assert loaded_runtime.project == spec.project
        assert loaded_runtime.env == spec.env
        assert len(loaded_runtime.roles) > 0
    
    @pytest.mark.skip(reason="Requires catalog and may require LLM - manual integration test")
    def test_spec_validation_before_generation(self, valid_spec_path, tmp_path):
        """Test workflow with validation before generation."""
        # Step 1: Validate spec
        validation_result = validate_spec(valid_spec_path)
        assert validation_result.valid is True
        
        # Step 2: Load spec
        spec = load_spec(valid_spec_path)
        
        # Step 3: Generate runtime
        result = generate_runtime_from_spec(spec)
        
        # Step 4: Save runtime
        runtime_path = tmp_path / "validated_runtime.yaml"
        save_runtime(runtime_path, result.runtime)
        
        # Verify saved file
        assert runtime_path.exists()
        loaded = load_runtime(runtime_path)
        assert loaded.project == spec.project
    
    @pytest.mark.skip(reason="Requires catalog - manual integration test")
    def test_multi_environment_workflow(self, valid_spec_path, tmp_path):
        """Test generating runtime configs for multiple environments."""
        # Load base spec
        spec = load_spec(valid_spec_path)
        
        environments = ["dev", "staging", "prod"]
        
        for env in environments:
            # Could modify spec.env here if needed
            # For this test, we'll use the same spec
            
            # Generate runtime
            result = generate_runtime_from_spec(spec)
            
            # Save to environment-specific file
            runtime_path = tmp_path / f"llmhub.{env}.yaml"
            save_runtime(runtime_path, result.runtime)
            
            # Verify file exists
            assert runtime_path.exists()
            
            # Verify can be loaded back
            loaded = load_runtime(runtime_path)
            assert loaded.project == spec.project


class TestCatalogToGenerationWorkflow:
    """Tests for catalog querying integrated with runtime generation."""
    
    @pytest.mark.skip(reason="Requires network access - manual integration test")
    def test_catalog_query_before_generation(self, valid_spec_path, tmp_path):
        """Test querying catalog before generating runtime."""
        # Step 1: Build catalog
        catalog = build_catalog()
        assert len(catalog.models) > 0
        
        # Step 2: Load spec
        spec = load_spec(valid_spec_path)
        
        # Step 3: Generate runtime (uses catalog internally)
        result = generate_runtime_from_spec(spec)
        
        # Step 4: Verify runtime has valid model selections
        assert len(result.runtime.roles) > 0
        for role_name, role_config in result.runtime.roles.items():
            assert role_config.provider is not None
            assert role_config.model is not None


class TestProgrammaticSpecCreation:
    """Tests for programmatically creating specs and generating runtimes."""
    
    @pytest.mark.skip(reason="Requires catalog - manual integration test")
    def test_programmatic_spec_to_runtime(self, tmp_path):
        """Test creating spec programmatically and generating runtime."""
        from llmhub_cli import SpecConfig
        from llmhub_cli.spec_models import (
            ProviderSpec,
            RoleSpec,
            PreferencesSpec,
            RoleKind,
        )
        
        # Create spec programmatically
        spec = SpecConfig(
            project="integration-test",
            env="test",
            providers={
                "openai": ProviderSpec(
                    enabled=True,
                    env_key="OPENAI_API_KEY"
                )
            },
            roles={
                "llm.test": RoleSpec(
                    kind=RoleKind.chat,
                    description="Test role",
                    preferences=PreferencesSpec(
                        cost="low",
                        quality="medium",
                        providers=["openai"]
                    ),
                    mode_params={}
                )
            }
        )
        
        # Validate spec
        validation_result = validate_spec(spec)
        assert validation_result.valid is True
        
        # Generate runtime
        result = generate_runtime_from_spec(spec)
        assert result.runtime is not None
        
        # Save and verify
        runtime_path = tmp_path / "programmatic_runtime.yaml"
        save_runtime(runtime_path, result.runtime)
        
        loaded = load_runtime(runtime_path)
        assert loaded.project == "integration-test"
        assert "llm.test" in loaded.roles


class TestErrorHandlingWorkflows:
    """Tests for error handling in integrated workflows."""
    
    def test_invalid_spec_workflow(self, tmp_path):
        """Test workflow handles invalid spec gracefully."""
        # Create invalid spec
        invalid_spec_content = """
project: test
# Missing required env field
providers: {}
roles: {}
"""
        spec_path = tmp_path / "invalid.yaml"
        spec_path.write_text(invalid_spec_content)
        
        # Validation should catch errors
        validation_result = validate_spec(spec_path)
        assert validation_result.valid is False
        assert len(validation_result.errors) > 0
    
    def test_save_load_runtime_consistency(self, tmp_path):
        """Test saving and loading maintains data consistency."""
        from llmhub_runtime.models import RuntimeConfig, ProviderConfig, RoleConfig
        
        # Create runtime programmatically
        runtime = RuntimeConfig(
            project="consistency-test",
            env="test",
            providers={
                "openai": ProviderConfig(env_key="OPENAI_API_KEY")
            },
            roles={
                "llm.test": RoleConfig(
                    provider="openai",
                    model="gpt-4o-mini",
                    mode="chat",
                    params={"temperature": 0.7}
                )
            }
        )
        
        # Save
        runtime_path = tmp_path / "consistency.yaml"
        save_runtime(runtime_path, runtime)
        
        # Load back
        loaded = load_runtime(runtime_path)
        
        # Verify consistency
        assert loaded.project == runtime.project
        assert loaded.env == runtime.env
        assert loaded.providers.keys() == runtime.providers.keys()
        assert loaded.roles.keys() == runtime.roles.keys()
        assert loaded.roles["llm.test"].model == runtime.roles["llm.test"].model
        assert loaded.roles["llm.test"].params["temperature"] == 0.7


class TestComplexWorkflows:
    """Tests for more complex integration scenarios."""
    
    @pytest.mark.skip(reason="Requires catalog and LLM - manual integration test")
    def test_generation_with_explanations_workflow(self, valid_spec_path, tmp_path):
        """Test workflow with explanation generation."""
        # Load spec
        spec = load_spec(valid_spec_path)
        
        # Generate with explanations
        options = GeneratorOptions(explain=True)
        result = generate_runtime_from_spec(spec, options)
        
        # Should have explanations
        assert isinstance(result.explanations, dict)
        assert len(result.explanations) > 0
        
        # Save runtime
        runtime_path = tmp_path / "explained_runtime.yaml"
        save_runtime(runtime_path, result.runtime)
        
        # Verify runtime is valid
        loaded = load_runtime(runtime_path)
        assert loaded.project == spec.project
    
    def test_multiple_save_locations(self, tmp_path):
        """Test saving same runtime to multiple locations."""
        from llmhub_runtime.models import RuntimeConfig, ProviderConfig, RoleConfig
        
        # Create runtime
        runtime = RuntimeConfig(
            project="multi-save",
            env="test",
            providers={
                "openai": ProviderConfig(env_key="OPENAI_API_KEY")
            },
            roles={
                "llm.test": RoleConfig(
                    provider="openai",
                    model="gpt-4o-mini",
                    mode="chat",
                    params={}
                )
            }
        )
        
        # Save to multiple locations
        locations = [
            tmp_path / "loc1" / "runtime.yaml",
            tmp_path / "loc2" / "config.yaml",
            tmp_path / "loc3" / "llmhub.yaml",
        ]
        
        for location in locations:
            save_runtime(location, runtime)
            assert location.exists()
            
            # Verify each can be loaded
            loaded = load_runtime(location)
            assert loaded.project == "multi-save"
