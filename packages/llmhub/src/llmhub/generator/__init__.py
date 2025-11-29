"""
Generator Module: Convert human specs into machine configs.

This is the main public API for the generator module.

Exports:
    - generate_machine_config: Main end-to-end function
    - All subproblem models and functions (for advanced usage)
"""
from typing import Optional, List
from llmhub_runtime import LLMHub
from llmhub.catalog.schema import CanonicalModel

# Import all subproblems
from .sp1_spec_schema import (
    ProjectSpec,
    load_project_spec,
    parse_project_spec,
    SpecSchemaError,
)
from .sp2_needs_interpreter import (
    interpret_needs,
    InterpreterError,
)
from .sp3_needs_schema import (
    RoleNeed,
    parse_role_needs,
    NeedsSchemaError,
)
from .sp4_catalog_view import (
    CanonicalModel,
    load_catalog_view,
    CatalogViewError,
)
from .sp9_selector_orchestrator import (
    SelectionResult,
    SelectorOptions,
    select_for_role,
)
from .sp10_machine_config_emitter import (
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


__all__ = [
    # Main API
    "generate_machine_config",
    "GeneratorError",
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
