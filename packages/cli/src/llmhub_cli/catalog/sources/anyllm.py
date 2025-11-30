"""
AnyLLM source: discover models that are actually callable via any-llm.

This module introspects the any-llm configuration to determine which models
are available given the current environment and API keys.
"""
from typing import Optional
from ..schema import AnyLLMModel


def load_anyllm_models() -> list[AnyLLMModel]:
    """
    Discover all models that are callable via any-llm given local environment.
    
    Returns:
        List of AnyLLMModel instances representing available models.
    """
    models: list[AnyLLMModel] = []
    
    try:
        # Try to import any-llm
        from any_llm import list_models
        
        # Try common providers
        # any-llm will only return models if the API key is valid
        common_providers = ["openai", "anthropic", "google", "mistral", "deepseek", "qwen", "groq", "together", "cohere", "ollama"]
        
        for provider in common_providers:
            try:
                provider_models = list_models(provider=provider)
                for model_obj in provider_models:
                    # Extract model ID from the Model object
                    model_id = model_obj.id if hasattr(model_obj, 'id') else str(model_obj)
                    models.append(AnyLLMModel(
                        provider=provider,
                        model_id=model_id
                    ))
            except Exception as e:
                # Provider not available, no API key, or API key invalid
                # This is expected for providers that aren't configured
                continue
                    
    except ImportError:
        # any-llm not installed or not available
        # Return empty list - catalog will still build but with no models
        pass
    
    return models
