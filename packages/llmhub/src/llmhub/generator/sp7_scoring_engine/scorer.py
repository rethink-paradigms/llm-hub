"""
SP7 - Scoring Engine: Model scoring and ranking logic.

Computes weighted scores for models and ranks them.
"""
from typing import List, Tuple
from datetime import datetime
from llmhub.generator.sp3_needs_schema import RoleNeed
from llmhub.generator.sp6_weights import Weights
from llmhub.catalog.schema import CanonicalModel


def _normalize_tier(tier: int) -> float:
    """Normalize tier (1-5) to score (1.0-0.0), where 1 is best."""
    return (6 - tier) / 5.0


def _normalize_arena_score(score: float) -> float:
    """Normalize arena score (typically 1000-1400) to [0, 1]."""
    # Typical range: 1000-1400, but can vary
    min_score = 900.0
    max_score = 1500.0
    normalized = (score - min_score) / (max_score - min_score)
    return max(0.0, min(1.0, normalized))


def _compute_quality_score(model: CanonicalModel) -> float:
    """Compute normalized quality score."""
    tier_score = _normalize_tier(model.quality_tier)
    
    if model.arena_score:
        arena_norm = _normalize_arena_score(model.arena_score)
        # Weight: 60% tier, 40% arena
        return 0.6 * tier_score + 0.4 * arena_norm
    
    return tier_score


def _compute_cost_score(model: CanonicalModel) -> float:
    """Compute normalized cost score (lower cost = higher score)."""
    # cost_tier: 1=cheapest (best), 5=most expensive (worst)
    return _normalize_tier(model.cost_tier)


def _compute_reasoning_score(model: CanonicalModel) -> float:
    """Compute normalized reasoning score."""
    return _normalize_tier(model.reasoning_tier)


def _compute_creative_score(model: CanonicalModel) -> float:
    """Compute normalized creative score."""
    return _normalize_tier(model.creative_tier)


def _compute_context_score(model: CanonicalModel, role: RoleNeed) -> float:
    """Compute normalized context score."""
    if not model.context_tokens:
        return 0.5  # Unknown = medium
    
    # If role has context_min, score based on how much above minimum
    if role.context_min:
        if model.context_tokens < role.context_min:
            return 0.0  # Should have been filtered out
        excess = model.context_tokens - role.context_min
        # Normalize: 0-100k excess → 0.5-1.0
        normalized_excess = min(1.0, excess / 100000)
        return 0.5 + 0.5 * normalized_excess
    
    # Otherwise, more context is always better
    # Normalize: 0-200k → 0.0-1.0
    return min(1.0, model.context_tokens / 200000)


def _compute_freshness_score(model: CanonicalModel) -> float:
    """Compute normalized freshness score."""
    date_str = model.last_updated or model.release_date
    if not date_str:
        return 0.5  # Unknown = medium
    
    try:
        model_date = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        now = datetime.now(model_date.tzinfo) if model_date.tzinfo else datetime.now()
        age_days = (now - model_date).days
        
        # Normalize: 0 days = 1.0, 365 days = 0.5, 730+ days = 0.0
        if age_days <= 0:
            return 1.0
        elif age_days <= 365:
            return 1.0 - 0.5 * (age_days / 365)
        elif age_days <= 730:
            return 0.5 - 0.5 * ((age_days - 365) / 365)
        else:
            return 0.0
    except:
        return 0.5


def _compute_final_score(
    model: CanonicalModel,
    role: RoleNeed,
    weights: Weights
) -> float:
    """Compute weighted final score for a model."""
    quality_score = _compute_quality_score(model)
    cost_score = _compute_cost_score(model)
    reasoning_score = _compute_reasoning_score(model)
    creative_score = _compute_creative_score(model)
    context_score = _compute_context_score(model, role)
    freshness_score = _compute_freshness_score(model)
    
    final_score = (
        weights.w_quality * quality_score +
        weights.w_cost * cost_score +
        weights.w_reasoning * reasoning_score +
        weights.w_creative * creative_score +
        weights.w_context * context_score +
        weights.w_freshness * freshness_score
    )
    
    return final_score


def score_candidates(
    role: RoleNeed,
    weights: Weights,
    models: List[CanonicalModel]
) -> List[Tuple[CanonicalModel, float]]:
    """
    Score and rank models by weighted multi-factor scoring.
    
    Args:
        role: RoleNeed for context
        weights: Scoring weights
        models: Filtered candidate models
        
    Returns:
        List of (model, score) tuples, sorted descending by score
    """
    scored = []
    
    for model in models:
        score = _compute_final_score(model, role, weights)
        scored.append((model, score))
    
    # Sort by score descending, with tie-breaking
    def sort_key(item: Tuple[CanonicalModel, float]) -> Tuple[float, int, float, int, str]:
        model, score = item
        
        # Tie-breakers (negated for descending sort)
        in_allowlist = 1 if (role.provider_allowlist and model.provider in role.provider_allowlist) else 0
        arena = model.arena_score if model.arena_score else 0
        context = model.context_tokens if model.context_tokens else 0
        model_id = model.model_id
        
        return (
            -score,  # Primary: score descending
            -in_allowlist,  # Provider in allowlist
            -arena,  # Arena score descending
            -context,  # Context tokens descending
            model_id,  # Model ID ascending
        )
    
    scored.sort(key=sort_key)
    
    return scored
