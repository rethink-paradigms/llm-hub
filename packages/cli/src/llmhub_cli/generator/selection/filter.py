"""
SP5 - Filter Candidates: Filtering logic.

Applies hard constraints from RoleNeed to filter catalog models.
"""
from typing import List
from llmhub_cli.generator.needs import RoleNeed
from llmhub_cli.catalog.schema import CanonicalModel


def filter_candidates(
    role: RoleNeed,
    models: List[CanonicalModel]
) -> List[CanonicalModel]:
    """
    Filter models by hard constraints from role need.
    
    Args:
        role: RoleNeed with constraints
        models: Full list of models from catalog
        
    Returns:
        Filtered list of candidate models
    """
    candidates = []
    
    for model in models:
        # Check provider allowlist
        if role.provider_allowlist and model.provider not in role.provider_allowlist:
            continue
        
        # Check provider blocklist
        if role.provider_blocklist and model.provider in role.provider_blocklist:
            continue
        
        # Check model denylist
        if role.model_denylist:
            # Check both canonical_id and model_id
            if model.canonical_id in role.model_denylist or model.model_id in role.model_denylist:
                continue
        
        # Check reasoning requirement
        if role.reasoning_required and not model.supports_reasoning:
            continue
        
        # Check tools requirement
        if role.tools_required and not model.supports_tool_call:
            continue
        
        # Check structured output requirement
        if role.structured_output_required and not model.supports_structured_output:
            continue
        
        # Check input modalities
        for modality in role.modalities_in:
            if modality not in model.input_modalities:
                break
        else:
            # Check output modalities (only if input modalities passed)
            for modality in role.modalities_out:
                if modality not in model.output_modalities:
                    break
            else:
                # Check context requirement
                if role.context_min is not None:
                    if model.context_tokens is None or model.context_tokens < role.context_min:
                        continue
                
                # All constraints passed
                candidates.append(model)
    
    return candidates
