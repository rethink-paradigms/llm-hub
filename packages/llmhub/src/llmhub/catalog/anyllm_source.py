"""
AnyLLM source: discover models that are actually callable via any-llm.

This module introspects the any-llm configuration to determine which models
are available given the current environment and API keys.
"""
from typing import Optional
from .schema import AnyLLMModel


def load_anyllm_models() -> list[AnyLLMModel]:
    """
    Discover all models that are callable via any-llm given local environment.
    
    Returns:
        List of AnyLLMModel instances representing available models.
    """
    models: list[AnyLLMModel] = []
    
    try:
        # Try to import any-llm
        import any_llm
        from any_llm import get_all_models, get_available_providers
        
        # Get available providers (those with API keys configured)
        try:
            providers = get_available_providers()
        except Exception:
            # Fallback: try to get all providers and filter later
            providers = []
        
        # For each provider, get models
        if not providers:
            # If we can't get providers, try common ones
            common_providers = ["openai", "anthropic", "google", "mistral", "deepseek", "qwen"]
            for provider in common_providers:
                try:
                    provider_models = get_all_models(provider=provider)
                    for model_id in provider_models:
                        models.append(AnyLLMModel(
                            provider=provider,
                            model_id=model_id
                        ))
                except Exception:
                    # Provider not available or no API key
                    continue
        else:
            # Get models from available providers
            for provider in providers:
                try:
                    provider_models = get_all_models(provider=provider)
                    for model_id in provider_models:
                        models.append(AnyLLMModel(
                            provider=provider,
                            model_id=model_id
                        ))
                except Exception:
                    continue
                    
    except ImportError:
        # any-llm not installed or not available
        # Return empty list - catalog will still build but with no models
        pass
    
    return models
