"""
SP3 - Needs Schema: Canonical RoleNeed model and parser.

Exports:
    - RoleNeed (data model)
    - parse_role_needs (parser function)
    - NeedsSchemaError (exception)
"""
from .models import RoleNeed
from .parser import parse_role_needs
from .errors import NeedsSchemaError

__all__ = [
    "RoleNeed",
    "parse_role_needs",
    "NeedsSchemaError",
]
