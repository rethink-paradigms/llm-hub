#!/usr/bin/env python3
"""
Example: Programmatic Runtime Generation

This script demonstrates how to use the LLMHub API to programmatically
generate runtime configurations from spec files.
"""

from pathlib import Path
from llmhub_cli import (
    load_spec,
    generate_runtime_from_spec,
    save_runtime,
    load_runtime,
)
from llmhub_cli.generator import GeneratorOptions
from llmhub_cli.spec import validate_spec


def example_1_basic_generation():
    """Example 1: Basic spec to runtime generation."""
    print("=" * 70)
    print("Example 1: Basic Runtime Generation")
    print("=" * 70)
    print()
    
    # Load spec from file
    spec_path = "llmhub.spec.yaml"
    
    if not Path(spec_path).exists():
        print(f"❌ Spec file not found: {spec_path}")
        print("Please create a spec file first using 'llmhub init'")
        return
    
    print(f"Loading spec from: {spec_path}")
    spec = load_spec(spec_path)
    
    print(f"  Project: {spec.project}")
    print(f"  Environment: {spec.env}")
    print(f"  Roles: {len(spec.roles)}")
    print()
    
    # Generate runtime
    print("Generating runtime configuration...")
    result = generate_runtime_from_spec(spec)
    
    print(f"✓ Runtime generated with {len(result.runtime.roles)} roles")
    print()
    
    # Display generated roles
    print("Generated role configurations:")
    for role_name, role_config in result.runtime.roles.items():
        print(f"  {role_name}:")
        print(f"    Provider: {role_config.provider}")
        print(f"    Model: {role_config.model}")
        print(f"    Mode: {role_config.mode}")
    print()


def example_2_generation_with_explanations():
    """Example 2: Generate with explanations for selections."""
    print("=" * 70)
    print("Example 2: Generation with Explanations")
    print("=" * 70)
    print()
    
    spec_path = "llmhub.spec.yaml"
    
    if not Path(spec_path).exists():
        print(f"❌ Spec file not found: {spec_path}")
        return
    
    spec = load_spec(spec_path)
    
    # Generate with explanations
    print("Generating runtime with explanations...")
    options = GeneratorOptions(explain=True)
    result = generate_runtime_from_spec(spec, options)
    
    print()
    print("Model Selection Explanations:")
    print()
    
    for role, explanation in result.explanations.items():
        print(f"  {role}:")
        print(f"    {explanation}")
        print()


def example_3_save_to_file():
    """Example 3: Generate and save runtime to file."""
    print("=" * 70)
    print("Example 3: Save Generated Runtime")
    print("=" * 70)
    print()
    
    spec_path = "llmhub.spec.yaml"
    runtime_path = "llmhub.generated.yaml"
    
    if not Path(spec_path).exists():
        print(f"❌ Spec file not found: {spec_path}")
        return
    
    # Load and generate
    spec = load_spec(spec_path)
    result = generate_runtime_from_spec(spec)
    
    # Save to file
    print(f"Saving runtime to: {runtime_path}")
    save_runtime(runtime_path, result.runtime)
    
    print(f"✓ Runtime saved")
    print()
    
    # Verify by loading back
    print("Verifying saved runtime...")
    loaded = load_runtime(runtime_path)
    
    print(f"✓ Runtime loaded successfully")
    print(f"  Project: {loaded.project}")
    print(f"  Roles: {len(loaded.roles)}")
    print()


def example_4_multi_environment():
    """Example 4: Generate configs for multiple environments."""
    print("=" * 70)
    print("Example 4: Multi-Environment Generation")
    print("=" * 70)
    print()
    
    spec_path = "llmhub.spec.yaml"
    
    if not Path(spec_path).exists():
        print(f"❌ Spec file not found: {spec_path}")
        return
    
    # Load base spec
    spec = load_spec(spec_path)
    
    # Generate for different environments
    environments = ["dev", "staging", "prod"]
    
    for env in environments:
        print(f"Generating for {env} environment...")
        
        # You could modify spec.env here if needed
        # spec.env = env
        
        result = generate_runtime_from_spec(spec)
        output_path = f"llmhub.{env}.yaml"
        
        save_runtime(output_path, result.runtime)
        print(f"  ✓ Saved to {output_path}")
    
    print()
    print("✓ All environment configs generated")
    print()


def example_5_validate_before_generation():
    """Example 5: Validate spec before generating runtime."""
    print("=" * 70)
    print("Example 5: Validate Spec Before Generation")
    print("=" * 70)
    print()
    
    spec_path = "llmhub.spec.yaml"
    
    if not Path(spec_path).exists():
        print(f"❌ Spec file not found: {spec_path}")
        return
    
    # Validate spec first
    print(f"Validating spec: {spec_path}")
    validation_result = validate_spec(spec_path)
    
    if validation_result.valid:
        print("✓ Spec is valid")
        
        if validation_result.warnings:
            print("\nWarnings:")
            for warning in validation_result.warnings:
                print(f"  ⚠️  {warning}")
        
        print()
        
        # Proceed with generation
        spec = load_spec(spec_path)
        result = generate_runtime_from_spec(spec)
        
        print("✓ Runtime generated successfully")
        print(f"  Roles: {len(result.runtime.roles)}")
        
    else:
        print("❌ Spec validation failed")
        print("\nErrors:")
        for error in validation_result.errors:
            print(f"  ✗ {error}")
        print()
        print("Please fix the errors before generating runtime.")
    
    print()


def example_6_programmatic_spec_creation():
    """Example 6: Create spec programmatically and generate runtime."""
    print("=" * 70)
    print("Example 6: Programmatic Spec Creation")
    print("=" * 70)
    print()
    
    from llmhub_cli import SpecConfig
    from llmhub_cli.spec_models import (
        ProviderSpec,
        RoleSpec,
        PreferencesSpec,
        RoleKind,
    )
    
    # Create spec programmatically
    print("Creating spec programmatically...")
    
    spec = SpecConfig(
        project="dynamic-app",
        env="dev",
        providers={
            "openai": ProviderSpec(
                enabled=True,
                env_key="OPENAI_API_KEY"
            )
        },
        roles={
            "llm.chat": RoleSpec(
                kind=RoleKind.chat,
                description="General chat interface",
                preferences=PreferencesSpec(
                    cost="low",
                    quality="medium",
                    latency="low",
                    providers=["openai"]
                ),
                mode_params={}
            ),
            "llm.embedding": RoleSpec(
                kind=RoleKind.embedding,
                description="Text embeddings",
                preferences=PreferencesSpec(
                    cost="low",
                    providers=["openai"]
                ),
                mode_params={}
            )
        }
    )
    
    print(f"✓ Spec created with {len(spec.roles)} roles")
    print()
    
    # Generate runtime
    print("Generating runtime from programmatic spec...")
    result = generate_runtime_from_spec(spec)
    
    print("✓ Runtime generated")
    print()
    
    print("Generated roles:")
    for role_name, role_config in result.runtime.roles.items():
        print(f"  {role_name}: {role_config.provider}:{role_config.model}")
    print()


def main():
    """Run all examples."""
    print("\n")
    print("╔" + "═" * 68 + "╗")
    print("║" + " " * 12 + "LLMHub Runtime Generation Examples" + " " * 21 + "║")
    print("╚" + "═" * 68 + "╝")
    print("\n")
    
    try:
        example_1_basic_generation()
        example_2_generation_with_explanations()
        example_3_save_to_file()
        example_4_multi_environment()
        example_5_validate_before_generation()
        example_6_programmatic_spec_creation()
        
        print("=" * 70)
        print("All examples completed successfully!")
        print("=" * 70)
        print()
        
    except Exception as e:
        print(f"\n❌ Error: {e}\n")
        import traceback
        traceback.print_exc()
        print()


if __name__ == '__main__':
    main()
