"""
SP2 - Needs Interpreter: LLM-based spec interpretation.

Converts ProjectSpec to RoleNeeds using structured LLM output.
"""
import json
from typing import List
from llmhub_runtime import LLMHub
from llmhub_cli.generator.spec import ProjectSpec
from llmhub_cli.generator.needs import RoleNeed, parse_role_needs
from .errors import InterpreterError
from .prompt import build_interpretation_prompt, ROLE_NEED_SCHEMA


def interpret_needs(
    spec: ProjectSpec,
    hub: LLMHub,
    model_role: str = "llm.generator"
) -> List[RoleNeed]:
    """
    Interpret human spec into canonical RoleNeeds using LLM.
    
    Args:
        spec: ProjectSpec from SP1
        hub: LLMHub instance for making LLM calls
        model_role: Role name in hub config (default: "llm.generator")
        
    Returns:
        List of RoleNeed objects
        
    Raises:
        InterpreterError: If LLM call or parsing fails
    """
    try:
        # Build prompt
        prompt = build_interpretation_prompt(spec)
        
        # Prepare messages
        messages = [
            {
                "role": "system",
                "content": "You are an expert at interpreting LLM usage specifications and converting them into structured role requirements."
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
        
        # Call LLM with structured output
        # Note: This assumes the hub/runtime supports response_format parameter
        response = hub.completion(
            role=model_role,
            messages=messages,
            params_override={
                "response_format": {"type": "json_object"},
                "temperature": 0.3,
            }
        )
        
        # Extract content
        if hasattr(response, 'choices') and response.choices:
            content = response.choices[0].message.content
        elif isinstance(response, dict):
            content = response.get("choices", [{}])[0].get("message", {}).get("content", "")
        else:
            content = str(response)
        
        # Parse JSON
        try:
            data = json.loads(content)
        except json.JSONDecodeError as e:
            raise InterpreterError(f"LLM returned invalid JSON: {str(e)}")
        
        # Extract role needs array
        if "roles" in data:
            raw_needs = data["roles"]
        elif isinstance(data, list):
            raw_needs = data
        else:
            raise InterpreterError(f"Unexpected response format: {data}")
        
        # Parse into RoleNeed objects
        needs = parse_role_needs(raw_needs)
        
        return needs
        
    except InterpreterError:
        raise
    except Exception as e:
        raise InterpreterError(f"Failed to interpret needs: {str(e)}") from e
