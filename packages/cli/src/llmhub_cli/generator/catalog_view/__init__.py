"""
SP4 - Catalog View: Load catalog for generator.

Exports:
    - CanonicalModel (re-exported from catalog.schema)
    - load_catalog_view (function)
    - CatalogViewError (exception)
"""
from llmhub_cli.catalog.schema import CanonicalModel
from .loader import load_catalog_view
from .errors import CatalogViewError

__all__ = [
    "CanonicalModel",
    "load_catalog_view",
    "CatalogViewError",
]
