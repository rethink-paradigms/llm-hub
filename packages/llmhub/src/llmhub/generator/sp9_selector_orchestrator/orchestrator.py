"""
SP9 - Selector Orchestrator: Main selection orchestration logic.

Coordinates all selection subproblems to select models for a role.
"""
from typing import List
from llmhub.generator.sp3_needs_schema import RoleNeed
from llmhub.catalog.schema import CanonicalModel
from llmhub.generator.sp5_filter_candidates import filter_candidates
from llmhub.generator.sp6_weights import derive_weights
from llmhub.generator.sp7_scoring_engine import score_candidates
from llmhub.generator.sp8_relaxation_engine import relax_and_select
from .models import SelectionResult, SelectorOptions


def select_for_role(
    role: RoleNeed,
    models: List[CanonicalModel],
    options: SelectorOptions = SelectorOptions()
) -> SelectionResult:
    """
    Select model(s) for a role need.
    
    Args:
        role: RoleNeed with constraints and preferences
        models: Full catalog of models
        options: Selection options
        
    Returns:
        SelectionResult with primary, backups, and rationale
    """
    # Step 1: Derive weights from role
    weights = derive_weights(role)
    
    # Step 2: Filter candidates
    filtered = filter_candidates(role, models)
    
    # Step 3: Score or relax
    relaxations = []
    if filtered:
        # Score and rank
        scored = score_candidates(role, weights, filtered)
    else:
        # Apply relaxation
        scored, relaxations = relax_and_select(role, models, weights)
    
    # Step 4: Select primary and backups
    primary = None
    primary_provider = None
    primary_model = None
    primary_score = None
    backups = []
    
    if scored:
        # Primary is top-ranked
        primary_candidate, primary_score = scored[0]
        primary = primary_candidate.canonical_id
        primary_provider = primary_candidate.provider
        primary_model = primary_candidate.model_id
        
        # Backups are next N
        for model, _ in scored[1:options.num_backups + 1]:
            backups.append(model.canonical_id)
    elif options.require_primary:
        # No candidates found even after relaxation
        rationale = "No suitable models found even after applying all relaxations"
        return SelectionResult(
            role_id=role.id,
            rationale=rationale,
            relaxations_applied=relaxations
        )
    
    # Step 5: Generate rationale
    rationale_parts = []
    
    if primary:
        rationale_parts.append(f"Selected {primary} (score: {primary_score:.3f})")
        
        if relaxations:
            rationale_parts.append(f"Applied {len(relaxations)} relaxation(s)")
        
        # Top factors
        factors = []
        if weights.w_quality > 0.2:
            factors.append(f"quality ({weights.w_quality:.1%})")
        if weights.w_cost > 0.2:
            factors.append(f"cost ({weights.w_cost:.1%})")
        if weights.w_reasoning > 0.2:
            factors.append(f"reasoning ({weights.w_reasoning:.1%})")
        
        if factors:
            rationale_parts.append(f"Top factors: {', '.join(factors)}")
        
        if backups:
            rationale_parts.append(f"{len(backups)} backup(s) available")
    
    rationale = ". ".join(rationale_parts)
    
    return SelectionResult(
        role_id=role.id,
        primary=primary,
        primary_provider=primary_provider,
        primary_model=primary_model,
        primary_score=primary_score,
        backups=backups,
        rationale=rationale,
        relaxations_applied=relaxations
    )
