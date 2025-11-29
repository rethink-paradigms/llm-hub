"""
Models.dev source: fetch and normalize model metadata from models.dev/api.json.

This module provides pricing, limits, modalities, and capability flags.
"""
import requests
from typing import Optional
from .schema import ModelsDevModel


def fetch_modelsdev_json() -> dict:
    """
    HTTP GET models.dev/api.json and return parsed dict.
    
    Returns:
        Parsed JSON response as dict.
        
    Raises:
        requests.RequestException: If the request fails.
    """
    url = "https://models.dev/api.json"
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        # Log warning but don't crash - catalog can build without models.dev data
        print(f"Warning: Failed to fetch models.dev data: {e}")
        return {}


def normalize_modelsdev(data: dict) -> dict[str, ModelsDevModel]:
    """
    Flatten provider → models into dict keyed by canonical ID.
    
    Args:
        data: Raw JSON from models.dev/api.json
        
    Returns:
        Dict mapping canonical_id (e.g. "openai/gpt-4o-mini") to ModelsDevModel
    """
    normalized: dict[str, ModelsDevModel] = {}
    
    if not data:
        return normalized
    
    # models.dev structure is typically: { providers: { provider_name: { models: [...] } } }
    providers = data.get("providers", {})
    
    for provider_name, provider_data in providers.items():
        models = provider_data.get("models", [])
        
        for model_data in models:
            model_id = model_data.get("id", model_data.get("name", ""))
            if not model_id:
                continue
            
            canonical_id = f"{provider_name}/{model_id}"
            
            # Parse capabilities
            capabilities = model_data.get("capabilities", {})
            modalities = model_data.get("modalities", {})
            
            # Parse pricing
            pricing = model_data.get("pricing", {})
            price_input = None
            price_output = None
            price_reasoning = None
            
            if pricing:
                # Pricing might be in various formats - normalize to per million
                input_price_data = pricing.get("input", pricing.get("prompt"))
                output_price_data = pricing.get("output", pricing.get("completion"))
                
                if isinstance(input_price_data, (int, float)):
                    price_input = float(input_price_data)
                elif isinstance(input_price_data, dict):
                    price_input = float(input_price_data.get("price", 0))
                
                if isinstance(output_price_data, (int, float)):
                    price_output = float(output_price_data)
                elif isinstance(output_price_data, dict):
                    price_output = float(output_price_data.get("price", 0))
                
                # Reasoning pricing if available
                reasoning_price_data = pricing.get("reasoning")
                if isinstance(reasoning_price_data, (int, float)):
                    price_reasoning = float(reasoning_price_data)
                elif isinstance(reasoning_price_data, dict):
                    price_reasoning = float(reasoning_price_data.get("price", 0))
            
            # Parse limits
            limits = model_data.get("limits", {})
            context_tokens = limits.get("context", limits.get("context_length"))
            max_input = limits.get("max_input", limits.get("max_input_tokens"))
            max_output = limits.get("max_output", limits.get("max_output_tokens"))
            
            # Parse input/output modalities
            input_mods = modalities.get("input", ["text"])
            output_mods = modalities.get("output", ["text"])
            
            # Ensure lists
            if not isinstance(input_mods, list):
                input_mods = [input_mods] if input_mods else ["text"]
            if not isinstance(output_mods, list):
                output_mods = [output_mods] if output_mods else ["text"]
            
            normalized[canonical_id] = ModelsDevModel(
                canonical_id=canonical_id,
                provider=provider_name,
                model_id=model_id,
                family=model_data.get("family"),
                display_name=model_data.get("display_name", model_data.get("name")),
                
                # Capabilities
                supports_reasoning=capabilities.get("reasoning", False),
                supports_tool_call=capabilities.get("tools", capabilities.get("function_calling", False)),
                supports_structured_output=capabilities.get("structured_output", False),
                input_modalities=input_mods,
                output_modalities=output_mods,
                attachments=model_data.get("attachments", []),
                
                # Limits
                context_tokens=context_tokens,
                max_input_tokens=max_input,
                max_output_tokens=max_output,
                
                # Pricing
                price_input_per_million=price_input,
                price_output_per_million=price_output,
                price_reasoning_per_million=price_reasoning,
                
                # Meta
                knowledge_cutoff=model_data.get("knowledge_cutoff"),
                release_date=model_data.get("release_date"),
                last_updated=model_data.get("last_updated"),
                open_weights=model_data.get("open_weights", model_data.get("open_source", False))
            )
    
    return normalized
