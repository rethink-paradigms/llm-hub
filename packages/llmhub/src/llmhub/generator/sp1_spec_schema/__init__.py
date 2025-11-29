"""
SP1 - Spec Schema: Parse and validate human spec YAML.

Exports:
    - ProjectSpec, RoleSpec, Preferences (data models)
    - parse_project_spec, load_project_spec (functions)
    - SpecSchemaError (exception)
"""
from .models import (
    ProjectSpec,
    RoleSpec,
    Preferences,
    DefaultPreferences,
    ProviderSpec,
)
from .parser import parse_project_spec, load_project_spec
from .errors import SpecSchemaError

__all__ = [
    "ProjectSpec",
    "RoleSpec",
    "Preferences",
    "DefaultPreferences",
    "ProviderSpec",
    "parse_project_spec",
    "load_project_spec",
    "SpecSchemaError",
]
