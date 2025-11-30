"""
SP3 - Needs Schema: Parser for RoleNeed.

Provides function to parse raw dicts into validated RoleNeed objects.
"""
from typing import Dict, Any, List
from .models import RoleNeed
from .errors import NeedsSchemaError


def parse_role_needs(raw: List[Dict[str, Any]]) -> List[RoleNeed]:
    """
    Parse raw dicts into validated RoleNeed objects.
    
    Args:
        raw: List of dicts from LLM output
        
    Returns:
        List of validated RoleNeed instances
        
    Raises:
        NeedsSchemaError: If validation fails
    """
    if not isinstance(raw, list):
        raise NeedsSchemaError("Expected list of role needs")
    
    needs = []
    errors = []
    
    for i, item in enumerate(raw):
        try:
            need = RoleNeed.model_validate(item)
            needs.append(need)
        except Exception as e:
            errors.append(f"Role {i}: {str(e)}")
    
    if errors:
        error_msg = "Failed to parse role needs:\n" + "\n".join(errors)
        raise NeedsSchemaError(error_msg)
    
    return needs
