from ..config.schema import OrchestratorConfig
from ..runtime.types import ResolvedLLMConfig
from ..utils.env import resolve_auth_key
from ..utils.errors import ConfigError

def resolve_llm_config(config: OrchestratorConfig, role: str) -> ResolvedLLMConfig:
    """
    Resolves a logical role to a concrete LLM configuration.
    """
    # 1. Find role binding
    role_binding = config.roles.get(role)
    if not role_binding:
        raise ConfigError(f"Role not defined in config: {role}")
    
    # 2. Find provider config
    provider_name = role_binding.provider
    provider_config = config.providers.get(provider_name)
    if not provider_config:
        raise ConfigError(f"Provider not defined in config: {provider_name} (referenced by role {role})")
    
    # 3. Resolve API key
    api_key = resolve_auth_key(provider_config.auth_profile)
    
    # 4. Build resolved config
    return ResolvedLLMConfig(
        provider=provider_name,
        model=role_binding.model,
        api_key=api_key,
        api_base=provider_config.api_base
    )
