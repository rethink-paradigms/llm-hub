"""
SP8 - Relaxation Engine: Constraint relaxation logic.

Systematically relaxes constraints to find candidates.
"""
from typing import List, Tuple
from copy import deepcopy
from llmhub_cli.generator.needs import RoleNeed
from llmhub_cli.generator.selection.weights_models import Weights
from llmhub_cli.catalog.schema import CanonicalModel
from llmhub_cli.generator.selection.filter import filter_candidates
from llmhub_cli.generator.selection.scorer import score_candidates


def relax_and_select(
    role: RoleNeed,
    models: List[CanonicalModel],
    weights: Weights
) -> Tuple[List[Tuple[CanonicalModel, float]], List[str]]:
    """
    Systematically relax constraints until candidates are found.
    
    Args:
        role: RoleNeed with constraints
        models: Full catalog
        weights: Scoring weights
        
    Returns:
        Tuple of (scored_candidates, relaxations_applied)
    """
    relaxations = []
    relaxed_role = deepcopy(role)
    
    # Relaxation Step 1: Remove provider allowlist
    if relaxed_role.provider_allowlist:
        relaxed_role.provider_allowlist = None
        relaxations.append("Removed provider allowlist")
        
        filtered = filter_candidates(relaxed_role, models)
        if filtered:
            scored = score_candidates(relaxed_role, weights, filtered)
            return scored, relaxations
    
    # Relaxation Step 2: Lower context_min by 25%
    if relaxed_role.context_min:
        original_context = relaxed_role.context_min
        relaxed_role.context_min = int(relaxed_role.context_min * 0.75)
        relaxations.append(f"Lowered context requirement from {original_context} to {relaxed_role.context_min}")
        
        filtered = filter_candidates(relaxed_role, models)
        if filtered:
            scored = score_candidates(relaxed_role, weights, filtered)
            return scored, relaxations
    
    # Relaxation Step 3: Turn structured_output_required into preference
    if relaxed_role.structured_output_required:
        relaxed_role.structured_output_required = False
        relaxations.append("Made structured output optional")
        
        filtered = filter_candidates(relaxed_role, models)
        if filtered:
            scored = score_candidates(relaxed_role, weights, filtered)
            return scored, relaxations
    
    # Relaxation Step 4: Turn reasoning_required into preference
    if relaxed_role.reasoning_required:
        relaxed_role.reasoning_required = False
        relaxations.append("Made reasoning optional")
        
        filtered = filter_candidates(relaxed_role, models)
        if filtered:
            scored = score_candidates(relaxed_role, weights, filtered)
            return scored, relaxations
    
    # Relaxation Step 5: Turn tools_required into preference
    if relaxed_role.tools_required:
        relaxed_role.tools_required = False
        relaxations.append("Made tools optional")
        
        filtered = filter_candidates(relaxed_role, models)
        if filtered:
            scored = score_candidates(relaxed_role, weights, filtered)
            return scored, relaxations
    
    # If still no candidates, return empty with all relaxations attempted
    return [], relaxations
