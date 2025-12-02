#!/usr/bin/env python3
"""
Example: Programmatic Catalog Access

This script demonstrates how to use the LLMHub catalog API programmatically
to query available models, filter by criteria, and access model metadata.
"""

from llmhub_cli import build_catalog, get_catalog


def example_1_basic_catalog():
    """Example 1: Build and access the full catalog."""
    print("=" * 70)
    print("Example 1: Build and Access Full Catalog")
    print("=" * 70)
    print()
    
    # Build the catalog (uses cache if fresh)
    catalog = build_catalog()
    
    print(f"Catalog built at: {catalog.built_at}")
    print(f"Total models: {len(catalog.models)}")
    print()
    
    # Count models by provider
    provider_counts = {}
    for model in catalog.models:
        provider_counts[model.provider] = provider_counts.get(model.provider, 0) + 1
    
    print("Models by provider:")
    for provider, count in sorted(provider_counts.items()):
        print(f"  {provider}: {count} models")
    print()


def example_2_filter_by_provider():
    """Example 2: Get models from a specific provider."""
    print("=" * 70)
    print("Example 2: Filter by Provider")
    print("=" * 70)
    print()
    
    # Get all OpenAI models
    openai_catalog = get_catalog(provider="openai")
    
    print(f"Found {len(openai_catalog.models)} OpenAI models:")
    print()
    
    # Display first 5 models
    for model in openai_catalog.models[:5]:
        print(f"  {model.model_id}")
        print(f"    Cost Tier: {model.cost_tier} | Quality Tier: {model.quality_tier}")
        if model.price_input_per_million:
            print(f"    Price: ${model.price_input_per_million:.4f} in / ${model.price_output_per_million:.4f} out (per 1M tokens)")
        print()


def example_3_find_cheapest_models():
    """Example 3: Find the cheapest models with good quality."""
    print("=" * 70)
    print("Example 3: Find Cheapest High-Quality Models")
    print("=" * 70)
    print()
    
    # Get full catalog
    catalog = build_catalog()
    
    # Filter for cost tier 1-2 (cheapest) and quality tier 1-3 (best)
    cheap_quality_models = [
        m for m in catalog.models
        if m.cost_tier <= 2 and m.quality_tier <= 3
    ]
    
    # Sort by cost tier, then quality tier
    cheap_quality_models.sort(key=lambda m: (m.cost_tier, m.quality_tier))
    
    print(f"Found {len(cheap_quality_models)} cheap, high-quality models:")
    print()
    
    # Display top 10
    for model in cheap_quality_models[:10]:
        print(f"  {model.provider}:{model.model_id}")
        print(f"    Cost Tier: {model.cost_tier} | Quality Tier: {model.quality_tier}")
        if model.arena_score:
            print(f"    Arena Score: {model.arena_score:.0f}")
        print()


def example_4_filter_by_capability():
    """Example 4: Find models with specific capabilities."""
    print("=" * 70)
    print("Example 4: Filter by Capability (Reasoning)")
    print("=" * 70)
    print()
    
    # Get models with reasoning capability
    reasoning_catalog = get_catalog(tags=["reasoning"])
    
    print(f"Found {len(reasoning_catalog.models)} models with reasoning:")
    print()
    
    # Sort by reasoning tier
    models_sorted = sorted(reasoning_catalog.models, key=lambda m: m.reasoning_tier)
    
    for model in models_sorted[:10]:
        print(f"  {model.provider}:{model.model_id}")
        print(f"    Reasoning Tier: {model.reasoning_tier}")
        print(f"    Quality Tier: {model.quality_tier} | Cost Tier: {model.cost_tier}")
        print()


def example_5_multi_modal_models():
    """Example 5: Find multi-modal models (vision support)."""
    print("=" * 70)
    print("Example 5: Find Vision-Capable Models")
    print("=" * 70)
    print()
    
    # Get models with vision capability
    vision_catalog = get_catalog(tags=["vision"])
    
    print(f"Found {len(vision_catalog.models)} vision-capable models:")
    print()
    
    for model in vision_catalog.models[:10]:
        print(f"  {model.provider}:{model.model_id}")
        print(f"    Input: {', '.join(model.input_modalities)}")
        print(f"    Output: {', '.join(model.output_modalities)}")
        print(f"    Tags: {', '.join(model.tags)}")
        print()


def example_6_compare_providers():
    """Example 6: Compare models across providers."""
    print("=" * 70)
    print("Example 6: Compare Providers")
    print("=" * 70)
    print()
    
    catalog = build_catalog()
    
    # Group by provider and calculate averages
    provider_stats = {}
    
    for model in catalog.models:
        if model.provider not in provider_stats:
            provider_stats[model.provider] = {
                'count': 0,
                'avg_cost': [],
                'avg_quality': [],
            }
        
        provider_stats[model.provider]['count'] += 1
        provider_stats[model.provider]['avg_cost'].append(model.cost_tier)
        provider_stats[model.provider]['avg_quality'].append(model.quality_tier)
    
    print("Provider Statistics:")
    print()
    
    for provider in sorted(provider_stats.keys()):
        stats = provider_stats[provider]
        avg_cost = sum(stats['avg_cost']) / len(stats['avg_cost'])
        avg_quality = sum(stats['avg_quality']) / len(stats['avg_quality'])
        
        print(f"  {provider}:")
        print(f"    Models: {stats['count']}")
        print(f"    Avg Cost Tier: {avg_cost:.2f}")
        print(f"    Avg Quality Tier: {avg_quality:.2f}")
        print()


def main():
    """Run all examples."""
    print("\n")
    print("╔" + "═" * 68 + "╗")
    print("║" + " " * 15 + "LLMHub Catalog API Examples" + " " * 26 + "║")
    print("╚" + "═" * 68 + "╝")
    print("\n")
    
    try:
        example_1_basic_catalog()
        example_2_filter_by_provider()
        example_3_find_cheapest_models()
        example_4_filter_by_capability()
        example_5_multi_modal_models()
        example_6_compare_providers()
        
        print("=" * 70)
        print("All examples completed successfully!")
        print("=" * 70)
        print()
        
    except Exception as e:
        print(f"\n❌ Error: {e}\n")
        print("Make sure you have:")
        print("  1. API keys configured in .env file")
        print("  2. Run 'llmhub catalog refresh' at least once")
        print()
        raise


if __name__ == '__main__':
    main()
