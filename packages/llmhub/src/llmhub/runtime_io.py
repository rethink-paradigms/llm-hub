from pathlib import Path
import yaml
from llmhub_runtime.models import RuntimeConfig, LLMMode


class RuntimeError(Exception):
    """Raised when runtime loading or saving fails."""
    pass


def load_runtime(path: Path) -> RuntimeConfig:
    """
    Load runtime config from YAML file.
    
    Args:
        path: Path to llmhub.yaml.
    
    Returns:
        Validated RuntimeConfig.
    
    Raises:
        RuntimeError: If file cannot be read or validation fails.
    """
    try:
        with open(path, 'r') as f:
            data = yaml.safe_load(f)
        return RuntimeConfig.model_validate(data)
    except FileNotFoundError:
        raise RuntimeError(f"Runtime file not found: {path}")
    except yaml.YAMLError as e:
        raise RuntimeError(f"Invalid YAML in runtime file: {e}")
    except Exception as e:
        raise RuntimeError(f"Failed to load runtime from {path}: {str(e)}")


def save_runtime(path: Path, runtime: RuntimeConfig) -> None:
    """
    Save runtime config to YAML file.
    
    Args:
        path: Path to write llmhub.yaml.
        runtime: RuntimeConfig to save.
    
    Raises:
        RuntimeError: If file cannot be written.
    """
    try:
        # Convert to dict
        data = runtime.model_dump(mode='python', exclude_none=True)
        
        # Convert enum values to strings
        def convert_enums(obj):
            if isinstance(obj, dict):
                return {k: convert_enums(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_enums(item) for item in obj]
            elif isinstance(obj, LLMMode):
                return obj.value
            return obj
        
        data = convert_enums(data)
        
        # Write YAML with stable formatting
        with open(path, 'w') as f:
            yaml.dump(
                data,
                f,
                default_flow_style=False,
                sort_keys=False,
                allow_unicode=True
            )
    except Exception as e:
        raise RuntimeError(f"Failed to save runtime to {path}: {str(e)}")
