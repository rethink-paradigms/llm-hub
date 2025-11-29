"""
SP6 - Weights: Weight calculation logic.

Derives scoring weights from RoleNeed biases and preferences.
"""
from llmhub.generator.sp3_needs_schema import RoleNeed
from .models import Weights


def derive_weights(role: RoleNeed) -> Weights:
    """
    Derive scoring weights from role need.
    
    Args:
        role: RoleNeed with biases and preferences
        
    Returns:
        Normalized Weights for scoring
    """
    # Start with biases directly from role
    raw_weights = {
        "w_quality": role.quality_bias,
        "w_cost": role.cost_bias,
        "w_reasoning": 0.0,
        "w_creative": 0.0,
        "w_context": 0.0,
        "w_freshness": 0.0,
    }
    
    # Adjust based on task kind
    task = role.task_kind.lower()
    if "reasoning" in task or "analysis" in task:
        raw_weights["w_reasoning"] = 0.3
        raw_weights["w_quality"] += 0.2
    elif "creative" in task or "writing" in task:
        raw_weights["w_creative"] = 0.3
    elif "factual" in task or "retrieval" in task:
        raw_weights["w_freshness"] = 0.2
    
    # Adjust based on importance
    importance_boost = {
        "low": 0.0,
        "medium": 0.1,
        "high": 0.2,
        "critical": 0.3,
    }
    quality_boost = importance_boost.get(role.importance, 0.1)
    raw_weights["w_quality"] += quality_boost
    
    # If tier preferences specified, boost corresponding weights
    if role.reasoning_tier_pref:
        raw_weights["w_reasoning"] = max(raw_weights["w_reasoning"], 0.25)
    if role.creative_tier_pref:
        raw_weights["w_creative"] = max(raw_weights["w_creative"], 0.25)
    
    # If context requirement specified, boost context weight
    if role.context_min:
        raw_weights["w_context"] = 0.15
    
    # Reduce cost weight if latency sensitivity is high
    if role.latency_sensitivity > 0.7:
        raw_weights["w_cost"] *= 0.5
    
    # Normalize to sum to 1.0
    total = sum(raw_weights.values())
    if total > 0:
        normalized = {k: v / total for k, v in raw_weights.items()}
    else:
        # Fallback: equal weights
        normalized = {k: 1.0 / 6 for k in raw_weights.keys()}
    
    return Weights(**normalized)
