"""
Catalog: local model catalog with cost/quality/capability metadata.

Public API for building and accessing the catalog of available models.
"""
from typing import Optional, List
from .schema import Catalog, CanonicalModel
from .builder import build_catalog
from .cache import load_cached_catalog, clear_cache


def get_catalog(
    ttl_hours: int = 24,
    force_refresh: bool = False,
    provider: Optional[str] = None,
    tags: Optional[List[str]] = None
) -> Catalog:
    """
    Get catalog with optional filtering by provider and tags.
    
    This is a convenience function that builds the catalog and applies
    filtering in one call. It's useful for quickly querying models that
    meet specific criteria without manually filtering the results.
    
    Args:
        ttl_hours: Cache TTL in hours, default 24
        force_refresh: If True, ignore cache and rebuild, default False
        provider: Optional provider name to filter by (e.g., "openai")
        tags: Optional list of tags to filter by (models must have all tags)
    
    Returns:
        Catalog object with filtered models (or all models if no filters)
    
    Example:
        >>> from llmhub_cli import get_catalog
        >>> 
        >>> # Get all models
        >>> catalog = get_catalog()
        >>> 
        >>> # Get all OpenAI models
        >>> openai_catalog = get_catalog(provider="openai")
        >>> print(f"Found {len(openai_catalog.models)} OpenAI models")
        >>> 
        >>> # Get models with reasoning capability
        >>> reasoning_catalog = get_catalog(tags=["reasoning"])
        >>> for model in reasoning_catalog.models:
        ...     print(f"{model.provider}:{model.model_id} - Tier {model.reasoning_tier}")
        >>> 
        >>> # Get OpenAI models with vision support
        >>> vision_catalog = get_catalog(provider="openai", tags=["vision"])
        >>> 
        >>> # Force fresh rebuild with filtering
        >>> fresh_catalog = get_catalog(force_refresh=True, provider="anthropic")
    
    See Also:
        - build_catalog: Build catalog without filtering
        - Catalog: The catalog model with .models attribute
        - CanonicalModel: Individual model schema
    """
    # Build the catalog
    catalog = build_catalog(ttl_hours=ttl_hours, force_refresh=force_refresh)
    
    # Apply filters if specified
    filtered_models = catalog.models
    
    if provider:
        filtered_models = [
            m for m in filtered_models 
            if m.provider.lower() == provider.lower()
        ]
    
    if tags:
        # Filter models that have all specified tags
        filtered_models = [
            m for m in filtered_models
            if all(tag in m.tags for tag in tags)
        ]
    
    # Return new Catalog with filtered models
    return Catalog(
        catalog_version=catalog.catalog_version,
        built_at=catalog.built_at,
        models=filtered_models
    )


__all__ = [
    "Catalog",
    "CanonicalModel",
    "build_catalog",
    "get_catalog",
    "load_cached_catalog",
    "clear_cache",
]
