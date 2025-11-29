import os
import pytest
from pathlib import Path
from llmhub_runtime.config_loader import load_runtime_config, parse_runtime_config
from llmhub_runtime.errors import ConfigError

FIXTURE_PATH = str(Path(__file__).parent / "fixtures" / "llmhub.yaml")

def test_load_runtime_config_success():
    config = load_runtime_config(FIXTURE_PATH)
    assert config.project == "memory"
    assert config.env == "dev"
    assert "openai" in config.providers
    assert config.roles["llm.inference"].model == "gpt-4"

def test_load_runtime_config_file_not_found():
    with pytest.raises(ConfigError) as excinfo:
        load_runtime_config("non_existent_file.yaml")
    assert "Failed to load config" in str(excinfo.value)

def test_parse_runtime_config_invalid_data():
    invalid_data = {"project": "test"} # Missing required fields
    with pytest.raises(ConfigError) as excinfo:
        parse_runtime_config(invalid_data)
    assert "Invalid runtime configuration" in str(excinfo.value)
