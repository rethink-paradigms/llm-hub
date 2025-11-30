"""
SP4 - Catalog View: Catalog loader.

Provides function to load catalog as list of CanonicalModel objects.
"""
from typing import Optional, List
from llmhub_cli.catalog.schema import CanonicalModel
from llmhub_cli.catalog.builder import build_catalog
from .errors import CatalogViewError


def load_catalog_view(
    ttl_hours: int = 24,
    force_refresh: bool = False,
    catalog_override: Optional[List[CanonicalModel]] = None
) -> List[CanonicalModel]:
    """
    Load catalog as list of CanonicalModel objects.
    
    Args:
        ttl_hours: Cache TTL in hours (default 24)
        force_refresh: Force rebuild of catalog (default False)
        catalog_override: Optional override for testing (default None)
        
    Returns:
        List of CanonicalModel instances
        
    Raises:
        CatalogViewError: If catalog loading fails
    """
    # If override provided (for testing), use it directly
    if catalog_override is not None:
        return catalog_override
    
    try:
        # Load catalog using catalog module
        catalog = build_catalog(ttl_hours=ttl_hours, force_refresh=force_refresh)
        return catalog.models
        
    except Exception as e:
        raise CatalogViewError(f"Failed to load catalog: {str(e)}") from e
