# SP4 – Catalog View

## Purpose

Adapt the catalog module's snapshot into **CanonicalModel** objects for the selector. This subproblem provides a clean interface between the catalog system and the generator's selection logic.

## Inputs

- Catalog API: `llmhub.catalog.builder.build_catalog()` or cached catalog
- Optional catalog override for testing

## Outputs

- **List[CanonicalModel]**: List of models from catalog schema

## Public Interfaces

```python
def load_catalog_view(
    ttl_hours: int = 24,
    force_refresh: bool = False,
    catalog_override: Optional[list[CanonicalModel]] = None
) -> list[CanonicalModel]:
    """
    Load catalog as list of CanonicalModel objects.
    
    Args:
        ttl_hours: Cache TTL in hours
        force_refresh: Force rebuild of catalog
        catalog_override: Optional override for testing
        
    Returns:
        List of CanonicalModel instances
        
    Raises:
        CatalogViewError: If catalog loading fails
    """
```

## Invariants / Constraints

- **No HTTP calls**: Only uses existing catalog module
- **Graceful degradation**: Missing fields are defaulted safely
- **Caching respected**: Uses catalog's TTL unless force_refresh=True
- **Testing support**: Accepts override catalog for tests

## Non-goals

- Catalog building (handled by catalog module)
- Model filtering (handled by SP5)
- Scoring (handled by SP7)

## Implementation Notes

- Re-export CanonicalModel from catalog.schema
- Wrap catalog.builder.build_catalog() with error handling
- Support test injection via catalog_override parameter
