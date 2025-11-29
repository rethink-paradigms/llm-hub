"""
Mapper: align IDs between any-llm, models.dev, and arena-catalog.

This module resolves naming differences and produces fused raw records
combining data from all sources.
"""
import json
from pathlib import Path
from typing import Optional
from .schema import AnyLLMModel, ModelsDevModel, ArenaModel, FusedRaw


def load_overrides() -> dict:
    """Load static ID overrides from data/overrides.json."""
    overrides_path = Path(__file__).parent / "data" / "overrides.json"
    
    if not overrides_path.exists():
        return {"id_mappings": {}, "model_families": {}}
    
    try:
        with open(overrides_path, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {"id_mappings": {}, "model_families": {}}


def _normalize_model_name(name: str) -> str:
    """Normalize model name for fuzzy matching."""
    return name.lower().replace("-", "").replace("_", "").replace(" ", "")


def fuse_sources(
    anyllm_models: list[AnyLLMModel],
    modelsdev_map: dict[str, ModelsDevModel],
    arena_map: dict[str, ArenaModel],
    overrides: dict
) -> list[FusedRaw]:
    """
    Fuse data from all sources using ID alignment and overrides.
    
    Args:
        anyllm_models: List of models discovered from any-llm
        modelsdev_map: Dict of models.dev data keyed by canonical_id
        arena_map: Dict of arena data keyed by arena_id
        overrides: Override mappings from overrides.json
        
    Returns:
        List of FusedRaw records combining all sources.
    """
    fused_records: list[FusedRaw] = []
    id_mappings = overrides.get("id_mappings", {})
    
    for anyllm_model in anyllm_models:
        # Build canonical_id from any-llm model
        canonical_id = f"{anyllm_model.provider}/{anyllm_model.model_id}"
        
        # Look up models.dev data
        modelsdev_model: Optional[ModelsDevModel] = None
        
        # 1. Try direct match
        modelsdev_model = modelsdev_map.get(canonical_id)
        
        # 2. Try override mapping
        if not modelsdev_model and canonical_id in id_mappings:
            override = id_mappings[canonical_id]
            modelsdev_id = override.get("modelsdev_id")
            if modelsdev_id:
                modelsdev_model = modelsdev_map.get(modelsdev_id)
        
        # 3. Try fuzzy match on model_id
        if not modelsdev_model:
            normalized_model_id = _normalize_model_name(anyllm_model.model_id)
            for dev_id, dev_model in modelsdev_map.items():
                if dev_model.provider == anyllm_model.provider:
                    if _normalize_model_name(dev_model.model_id) == normalized_model_id:
                        modelsdev_model = dev_model
                        break
        
        # Look up arena data
        arena_model: Optional[ArenaModel] = None
        
        # 1. Try override mapping
        if canonical_id in id_mappings:
            override = id_mappings[canonical_id]
            arena_id = override.get("arena_id")
            if arena_id:
                arena_model = arena_map.get(arena_id)
        
        # 2. Try direct match with model_id
        if not arena_model:
            arena_model = arena_map.get(anyllm_model.model_id)
        
        # 3. Try canonical_id as arena_id
        if not arena_model:
            arena_model = arena_map.get(canonical_id)
        
        # 4. Try fuzzy match
        if not arena_model:
            normalized_model_id = _normalize_model_name(anyllm_model.model_id)
            for arena_id, arena_data in arena_map.items():
                if _normalize_model_name(arena_id) == normalized_model_id:
                    arena_model = arena_data
                    break
        
        # Create fused record
        fused_records.append(FusedRaw(
            canonical_id=canonical_id,
            anyllm=anyllm_model,
            modelsdev=modelsdev_model,
            arena=arena_model
        ))
    
    return fused_records
