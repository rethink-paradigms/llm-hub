"""
SP2 - Needs Interpreter: Prompt building for LLM interpretation.

Constructs prompts and schema for converting ProjectSpec to RoleNeeds.
"""
from llmhub_cli.generator.spec import ProjectSpec


ROLE_NEED_SCHEMA = """
{
  "roles": [
    {
      "id": "string (role identifier)",
      "task_kind": "string (reasoning|creative|factual|chat|general)",
      "importance": "string (low|medium|high|critical)",
      "quality_bias": "float 0.0-1.0 (bias towards quality)",
      "cost_bias": "float 0.0-1.0 (bias towards low cost)",
      "latency_sensitivity": "float 0.0-1.0 (sensitivity to latency)",
      "reasoning_required": "boolean",
      "tools_required": "boolean",
      "structured_output_required": "boolean",
      "context_min": "int (minimum context window tokens, optional)",
      "modalities_in": ["text", "image", "audio"],
      "modalities_out": ["text", "image", "audio"],
      "provider_allowlist": ["openai", "anthropic", ...] (optional),
      "provider_blocklist": ["..."] (optional),
      "model_denylist": ["model-name", ...] (optional),
      "reasoning_tier_pref": "int 1-5 (1=best, optional)",
      "creative_tier_pref": "int 1-5 (1=best, optional)",
      "notes": "string (optional context)"
    }
  ]
}
"""


def build_interpretation_prompt(spec: ProjectSpec) -> str:
    """
    Build prompt for LLM to interpret ProjectSpec into RoleNeeds.
    
    Args:
        spec: ProjectSpec to interpret
        
    Returns:
        Prompt string
    """
    # Build roles section
    roles_text = []
    for role_id, role_spec in spec.roles.items():
        prefs = role_spec.preferences
        
        role_desc = f"""
Role: {role_id}
Kind: {role_spec.kind}
Description: {role_spec.description}
"""
        
        if prefs:
            if prefs.quality:
                role_desc += f"Quality preference: {prefs.quality}\n"
            if prefs.cost:
                role_desc += f"Cost preference: {prefs.cost}\n"
            if prefs.latency:
                role_desc += f"Latency preference: {prefs.latency}\n"
            if prefs.providers:
                role_desc += f"Preferred providers: {', '.join(prefs.providers)}\n"
            if prefs.provider_blocklist:
                role_desc += f"Blocked providers: {', '.join(prefs.provider_blocklist)}\n"
            if prefs.model_denylist:
                role_desc += f"Denied models: {', '.join(prefs.model_denylist)}\n"
        
        if role_spec.force_provider:
            role_desc += f"Forced provider: {role_spec.force_provider}\n"
        if role_spec.force_model:
            role_desc += f"Forced model: {role_spec.force_model}\n"
        
        roles_text.append(role_desc.strip())
    
    # Build default preferences section
    defaults_text = ""
    if spec.defaults:
        defaults_text = "\nDefault Preferences:\n"
        if spec.defaults.providers:
            defaults_text += f"- Preferred providers: {', '.join(spec.defaults.providers)}\n"
        if spec.defaults.quality:
            defaults_text += f"- Quality: {spec.defaults.quality}\n"
        if spec.defaults.cost:
            defaults_text += f"- Cost: {spec.defaults.cost}\n"
        if spec.defaults.latency:
            defaults_text += f"- Latency: {spec.defaults.latency}\n"
    
    prompt = f"""Convert the following LLM project specification into structured role requirements.

Project: {spec.project}
Environment: {spec.env}
{defaults_text}

Roles:
{chr(10).join(roles_text)}

Instructions:
1. For each role, determine the task characteristics and requirements
2. Convert preference levels (low/medium/high) to numeric biases:
   - low: 0.2-0.4
   - medium: 0.4-0.6
   - high: 0.6-0.8
3. Infer boolean requirements (reasoning, tools, structured output) from the description
4. Estimate minimum context window if description mentions large inputs
5. Apply default preferences where role-specific preferences are missing
6. Set importance based on role description (critical for production, high for important, medium default)

Output JSON matching this schema:
{ROLE_NEED_SCHEMA}

Ensure all roles are included and all required fields are populated.
"""
    
    return prompt
