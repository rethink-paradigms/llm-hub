"""SP2/SP3 - Needs Schema: Error definitions."""


class InterpreterError(Exception):
    """Raised when needs interpretation via LLM fails."""
    pass


class NeedsSchemaError(Exception):
    """Raised when RoleNeed parsing or validation fails."""
    pass
