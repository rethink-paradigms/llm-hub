"""
Generator Module: Convert human specs into machine configs.

This is the main public API for the generator module.

Exports:
    - generate_machine_config: Main end-to-end function
    - All subproblem models and functions (for advanced usage)
"""
from typing import Optional, List
from llmhub_runtime import LLMHub
from llmhub_cli.catalog.schema import CanonicalModel

# Import all subproblems
from .spec import (
    ProjectSpec,
    load_project_spec,
    parse_project_spec,
    SpecSchemaError,
)
from .needs import (
    interpret_needs,
    InterpreterError,
    RoleNeed,
    parse_role_needs,
    NeedsSchemaError,
)
from .catalog_view import (
    CanonicalModel,
    load_catalog_view,
    CatalogViewError,
)
from .selection import (
    SelectionResult,
    SelectorOptions,
    select_for_role,
)
from .emitter import (
    MachineConfig,
    build_machine_config,
    write_machine_config,
)


class GeneratorError(Exception):
    """Base exception for generator errors."""
    pass


def generate_machine_config(
    spec_path: str,
    hub: LLMHub,
    output_path: Optional[str] = None,
    catalog_override: Optional[List[CanonicalModel]] = None,
    catalog_ttl_hours: int = 24,
    force_catalog_refresh: bool = False,
    selector_options: Optional[SelectorOptions] = None
) -> MachineConfig:
    """
    Generate machine config from human spec (end-to-end).
    
    This is the main entrypoint for the generator. It orchestrates all subproblems
    to convert a human-written spec into a machine-readable config.
    
    Args:
        spec_path: Path to llmhub.spec.yaml
        hub: LLMHub instance (must have generator role configured)
        output_path: Optional path to write llmhub.yaml (if None, don't write)
        catalog_override: Optional catalog override for testing
        catalog_ttl_hours: Catalog cache TTL in hours
        force_catalog_refresh: Force catalog rebuild
        selector_options: Options for model selection
        
    Returns:
        MachineConfig ready for runtime
        
    Raises:
        GeneratorError: If any step fails
    """
    try:
        # Step 1: Load and parse spec (SP1)
        spec = load_project_spec(spec_path)
        
        # Step 2: Interpret needs via LLM (SP2)
        needs = interpret_needs(spec, hub)
        
        # Step 3: Load catalog (SP4)
        models = load_catalog_view(
            ttl_hours=catalog_ttl_hours,
            force_refresh=force_catalog_refresh,
            catalog_override=catalog_override
        )
        
        # Step 4: Select models for each role (SP9)
        if selector_options is None:
            selector_options = SelectorOptions()
        
        selections = []
        for need in needs:
            selection = select_for_role(need, models, selector_options)
            selections.append(selection)
        
        # Step 5: Build machine config (SP10)
        machine_config = build_machine_config(spec, selections)
        
        # Step 6: Write to file if path provided
        if output_path:
            write_machine_config(output_path, machine_config)
        
        return machine_config
        
    except (SpecSchemaError, InterpreterError, NeedsSchemaError, CatalogViewError) as e:
        raise GeneratorError(f"Generator failed: {str(e)}") from e
    except Exception as e:
        raise GeneratorError(f"Unexpected error in generator: {str(e)}") from e


# Import from generator_hook for simple runtime generation API
from ..generator_hook import (
    generate_runtime,
    GeneratorOptions,
    GenerationResult,
)


def generate_runtime_from_spec(
    spec,
    options: Optional[GeneratorOptions] = None
) -> GenerationResult:
    """
    Generate runtime configuration from spec configuration.
    
    This function converts a spec configuration (which describes what you want
    from your LLMs) into a runtime configuration (which specifies concrete
    provider and model selections). It uses heuristics and optionally LLM-
    assisted selection to choose the best models for each role.
    
    Args:
        spec: SpecConfig object with role definitions and preferences
        options: Optional GeneratorOptions to control generation behavior:
            - no_llm (bool): Use heuristic-only mode without LLM assistance
            - explain (bool): Include explanations for model selections
    
    Returns:
        GenerationResult object containing:
            - runtime (RuntimeConfig): Generated runtime configuration with
              concrete provider/model mappings for each role
            - explanations (dict[str, str]): Role selection explanations
              (only populated if options.explain=True)
    
    Example:
        >>> from llmhub_cli import load_spec, generate_runtime_from_spec, save_runtime
        >>> from llmhub_cli.generator import GeneratorOptions
        >>> 
        >>> # Load spec from file
        >>> spec = load_spec("llmhub.spec.yaml")
        >>> 
        >>> # Generate runtime with default options
        >>> result = generate_runtime_from_spec(spec)
        >>> 
        >>> # Save generated runtime
        >>> save_runtime("llmhub.yaml", result.runtime)
        >>> 
        >>> # Generate with explanations
        >>> options = GeneratorOptions(explain=True)
        >>> result = generate_runtime_from_spec(spec, options)
        >>> 
        >>> # Print explanations
        >>> for role, explanation in result.explanations.items():
        ...     print(f"{role}: {explanation}")
        >>> 
        >>> # Use heuristic-only mode (no LLM calls)
        >>> options = GeneratorOptions(no_llm=True)
        >>> result = generate_runtime_from_spec(spec, options)
    
    See Also:
        - load_spec: Load a spec configuration from file
        - save_runtime: Save generated runtime to file
        - GeneratorOptions: Options for controlling generation
        - GenerationResult: Result object with runtime and explanations
    """
    return generate_runtime(spec, options)


__all__ = [
    # Main API
    "generate_machine_config",
    "GeneratorError",
    # Simple runtime generation API (for CLI-compatible usage)
    "generate_runtime_from_spec",
    "GeneratorOptions",
    "GenerationResult",
    # Core models
    "ProjectSpec",
    "RoleNeed",
    "SelectionResult",
    "MachineConfig",
    # Utilities
    "load_project_spec",
    "parse_project_spec",
    "interpret_needs",
    "parse_role_needs",
    "load_catalog_view",
    "select_for_role",
    "build_machine_config",
    "write_machine_config",
    # Options
    "SelectorOptions",
    # Exceptions
    "SpecSchemaError",
    "InterpreterError",
    "NeedsSchemaError",
    "CatalogViewError",
]
