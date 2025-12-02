"""LLMHub CLI package.

This package provides both CLI commands and programmatic APIs for:
- Building and querying model catalogs
- Loading and validating spec configurations
- Generating runtime configurations from specs
- Managing runtime configurations

Programmatic API Quick Reference:

Catalog Operations:
    from llmhub_cli import build_catalog, get_catalog
    catalog = build_catalog()  # Build full catalog
    openai = get_catalog(provider="openai")  # Filter by provider

Spec Management:
    from llmhub_cli import load_spec
    from llmhub_cli.spec import validate_spec
    spec = load_spec("llmhub.spec.yaml")
    result = validate_spec(spec)

Runtime Generation:
    from llmhub_cli import generate_runtime_from_spec, save_runtime
    result = generate_runtime_from_spec(spec)
    save_runtime("llmhub.yaml", result.runtime)

Runtime Management:
    from llmhub_cli import load_runtime, save_runtime
    runtime = load_runtime("llmhub.yaml")

For more details, see individual module documentation.
"""

__version__ = "0.1.0"

# Catalog operations
from .catalog import build_catalog, get_catalog, Catalog, CanonicalModel

# Spec management
from .spec import load_spec, SpecConfig

# Generator
from .generator import generate_runtime_from_spec, GeneratorOptions, GenerationResult

# Runtime management
from .runtime import load_runtime, save_runtime

__all__ = [
    # Version
    "__version__",
    # Catalog
    "build_catalog",
    "get_catalog",
    "Catalog",
    "CanonicalModel",
    # Spec
    "load_spec",
    "SpecConfig",
    # Generator
    "generate_runtime_from_spec",
    "GeneratorOptions",
    "GenerationResult",
    # Runtime
    "load_runtime",
    "save_runtime",
]
