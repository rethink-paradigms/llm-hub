"""
SP1 - Spec Schema: Parser functions.

Provides functions to parse and load ProjectSpec from YAML.
"""
from pathlib import Path
from typing import Dict, Any
import yaml
from .models import ProjectSpec
from .errors import SpecSchemaError


def parse_project_spec(raw: Dict[str, Any]) -> ProjectSpec:
    """
    Parse and validate raw YAML dict into ProjectSpec.
    
    Args:
        raw: Dictionary loaded from YAML file
        
    Returns:
        Validated ProjectSpec instance
        
    Raises:
        SpecSchemaError: If validation fails
    """
    try:
        return ProjectSpec.model_validate(raw)
    except Exception as e:
        raise SpecSchemaError(f"Failed to parse project spec: {str(e)}") from e


def load_project_spec(path: str) -> ProjectSpec:
    """
    Load ProjectSpec from file path.
    
    Args:
        path: Path to llmhub.spec.yaml
        
    Returns:
        Validated ProjectSpec instance
        
    Raises:
        SpecSchemaError: If file not found or validation fails
    """
    file_path = Path(path)
    
    if not file_path.exists():
        raise SpecSchemaError(f"Spec file not found: {path}")
    
    try:
        with open(file_path, 'r') as f:
            raw = yaml.safe_load(f)
        
        if raw is None:
            raise SpecSchemaError(f"Spec file is empty: {path}")
        
        return parse_project_spec(raw)
        
    except yaml.YAMLError as e:
        raise SpecSchemaError(f"Invalid YAML in spec file: {e}") from e
    except SpecSchemaError:
        # Re-raise SpecSchemaError as-is
        raise
    except Exception as e:
        raise SpecSchemaError(f"Failed to load spec from {path}: {str(e)}") from e
