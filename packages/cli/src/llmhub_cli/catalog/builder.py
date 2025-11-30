"""
Builder: main build_catalog pipeline.

Coordinates source loading, fusion, global statistics, tier derivation,
and produces the final Catalog.
"""
from datetime import datetime
from typing import Optional
from pathlib import Path
import numpy as np
from pydantic import BaseModel
from dotenv import load_dotenv
from .schema import FusedRaw, CanonicalModel, Catalog
from .sources.anyllm import load_anyllm_models
from .sources.modelsdev import fetch_modelsdev_json, normalize_modelsdev
from .sources.arena import load_arena_models
from .mapper import load_overrides, fuse_sources
from . import cache as cache_module


class GlobalStats(BaseModel):
    """Global statistics for tier derivation."""
    # Price quantiles (for cost tiers)
    price_p20: float = 0.0
    price_p40: float = 0.0
    price_p60: float = 0.0
    price_p80: float = 0.0
    
    # Arena score quantiles (for quality tiers)
    arena_p20: float = 1000.0
    arena_p40: float = 1100.0
    arena_p60: float = 1200.0
    arena_p80: float = 1300.0


def _load_env_file() -> None:
    """
    Load .env file from common locations to populate environment variables.
    
    This function checks for .env files in:
    1. Current working directory
    2. Project root (by looking for llmhub.spec.yaml, .git, or pyproject.toml)
    3. Home directory
    
    The function loads the first .env file it finds and stops.
    This ensures API keys are available before any-llm tries to detect providers.
    """
    # Check current working directory first
    cwd_env = Path.cwd() / ".env"
    if cwd_env.exists():
        load_dotenv(cwd_env, override=False)
        return
    
    # Try to find project root and check there
    current = Path.cwd()
    for path in [current] + list(current.parents):
        # Check for project markers
        if (path / "llmhub.spec.yaml").exists() or (path / ".git").exists() or (path / "pyproject.toml").exists():
            env_path = path / ".env"
            if env_path.exists():
                load_dotenv(env_path, override=False)
                return
    
    # Finally check home directory
    home_env = Path.home() / ".env"
    if home_env.exists():
        load_dotenv(home_env, override=False)


def _compute_global_stats(fused: list[FusedRaw]) -> GlobalStats:
    """
    Compute price and arena-score quantiles for tier bucketing.
    
    Args:
        fused: List of fused raw records
        
    Returns:
        GlobalStats with quantiles for tier derivation
    """
    # Collect prices (average of input/output)
    prices = []
    for f in fused:
        if f.modelsdev and f.modelsdev.price_input_per_million and f.modelsdev.price_output_per_million:
            avg_price = (f.modelsdev.price_input_per_million + f.modelsdev.price_output_per_million) / 2
            prices.append(avg_price)
    
    # Collect arena scores
    arena_scores = []
    for f in fused:
        if f.arena and f.arena.rating:
            arena_scores.append(f.arena.rating)
    
    stats = GlobalStats()
    
    # Compute price quantiles if we have data
    if prices:
        prices_array = np.array(prices)
        stats.price_p20 = float(np.percentile(prices_array, 20))
        stats.price_p40 = float(np.percentile(prices_array, 40))
        stats.price_p60 = float(np.percentile(prices_array, 60))
        stats.price_p80 = float(np.percentile(prices_array, 80))
    
    # Compute arena score quantiles if we have data
    if arena_scores:
        arena_array = np.array(arena_scores)
        stats.arena_p20 = float(np.percentile(arena_array, 20))
        stats.arena_p40 = float(np.percentile(arena_array, 40))
        stats.arena_p60 = float(np.percentile(arena_array, 60))
        stats.arena_p80 = float(np.percentile(arena_array, 80))
    
    return stats


def _derive_cost_tier(avg_price: Optional[float], stats: GlobalStats) -> int:
    """Derive cost tier from price (1=cheapest, 5=most expensive)."""
    if avg_price is None:
        return 3  # Default to medium
    
    # Lower price = lower tier number = better
    if avg_price <= stats.price_p20:
        return 1
    elif avg_price <= stats.price_p40:
        return 2
    elif avg_price <= stats.price_p60:
        return 3
    elif avg_price <= stats.price_p80:
        return 4
    else:
        return 5


def _derive_quality_tier(arena_score: Optional[float], provider: str, stats: GlobalStats) -> int:
    """Derive quality tier from arena score (1=best, 5=worst)."""
    if arena_score is not None:
        # Higher arena score = lower tier number = better quality
        if arena_score >= stats.arena_p80:
            return 1
        elif arena_score >= stats.arena_p60:
            return 2
        elif arena_score >= stats.arena_p40:
            return 3
        elif arena_score >= stats.arena_p20:
            return 4
        else:
            return 5
    
    # Fallback based on provider reputation
    provider_tiers = {
        "openai": 2,
        "anthropic": 1,
        "google": 2,
        "deepseek": 3,
        "mistral": 3,
        "qwen": 3,
    }
    return provider_tiers.get(provider.lower(), 3)


def _derive_tags(f: FusedRaw) -> list[str]:
    """Derive tags from model capabilities and metadata."""
    tags = []
    
    if f.modelsdev:
        if f.modelsdev.supports_reasoning:
            tags.append("reasoning")
        if f.modelsdev.supports_tool_call:
            tags.append("tools")
        if f.modelsdev.supports_structured_output:
            tags.append("structured-output")
        if f.modelsdev.open_weights:
            tags.append("open-weights")
        
        # Modality tags
        if "image" in f.modelsdev.input_modalities:
            tags.append("vision")
        if "audio" in f.modelsdev.input_modalities:
            tags.append("audio-input")
        if "image" in f.modelsdev.output_modalities:
            tags.append("image-gen")
    
    return tags


def _derive_canonical(f: FusedRaw, stats: GlobalStats, overrides: dict) -> CanonicalModel:
    """
    Derive a CanonicalModel from a FusedRaw record.
    
    Args:
        f: Fused raw record
        stats: Global statistics for tier derivation
        overrides: Override data including model families
        
    Returns:
        CanonicalModel with all fields populated
    """
    # Basic identity
    provider = f.anyllm.provider
    model_id = f.anyllm.model_id
    canonical_id = f.canonical_id
    
    # Determine family and display name
    family = None
    display_name = None
    
    if f.modelsdev:
        family = f.modelsdev.family
        display_name = f.modelsdev.display_name
    
    # Try to infer family from model_id using overrides
    if not family:
        model_families = overrides.get("model_families", {})
        for family_key, family_name in model_families.items():
            if family_key.lower() in model_id.lower():
                family = family_name
                break
    
    if not display_name:
        display_name = model_id
    
    # Capabilities - use modelsdev if available, else defaults
    supports_reasoning = f.modelsdev.supports_reasoning if f.modelsdev else False
    supports_tool_call = f.modelsdev.supports_tool_call if f.modelsdev else False
    supports_structured_output = f.modelsdev.supports_structured_output if f.modelsdev else False
    input_modalities = f.modelsdev.input_modalities if f.modelsdev else ["text"]
    output_modalities = f.modelsdev.output_modalities if f.modelsdev else ["text"]
    attachments = f.modelsdev.attachments if f.modelsdev else []
    
    # Limits
    context_tokens = f.modelsdev.context_tokens if f.modelsdev else None
    max_input_tokens = f.modelsdev.max_input_tokens if f.modelsdev else None
    max_output_tokens = f.modelsdev.max_output_tokens if f.modelsdev else None
    
    # Pricing
    price_input = f.modelsdev.price_input_per_million if f.modelsdev else None
    price_output = f.modelsdev.price_output_per_million if f.modelsdev else None
    price_reasoning = f.modelsdev.price_reasoning_per_million if f.modelsdev else None
    
    # Calculate average price for tier
    avg_price = None
    if price_input is not None and price_output is not None:
        avg_price = (price_input + price_output) / 2
    
    # Derive tiers
    cost_tier = _derive_cost_tier(avg_price, stats)
    arena_score = f.arena.rating if f.arena else None
    quality_tier = _derive_quality_tier(arena_score, provider, stats)
    
    # Reasoning tier: base on quality, bump if reasoning supported
    reasoning_tier = quality_tier
    if supports_reasoning and reasoning_tier > 1:
        reasoning_tier = max(1, reasoning_tier - 1)
    
    # Creative tier: start with quality tier (can be refined later)
    creative_tier = quality_tier
    
    # Arena confidence intervals
    arena_ci_low = f.arena.rating_q025 if f.arena else None
    arena_ci_high = f.arena.rating_q975 if f.arena else None
    
    # Meta
    knowledge_cutoff = f.modelsdev.knowledge_cutoff if f.modelsdev else None
    release_date = f.modelsdev.release_date if f.modelsdev else None
    last_updated = f.modelsdev.last_updated if f.modelsdev else None
    open_weights = f.modelsdev.open_weights if f.modelsdev else False
    
    # Tags
    tags = _derive_tags(f)
    
    return CanonicalModel(
        canonical_id=canonical_id,
        provider=provider,
        model_id=model_id,
        family=family,
        display_name=display_name,
        supports_reasoning=supports_reasoning,
        supports_tool_call=supports_tool_call,
        supports_structured_output=supports_structured_output,
        input_modalities=input_modalities,
        output_modalities=output_modalities,
        attachments=attachments,
        context_tokens=context_tokens,
        max_input_tokens=max_input_tokens,
        max_output_tokens=max_output_tokens,
        price_input_per_million=price_input,
        price_output_per_million=price_output,
        price_reasoning_per_million=price_reasoning,
        quality_tier=quality_tier,
        reasoning_tier=reasoning_tier,
        creative_tier=creative_tier,
        cost_tier=cost_tier,
        arena_score=arena_score,
        arena_ci_low=arena_ci_low,
        arena_ci_high=arena_ci_high,
        knowledge_cutoff=knowledge_cutoff,
        release_date=release_date,
        last_updated=last_updated,
        open_weights=open_weights,
        tags=tags
    )


def build_catalog(
    ttl_hours: int = 24,
    force_refresh: bool = False
) -> Catalog:
    """
    Build the complete catalog from all sources.
    
    This is the main public entrypoint for catalog building. It:
    0. Loads .env file if available (for API keys)
    1. Checks cache if force_refresh=False
    2. Loads data from all sources
    3. Fuses sources using ID mapping
    4. Computes global statistics
    5. Derives CanonicalModels with tiers
    6. Saves to cache
    7. Returns Catalog
    
    Args:
        ttl_hours: Cache TTL in hours (default 24)
        force_refresh: If True, ignore cache and rebuild
        
    Returns:
        Catalog with all available models
    """
    # 0. Try to load .env file from common locations
    # This ensures any-llm can discover providers
    _load_env_file()
    
    # 1. Check cache
    if not force_refresh:
        cached = cache_module.load_cached_catalog(ttl_hours)
        if cached:
            return cached
    
    # 2. Load sources
    print("Loading models from any-llm...")
    anyllm_models = load_anyllm_models()
    
    if not anyllm_models:
        print("Warning: No models found from any-llm. Catalog will be empty.")
        print("")
        print("Possible reasons:")
        print("  1. No valid API keys found in environment")
        print("  2. Check your .env file has valid API keys:")
        print("     OPENAI_API_KEY=sk-proj-...")
        print("     ANTHROPIC_API_KEY=sk-ant-...")
        print("  3. API keys may be invalid or expired")
        print("")
    
    print("Fetching models.dev metadata...")
    modelsdev_data = fetch_modelsdev_json()
    modelsdev_map = normalize_modelsdev(modelsdev_data)
    
    print("Loading arena quality scores...")
    arena_map = load_arena_models()
    
    print("Loading overrides...")
    overrides = load_overrides()
    
    # 3. Fuse sources
    print("Fusing data sources...")
    fused_raw = fuse_sources(anyllm_models, modelsdev_map, arena_map, overrides)
    
    # 4. Compute global stats
    print("Computing global statistics...")
    stats = _compute_global_stats(fused_raw)
    
    # 5. Derive canonical models
    print("Deriving canonical models...")
    canonical_models = [
        _derive_canonical(f, stats, overrides)
        for f in fused_raw
    ]
    
    # 6. Create catalog
    catalog = Catalog(
        catalog_version=1,
        built_at=datetime.now().isoformat(),
        models=canonical_models
    )
    
    # 7. Save to cache
    print(f"Saving catalog with {len(canonical_models)} models...")
    cache_module.save_catalog(catalog)
    
    return catalog
