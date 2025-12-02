"""
Spec module: Load and validate LLMHub spec configurations.

This module provides programmatic access to spec file operations,
allowing developers to load, validate, and work with spec configurations
without using the CLI.
"""
from pathlib import Path
from typing import Union
from pydantic import BaseModel, Field

from ..spec_models import (
    SpecConfig,
    SpecProviderConfig as ProviderSpec,
    RoleSpec,
    Preferences as PreferencesSpec,
    RoleKind,
    load_spec as _load_spec,
    SpecError,
)


class ValidationResult(BaseModel):
    """Result of spec validation."""
    valid: bool
    errors: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)


def load_spec(spec_path: Union[str, Path]) -> SpecConfig:
    """
    Load and validate spec configuration from YAML file.
    
    This function reads a spec file, parses it, and validates the structure
    using Pydantic models. It's useful for programmatic access to spec
    configurations in applications, testing, and automation.
    
    Args:
        spec_path: Path to spec YAML file (string or Path object)
    
    Returns:
        SpecConfig object with validated configuration containing:
            - project: Project name
            - env: Environment name (dev, staging, prod, etc.)
            - providers: Dictionary of provider configurations
            - roles: Dictionary of role specifications
            - defaults: Optional default configurations
    
    Raises:
        SpecError: If file not found, cannot be parsed, or validation fails
    
    Example:
        >>> from llmhub_cli.spec import load_spec
        >>> 
        >>> # Load spec file
        >>> spec = load_spec("llmhub.spec.yaml")
        >>> 
        >>> # Access spec properties
        >>> print(f"Project: {spec.project}")
        >>> print(f"Roles: {list(spec.roles.keys())}")
        >>> 
        >>> # Iterate through roles
        >>> for role_name, role_spec in spec.roles.items():
        ...     print(f"  {role_name}: {role_spec.kind} - {role_spec.description}")
    
    See Also:
        - validate_spec: Validate a spec configuration
        - SpecConfig: The spec configuration model
    """
    return _load_spec(spec_path)


def validate_spec(spec: Union[SpecConfig, str, Path]) -> ValidationResult:
    """
    Validate spec configuration and return detailed results.
    
    This function validates a spec configuration, either from a SpecConfig
    object or by loading from a file path. It checks for structural issues,
    required fields, and logical consistency.
    
    Args:
        spec: Either a SpecConfig object or path to spec file
    
    Returns:
        ValidationResult object containing:
            - valid (bool): True if spec is valid
            - errors (list[str]): List of validation error messages
            - warnings (list[str]): List of validation warnings
    
    Example:
        >>> from llmhub_cli.spec import validate_spec
        >>> 
        >>> # Validate from file path
        >>> result = validate_spec("llmhub.spec.yaml")
        >>> 
        >>> if result.valid:
        ...     print("Spec is valid")
        ... else:
        ...     print("Validation errors:")
        ...     for error in result.errors:
        ...         print(f"  - {error}")
        >>> 
        >>> # Validate existing SpecConfig object
        >>> from llmhub_cli.spec import load_spec
        >>> spec = load_spec("llmhub.spec.yaml")
        >>> result = validate_spec(spec)
    
    See Also:
        - load_spec: Load a spec from file
        - SpecConfig: The spec configuration model
    """
    errors = []
    warnings = []
    
    # If spec is a path, try to load it
    if isinstance(spec, (str, Path)):
        try:
            spec = load_spec(spec)
        except SpecError as e:
            return ValidationResult(
                valid=False,
                errors=[f"Failed to load spec: {str(e)}"]
            )
    
    # Validate that spec is a SpecConfig instance
    if not isinstance(spec, SpecConfig):
        return ValidationResult(
            valid=False,
            errors=["Invalid spec type: expected SpecConfig object"]
        )
    
    # Basic validation - check required fields
    if not spec.project:
        errors.append("Project name is required")
    
    if not spec.env:
        errors.append("Environment name is required")
    
    # Validate providers
    if not spec.providers:
        errors.append("At least one provider must be configured")
    else:
        enabled_providers = [p for p, cfg in spec.providers.items() if cfg.enabled]
        if not enabled_providers:
            errors.append("At least one provider must be enabled")
    
    # Validate roles
    if not spec.roles:
        errors.append("At least one role must be defined")
    else:
        for role_name, role_spec in spec.roles.items():
            # Check for forced provider/model consistency
            if role_spec.force_provider and not role_spec.force_model:
                warnings.append(
                    f"Role '{role_name}' has force_provider but no force_model"
                )
            if role_spec.force_model and not role_spec.force_provider:
                warnings.append(
                    f"Role '{role_name}' has force_model but no force_provider"
                )
            
            # Check if forced provider exists and is enabled
            if role_spec.force_provider:
                if role_spec.force_provider not in spec.providers:
                    errors.append(
                        f"Role '{role_name}' forces unknown provider '{role_spec.force_provider}'"
                    )
                elif not spec.providers[role_spec.force_provider].enabled:
                    warnings.append(
                        f"Role '{role_name}' forces disabled provider '{role_spec.force_provider}'"
                    )
            
            # Check if preferred providers exist
            if role_spec.preferences.providers:
                for pref_provider in role_spec.preferences.providers:
                    if pref_provider not in spec.providers:
                        warnings.append(
                            f"Role '{role_name}' prefers unknown provider '{pref_provider}'"
                        )
    
    # Validate defaults
    if spec.defaults and spec.defaults.providers:
        for default_provider in spec.defaults.providers:
            if default_provider not in spec.providers:
                warnings.append(
                    f"Default provider '{default_provider}' is not configured"
                )
    
    return ValidationResult(
        valid=len(errors) == 0,
        errors=errors,
        warnings=warnings
    )


__all__ = [
    "load_spec",
    "validate_spec",
    "ValidationResult",
    "SpecConfig",
    "ProviderSpec",
    "RoleSpec",
    "PreferencesSpec",
    "RoleKind",
    "SpecError",
]
