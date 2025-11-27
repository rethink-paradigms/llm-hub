import os
from typing import Any

import yaml
from pydantic import ValidationError

from ..utils.errors import ConfigError
from .schema import OrchestratorConfig


def _load_yaml(config_path: str) -> Any:
    if not os.path.exists(config_path):
        raise ConfigError(f"Config file not found: {config_path}")

    try:
        with open(config_path, "r") as file:
            return yaml.safe_load(file)
    except yaml.YAMLError as exc:
        raise ConfigError(f"Failed to parse YAML at {config_path}: {exc}") from exc
    except OSError as exc:
        raise ConfigError(f"Unable to read config file {config_path}: {exc}") from exc


def load_config(config_path: str) -> OrchestratorConfig:
    """
    Load and validate an orchestrator config from disk.
    """
    raw_data = _load_yaml(config_path)
    if raw_data is None:
        raise ConfigError(f"Config file is empty: {config_path}")
    if not isinstance(raw_data, dict):
        raise ConfigError(f"Config root must be a mapping object in {config_path}")

    try:
        return OrchestratorConfig(**raw_data)
    except ValidationError as exc:
        raise ConfigError(f"Config validation failed for {config_path}: {exc}") from exc
