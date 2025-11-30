"""Generator needs module - handles LLM interpretation and needs schema."""

from llmhub_cli.generator.needs.interpreter import interpret_needs
from llmhub_cli.generator.needs.schema import parse_role_needs
from llmhub_cli.generator.needs.models import RoleNeed
from llmhub_cli.generator.needs.errors import NeedsSchemaError, InterpreterError

__all__ = ["interpret_needs", "parse_role_needs", "RoleNeed", "NeedsSchemaError", "InterpreterError"]
