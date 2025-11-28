import pytest
import os
from pathlib import Path
from llmhub.spec_models import SpecConfig, SpecProviderConfig, RoleSpec, RoleKind
from llmhub.env_manager import generate_env_example, check_env, MissingEnvVar


def test_generate_env_example(tmp_path):
    """Test generating .env.example file."""
    spec = SpecConfig(
        project="test",
        env="dev",
        providers={
            "openai": SpecProviderConfig(enabled=True, env_key="OPENAI_API_KEY"),
            "anthropic": SpecProviderConfig(enabled=True, env_key="ANTHROPIC_API_KEY")
        },
        roles={}
    )
    
    env_path = tmp_path / ".env.example"
    generate_env_example(spec, env_path)
    
    assert env_path.exists()
    content = env_path.read_text()
    
    assert "OPENAI_API_KEY=" in content
    assert "ANTHROPIC_API_KEY=" in content
    assert "test" in content
    assert "dev" in content


def test_generate_env_example_overwrite(tmp_path):
    """Test overwriting existing .env.example."""
    env_path = tmp_path / ".env.example"
    env_path.write_text("old content")
    
    spec = SpecConfig(
        project="test",
        env="dev",
        providers={
            "openai": SpecProviderConfig(enabled=True, env_key="OPENAI_API_KEY")
        },
        roles={}
    )
    
    generate_env_example(spec, env_path, overwrite=True)
    content = env_path.read_text()
    
    assert "OPENAI_API_KEY=" in content
    assert "old content" not in content


def test_check_env_missing_vars():
    """Test checking for missing environment variables."""
    # Clear env vars if they exist
    old_openai = os.environ.pop("OPENAI_API_KEY", None)
    old_anthropic = os.environ.pop("ANTHROPIC_API_KEY", None)
    
    try:
        spec = SpecConfig(
            project="test",
            env="dev",
            providers={
                "openai": SpecProviderConfig(enabled=True, env_key="OPENAI_API_KEY"),
                "anthropic": SpecProviderConfig(enabled=True, env_key="ANTHROPIC_API_KEY")
            },
            roles={}
        )
        
        missing = check_env(spec)
        
        assert len(missing) == 2
        env_keys = [m.env_key for m in missing]
        assert "OPENAI_API_KEY" in env_keys
        assert "ANTHROPIC_API_KEY" in env_keys
    finally:
        # Restore env vars
        if old_openai:
            os.environ["OPENAI_API_KEY"] = old_openai
        if old_anthropic:
            os.environ["ANTHROPIC_API_KEY"] = old_anthropic


def test_check_env_with_set_vars():
    """Test checking when env vars are set."""
    os.environ["TEST_OPENAI_KEY"] = "test-key"
    
    try:
        spec = SpecConfig(
            project="test",
            env="dev",
            providers={
                "openai": SpecProviderConfig(enabled=True, env_key="TEST_OPENAI_KEY")
            },
            roles={}
        )
        
        missing = check_env(spec)
        assert len(missing) == 0
    finally:
        os.environ.pop("TEST_OPENAI_KEY", None)


def test_check_env_disabled_provider():
    """Test that disabled providers are not checked."""
    spec = SpecConfig(
        project="test",
        env="dev",
        providers={
            "openai": SpecProviderConfig(enabled=False, env_key="MISSING_KEY")
        },
        roles={}
    )
    
    missing = check_env(spec)
    assert len(missing) == 0


def test_check_env_with_dotenv(tmp_path):
    """Test checking env with .env file loading."""
    # Create .env file
    env_file = tmp_path / ".env"
    env_file.write_text("TEST_KEY_FROM_FILE=test-value\n")
    
    spec = SpecConfig(
        project="test",
        env="dev",
        providers={
            "test": SpecProviderConfig(enabled=True, env_key="TEST_KEY_FROM_FILE")
        },
        roles={}
    )
    
    missing = check_env(spec, load_dotenv_path=env_file)
    assert len(missing) == 0
    
    # Clean up
    os.environ.pop("TEST_KEY_FROM_FILE", None)
