from typing import Optional
from pydantic import BaseModel, Field
from llmhub_runtime.models import (
    RuntimeConfig,
    ProviderConfig,
    RoleConfig,
    RoleDefaultsConfig,
    LLMMode
)
from .spec_models import SpecConfig, RoleKind


class GeneratorOptions(BaseModel):
    """Options for runtime generation."""
    no_llm: bool = False
    explain: bool = False


class GenerationResult(BaseModel):
    """Result of runtime generation."""
    runtime: RuntimeConfig
    explanations: dict[str, str] = Field(default_factory=dict)


def _map_kind_to_mode(kind: RoleKind) -> LLMMode:
    """Map spec RoleKind to runtime LLMMode."""
    mapping = {
        RoleKind.chat: LLMMode.chat,
        RoleKind.embedding: LLMMode.embedding,
        RoleKind.image: LLMMode.image,
        RoleKind.audio: LLMMode.audio,
        RoleKind.tool: LLMMode.tool,
        RoleKind.other: LLMMode.other,
    }
    return mapping.get(kind, LLMMode.other)


def _select_model_stub(spec: SpecConfig, role_name: str) -> tuple[str, str, dict]:
    """
    Stub model selection logic.
    Returns (provider, model, params) tuple.
    
    This is a simple deterministic implementation for v0.
    In production, this would use sophisticated model selection logic.
    """
    role_spec = spec.roles[role_name]
    
    # Check for forced provider/model
    if role_spec.force_provider and role_spec.force_model:
        return role_spec.force_provider, role_spec.force_model, role_spec.mode_params
    
    # Get preferred providers
    preferred_providers = role_spec.preferences.providers or []
    if not preferred_providers and spec.defaults:
        preferred_providers = spec.defaults.providers
    
    # Find first enabled provider from preferences
    provider = None
    for pref_provider in preferred_providers:
        if pref_provider in spec.providers and spec.providers[pref_provider].enabled:
            provider = pref_provider
            break
    
    # Fallback to first enabled provider
    if not provider:
        for p, config in spec.providers.items():
            if config.enabled:
                provider = p
                break
    
    if not provider:
        provider = "openai"  # Ultimate fallback
    
    # Simple model selection based on role kind and preferences
    model = None
    params = {**role_spec.mode_params}
    
    if role_spec.kind == RoleKind.chat:
        # Chat models
        if role_spec.preferences.quality == "high":
            if provider == "openai":
                model = "gpt-4"
                params.setdefault("temperature", 0.7)
                params.setdefault("max_tokens", 2048)
            elif provider == "anthropic":
                model = "claude-3-5-sonnet-20241022"
                params.setdefault("temperature", 0.7)
                params.setdefault("max_tokens", 2048)
            else:
                model = "gpt-4"
        elif role_spec.preferences.cost == "low":
            if provider == "openai":
                model = "gpt-4o-mini"
                params.setdefault("temperature", 0.3)
                params.setdefault("max_tokens", 1024)
            elif provider == "anthropic":
                model = "claude-3-haiku-20240307"
                params.setdefault("temperature", 0.3)
                params.setdefault("max_tokens", 1024)
            else:
                model = "gpt-4o-mini"
        else:
            # Default chat model
            if provider == "openai":
                model = "gpt-4o-mini"
            elif provider == "anthropic":
                model = "claude-3-5-sonnet-20241022"
            else:
                model = "gpt-4o-mini"
            params.setdefault("temperature", 0.5)
            params.setdefault("max_tokens", 1024)
    
    elif role_spec.kind == RoleKind.embedding:
        # Embedding models
        if provider == "openai":
            model = "text-embedding-3-small"
        elif provider == "anthropic":
            model = "text-embedding-3-small"  # Fallback to OpenAI
            provider = "openai"
        else:
            model = "text-embedding-3-small"
        params = {}
    
    else:
        # Other modes - use generic model
        model = "gpt-4o-mini"
        params.setdefault("temperature", 0.5)
    
    return provider, model, params


def generate_runtime(
    spec: SpecConfig,
    options: Optional[GeneratorOptions] = None
) -> GenerationResult:
    """
    Generate runtime configuration from spec.
    
    This is a stub implementation that uses simple heuristics.
    In production, this would use sophisticated model selection,
    potentially calling LLMs for recommendations.
    
    Args:
        spec: SpecConfig to convert.
        options: Optional generation options.
    
    Returns:
        GenerationResult with RuntimeConfig and explanations.
    """
    if options is None:
        options = GeneratorOptions()
    
    explanations = {}
    
    # Convert providers
    runtime_providers = {}
    for provider_name, provider_config in spec.providers.items():
        if provider_config.enabled:
            runtime_providers[provider_name] = ProviderConfig(
                env_key=provider_config.env_key
            )
    
    # Convert roles
    runtime_roles = {}
    for role_name, role_spec in spec.roles.items():
        provider, model, params = _select_model_stub(spec, role_name)
        mode = _map_kind_to_mode(role_spec.kind)
        
        runtime_roles[role_name] = RoleConfig(
            provider=provider,
            model=model,
            mode=mode,
            params=params
        )
        
        if options.explain:
            explanations[role_name] = (
                f"Selected {provider}:{model} based on kind={role_spec.kind}, "
                f"cost={role_spec.preferences.cost}, "
                f"quality={role_spec.preferences.quality}"
            )
    
    # Convert defaults if present
    runtime_defaults = None
    if spec.defaults and spec.defaults.providers:
        # Use first default provider
        default_provider = spec.defaults.providers[0]
        runtime_defaults = RoleDefaultsConfig(
            provider=default_provider,
            model="gpt-4o-mini",
            mode=LLMMode.chat,
            params={"temperature": 0.3, "max_tokens": 1024}
        )
    
    runtime = RuntimeConfig(
        project=spec.project,
        env=spec.env,
        providers=runtime_providers,
        roles=runtime_roles,
        defaults=runtime_defaults
    )
    
    return GenerationResult(runtime=runtime, explanations=explanations)
