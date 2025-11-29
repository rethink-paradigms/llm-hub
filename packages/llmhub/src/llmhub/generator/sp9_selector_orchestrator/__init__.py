"""
SP9 - Selector Orchestrator: Coordinate model selection for a role.

Exports:
    - SelectionResult, SelectorOptions (models)
    - select_for_role (function)
"""
from .models import SelectionResult, SelectorOptions
from .orchestrator import select_for_role

__all__ = [
    "SelectionResult",
    "SelectorOptions",
    "select_for_role",
]
