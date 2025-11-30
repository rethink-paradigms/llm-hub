"""Generator needs module - handles LLM interpretation and needs schema."""

from llmhub_cli.generator.needs.interpreter import interpret_needs
from llmhub_cli.generator.needs.schema import parse_needs_schema
from llmhub_cli.generator.needs.models import RoleNeed

__all__ = ["interpret_needs", "parse_needs_schema", "RoleNeed"]
