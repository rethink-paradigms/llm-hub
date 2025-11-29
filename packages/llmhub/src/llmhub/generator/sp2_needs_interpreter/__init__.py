"""
SP2 - Needs Interpreter: Convert ProjectSpec to RoleNeeds via LLM.

Exports:
    - interpret_needs (function)
    - InterpreterError (exception)
"""
from .interpreter import interpret_needs
from .errors import InterpreterError

__all__ = [
    "interpret_needs",
    "InterpreterError",
]
