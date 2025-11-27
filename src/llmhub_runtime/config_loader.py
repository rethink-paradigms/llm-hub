import yaml
from typing import Dict, Any
from .models import RuntimeConfig
from .errors import ConfigError

def load_runtime_config(path: str) -> RuntimeConfig:
    """
    Load and validate the runtime configuration from a YAML file.

    Args:
        path: The file path to the YAML configuration file.

    Returns:
        A validated RuntimeConfig object.

    Raises:
        ConfigError: If the file cannot be read, parsed, or validation fails.
    """
    try:
        with open(path, 'r') as f:
            data = yaml.safe_load(f)
        return parse_runtime_config(data)
    except Exception as e:
        raise ConfigError(f"Failed to load config from {path}: {str(e)}") from e

def parse_runtime_config(data: Dict[str, Any]) -> RuntimeConfig:
    """
    Validate a runtime configuration dictionary.

    Args:
        data: The dictionary containing the configuration data.

    Returns:
        A validated RuntimeConfig object.

    Raises:
        ConfigError: If validation fails.
    """
    try:
        return RuntimeConfig.model_validate(data)
    except Exception as e:
        raise ConfigError(f"Invalid runtime configuration: {str(e)}") from e
