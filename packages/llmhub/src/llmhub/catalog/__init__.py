"""
Catalog: local model catalog with cost/quality/capability metadata.

Public API for building and accessing the catalog of available models.
"""
from .schema import Catalog, CanonicalModel
from .builder import build_catalog
from .cache import load_cached_catalog, clear_cache

__all__ = [
    "Catalog",
    "CanonicalModel",
    "build_catalog",
    "load_cached_catalog",
    "clear_cache",
]
