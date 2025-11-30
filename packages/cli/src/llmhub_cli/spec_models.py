from enum import Enum
from pathlib import Path
from typing import Any, Optional
import yaml
from pydantic import BaseModel, Field


class SpecError(Exception):
    """Raised when spec loading or validation fails."""
    pass


class PreferenceLevel(str, Enum):
    """Preference level for cost, latency, or quality."""
    low = "low"
    medium = "medium"
    high = "high"


class RoleKind(str, Enum):
    """LLM role kind/mode."""
    chat = "chat"
    embedding = "embedding"
    image = "image"
    audio = "audio"
    tool = "tool"
    other = "other"


class SpecProviderConfig(BaseModel):
    """Provider configuration in spec."""
    enabled: bool = True
    env_key: Optional[str] = None


class Preferences(BaseModel):
    """Role preferences for model selection."""
    latency: Optional[PreferenceLevel] = None
    cost: Optional[PreferenceLevel] = None
    quality: Optional[PreferenceLevel] = None
    providers: Optional[list[str]] = None


class RoleSpec(BaseModel):
    """Specification for a single role."""
    kind: RoleKind
    description: str
    preferences: Preferences = Field(default_factory=Preferences)
    force_provider: Optional[str] = None
    force_model: Optional[str] = None
    mode_params: dict[str, Any] = Field(default_factory=dict)


class SpecDefaults(BaseModel):
    """Default provider preferences."""
    providers: list[str] = Field(default_factory=list)


class SpecConfig(BaseModel):
    """Complete spec configuration."""
    project: str
    env: str
    providers: dict[str, SpecProviderConfig]
    roles: dict[str, RoleSpec]
    defaults: Optional[SpecDefaults] = None


def load_spec(path: Path) -> SpecConfig:
    """
    Load and validate spec from YAML file.
    
    Args:
        path: Path to llmhub.spec.yaml.
    
    Returns:
        Validated SpecConfig.
    
    Raises:
        SpecError: If file cannot be read or validation fails.
    """
    try:
        with open(path, 'r') as f:
            data = yaml.safe_load(f)
        return SpecConfig.model_validate(data)
    except FileNotFoundError:
        raise SpecError(f"Spec file not found: {path}")
    except yaml.YAMLError as e:
        raise SpecError(f"Invalid YAML in spec file: {e}")
    except Exception as e:
        raise SpecError(f"Failed to load spec from {path}: {str(e)}")


def save_spec(path: Path, spec: SpecConfig) -> None:
    """
    Save spec to YAML file with stable ordering.
    
    Args:
        path: Path to write llmhub.spec.yaml.
        spec: SpecConfig to save.
    
    Raises:
        SpecError: If file cannot be written.
    """
    try:
        # Convert to dict with proper serialization of enums
        data = spec.model_dump(mode='python', exclude_none=True, by_alias=False)
        
        # Convert enum values to strings
        def convert_enums(obj):
            if isinstance(obj, dict):
                return {k: convert_enums(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_enums(item) for item in obj]
            elif isinstance(obj, (PreferenceLevel, RoleKind)):
                return obj.value
            return obj
        
        data = convert_enums(data)
        
        # Write YAML with nice formatting
        with open(path, 'w') as f:
            yaml.dump(
                data,
                f,
                default_flow_style=False,
                sort_keys=False,
                allow_unicode=True
            )
    except Exception as e:
        raise SpecError(f"Failed to save spec to {path}: {str(e)}")
