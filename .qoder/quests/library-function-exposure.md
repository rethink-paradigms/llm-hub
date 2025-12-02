# Library Function Exposure Design

## Overview

This design document addresses the need to expose CLI functionality as programmatic library functions in the LLM Hub project. Currently, users can only interact with catalog operations and runtime generation through CLI commands. This enhancement will enable developers to import the libraries and call these functions directly in their code.

## Current State Analysis

### Existing CLI Commands

The project provides the following key CLI operations:

| Command | Function | Current Access | Package |
|---------|----------|----------------|----------|
| `llmhub catalog refresh` | Force rebuild catalog from sources | CLI only | llmhub_cli |
| `llmhub catalog show` | Display catalog with filtering | CLI only | llmhub_cli |
| `llmhub generate` | Generate runtime config from spec | CLI only | llmhub_cli |
| `llmhub runtime show` | Display runtime configuration | CLI only | llmhub_cli |

### Currently Exposed APIs

#### Runtime Library (llmhub_runtime)
The runtime package already exposes a clean programmatic API:

| Function | Purpose | Status |
|----------|---------|--------|
| `LLMHub.__init__()` | Initialize hub with config | ✅ Available |
| `LLMHub.completion()` | Execute LLM completion by role | ✅ Available |
| `LLMHub.embedding()` | Generate embeddings by role | ✅ Available |

#### CLI Library (llmhub_cli)
The catalog module has limited exposure:

| Function | Purpose | Status |
|----------|---------|--------|
| `build_catalog()` | Build catalog from sources | ✅ Available |
| `load_cached_catalog()` | Load cached catalog | ✅ Available |
| `clear_cache()` | Clear catalog cache | ✅ Available |

### Gaps Identified

The following capabilities are **not exposed** programmatically:

1. **Runtime Generation**: Converting spec to runtime config
2. **Spec Loading/Validation**: Loading and validating spec files
3. **Runtime Loading/Saving**: Reading and writing runtime configs
4. **Catalog Operations**: High-level catalog query and filtering
5. **Environment Management**: Generating and validating environment files

## Design Goals

### Primary Objectives

1. **Enable Programmatic Access**: Expose all CLI operations as importable functions
2. **Maintain Separation**: Keep CLI-specific logic (user interaction, formatting) separate from core functionality
3. **Backward Compatibility**: Ensure existing CLI commands continue to work without changes
4. **Consistent Interface**: Provide intuitive, well-documented APIs that follow Python conventions

### Non-Goals

1. Creating new functionality beyond what CLI commands offer
2. Modifying the runtime execution layer (already well-exposed)
3. Changing the CLI command structure or behavior

## Proposed Public API

### Catalog Operations

**Module**: `llmhub_cli.catalog`

```
Current Exposure:
- build_catalog(ttl_hours, force_refresh) → Catalog
- load_cached_catalog(ttl_hours) → Optional[Catalog]
- clear_cache() → None

Additional Exposure Needed:
- get_catalog(ttl_hours, force_refresh, provider_filter) → Catalog
  (convenience wrapper that combines build + filtering)

Already Available:
- Catalog model with .models attribute
- CanonicalModel schema with all metadata fields
```

**Usage Pattern**:
Developers can import and use catalog functions directly to query available models, check pricing, and filter by capabilities without running CLI commands.

### Runtime Generation

**Module**: `llmhub_cli.generator` (new public API layer)

```
New Exposure Needed:
- generate_runtime_from_spec(spec, options) → GenerationResult
  (already exists as generate_runtime() in generator_hook.py)

Supporting Types:
- GeneratorOptions (already exposed in generator_hook.py)
- GenerationResult (already exposed in generator_hook.py)
```

**Usage Pattern**:
Developers can programmatically generate runtime configurations from spec objects or files, enabling automated configuration management and testing workflows.

### Spec Management

**Module**: `llmhub_cli.spec` (new public API layer)

```
Current Internal Functions (runtime_io.py, spec_models.py):
- load_spec(spec_path) → SpecConfig
- validate_spec(spec) → ValidationResult
- SpecConfig model (already exposed in spec_models.py)

New Exposure Needed:
- Expose load_spec() publicly
- Add validate_spec() as public function
- Expose SpecConfig and related models
```

**Usage Pattern**:
Developers can load and validate spec files programmatically, enabling integration with configuration management tools and automated validation pipelines.

### Runtime Configuration Management

**Module**: `llmhub_cli.runtime` (new public API layer)

```
Current Internal Functions (runtime_io.py):
- load_runtime(runtime_path) → RuntimeConfig
- save_runtime(runtime_path, config) → None

New Exposure Needed:
- Expose load_runtime() publicly
- Expose save_runtime() publicly
- RuntimeConfig already exposed via llmhub_runtime package
```

**Usage Pattern**:
Developers can programmatically load and save runtime configurations, enabling dynamic configuration updates and multi-environment management.

## Architecture Changes

### Package Restructuring

#### Current Structure
```
llmhub_cli/
├── __init__.py (minimal, only __version__)
├── catalog/
│   ├── __init__.py (exposes build_catalog, Catalog, CanonicalModel)
│   └── builder.py
├── commands/ (CLI-specific)
├── generator_hook.py (internal)
├── spec_models.py (internal)
└── runtime_io.py (internal)
```

#### Proposed Structure
```
llmhub_cli/
├── __init__.py (expose public API)
├── catalog/
│   └── __init__.py (unchanged, already good)
├── generator/
│   └── __init__.py (expose generate_runtime_from_spec, GeneratorOptions)
├── spec/
│   └── __init__.py (NEW: expose load_spec, validate_spec, SpecConfig)
├── runtime/
│   └── __init__.py (NEW: expose load_runtime, save_runtime)
├── commands/ (CLI-specific, internal only)
└── [internal modules]
```

### Module Exposure Strategy

#### Top-Level Package Init
Update `llmhub_cli/__init__.py` to expose commonly used functions:

```
Exposed at package level:
- build_catalog (from catalog)
- get_catalog (from catalog) 
- generate_runtime_from_spec (from generator)
- load_spec (from spec)
- load_runtime (from runtime)
- save_runtime (from runtime)
```

This allows developers to use:
- `from llmhub_cli import build_catalog, generate_runtime_from_spec`
- Or more specific: `from llmhub_cli.catalog import build_catalog`

#### Submodule Organization

| Module | Exposed Functions | Exposed Models |
|--------|------------------|----------------|
| catalog | build_catalog, load_cached_catalog, clear_cache, get_catalog | Catalog, CanonicalModel |
| generator | generate_runtime_from_spec | GeneratorOptions, GenerationResult |
| spec | load_spec, validate_spec | SpecConfig, RoleSpec, PreferencesSpec |
| runtime | load_runtime, save_runtime | RuntimeConfig (from llmhub_runtime) |

### Handling CLI-Specific Code

**Separation Strategy**:

The commands directory remains internal and contains only CLI-specific concerns:
- User prompts and confirmations
- Rich console formatting and tables
- Typer command definitions
- Exit codes and error handling for CLI

Core business logic is extracted to the public modules:
- All data transformation logic
- Validation logic
- File I/O operations
- API calls and data fetching

**Migration Approach**:

For functions currently in command files:
1. Extract core logic to appropriate public module
2. CLI command becomes thin wrapper that calls public function
3. CLI command adds only presentation layer (formatting, prompts, exit codes)

## Implementation Plan

### Phase 1: Create Public Module Structure

**Actions**:
1. Create `llmhub_cli/spec/__init__.py` module
2. Create `llmhub_cli/runtime/__init__.py` module
3. Update `llmhub_cli/generator/__init__.py` to expose public API

**No Code Changes Required**:
- Move or refactor code from existing modules
- Simply expose existing functions through new module __init__ files

### Phase 2: Expose Existing Functions

**Catalog Module** (already good):
- No changes needed
- Already exposes build_catalog, Catalog, CanonicalModel

**Generator Module**:
- Add __init__.py that imports and exposes:
  - generate_runtime (rename to generate_runtime_from_spec at public API level)
  - GeneratorOptions
  - GenerationResult
- Source: generator_hook.py

**Spec Module** (new):
- Create __init__.py that imports and exposes:
  - load_spec (from spec_models.py)
  - SpecConfig and related models (from spec_models.py)
- Add validate_spec function wrapper

**Runtime Module** (new):
- Create __init__.py that imports and exposes:
  - load_runtime (from runtime_io.py)
  - save_runtime (from runtime_io.py)
  - RuntimeConfig (from llmhub_runtime)

### Phase 3: Update Top-Level Package Init

**Update llmhub_cli/__init__.py**:
- Import and re-export key functions for convenience
- Maintain __version__ export
- Add __all__ list for explicit public API

### Phase 4: Add Convenience Functions

**Catalog Module**:
Add `get_catalog()` function that wraps build_catalog with filtering:
- Parameters: ttl_hours, force_refresh, provider_filter, tag_filter
- Returns filtered Catalog object
- Simplifies common query patterns

**Spec Module**:
Add `validate_spec()` function:
- Parameter: spec (SpecConfig or file path)
- Returns validation result with detailed error messages
- Wraps Pydantic validation with user-friendly output

### Phase 5: Documentation

**Add docstrings** to all exposed functions with:
- Purpose and usage description
- Parameter descriptions with types
- Return value description
- Example usage
- Related functions

**Create usage examples** in examples directory:
- catalog_programmatic_access.py
- runtime_generation_programmatic.py
- spec_validation_programmatic.py

**Update README** with programmatic API section:
- Quick reference for each exposed function
- Link to examples
- Comparison with CLI usage

## API Reference

### Catalog API

#### build_catalog

```
Function Signature:
  build_catalog(ttl_hours=24, force_refresh=False) → Catalog

Purpose:
  Build the complete catalog from all data sources (any-llm, models.dev, LMArena)

Parameters:
  - ttl_hours (int): Cache TTL in hours, default 24
  - force_refresh (bool): If True, ignore cache and rebuild, default False

Returns:
  Catalog object containing list of CanonicalModel instances

Raises:
  Exception: If catalog building fails and no cache available

Example Usage:
  from llmhub_cli import build_catalog
  
  # Get cached catalog or build if stale
  catalog = build_catalog(ttl_hours=24)
  
  # Force fresh rebuild
  catalog = build_catalog(force_refresh=True)
  
  # Access models
  for model in catalog.models:
      print(f"{model.provider}:{model.model_id} - Cost Tier: {model.cost_tier}")
```

#### get_catalog (new convenience function)

```
Function Signature:
  get_catalog(ttl_hours=24, force_refresh=False, provider=None, tags=None) → Catalog

Purpose:
  Get catalog with optional filtering by provider and tags

Parameters:
  - ttl_hours (int): Cache TTL in hours, default 24
  - force_refresh (bool): If True, ignore cache and rebuild, default False
  - provider (str, optional): Filter models by provider name
  - tags (list[str], optional): Filter models that have all specified tags

Returns:
  Catalog object with filtered models

Example Usage:
  from llmhub_cli import get_catalog
  
  # Get all OpenAI models
  openai_catalog = get_catalog(provider="openai")
  
  # Get models with reasoning capability
  reasoning_catalog = get_catalog(tags=["reasoning"])
  
  # Get OpenAI models with vision
  vision_catalog = get_catalog(provider="openai", tags=["vision"])
```

#### load_cached_catalog

```
Function Signature:
  load_cached_catalog(ttl_hours=24) → Optional[Catalog]

Purpose:
  Load catalog from cache if available and fresh

Parameters:
  - ttl_hours (int): Maximum age of cache in hours, default 24

Returns:
  Catalog object if cache hit, None if cache miss or stale

Example Usage:
  from llmhub_cli.catalog import load_cached_catalog
  
  catalog = load_cached_catalog(ttl_hours=24)
  if catalog is None:
      print("Cache miss or stale")
```

#### clear_cache

```
Function Signature:
  clear_cache() → None

Purpose:
  Delete the catalog cache file

Example Usage:
  from llmhub_cli.catalog import clear_cache
  
  clear_cache()
  print("Catalog cache cleared")
```

### Generator API

#### generate_runtime_from_spec

```
Function Signature:
  generate_runtime_from_spec(spec, options=None) → GenerationResult

Purpose:
  Generate runtime configuration from spec configuration

Parameters:
  - spec (SpecConfig): Spec configuration object
  - options (GeneratorOptions, optional): Generation options
    - no_llm (bool): Use heuristic-only mode, default False
    - explain (bool): Include explanations for selections, default False

Returns:
  GenerationResult object containing:
    - runtime (RuntimeConfig): Generated runtime configuration
    - explanations (dict[str, str]): Role selection explanations if explain=True

Example Usage:
  from llmhub_cli import load_spec, generate_runtime_from_spec, save_runtime
  from llmhub_cli.generator import GeneratorOptions
  
  # Load spec
  spec = load_spec("llmhub.spec.yaml")
  
  # Generate runtime with explanations
  options = GeneratorOptions(explain=True)
  result = generate_runtime_from_spec(spec, options)
  
  # Save runtime
  save_runtime("llmhub.yaml", result.runtime)
  
  # Print explanations
  for role, explanation in result.explanations.items():
      print(f"{role}: {explanation}")
```

### Spec API

#### load_spec

```
Function Signature:
  load_spec(spec_path) → SpecConfig

Purpose:
  Load and validate spec configuration from YAML file

Parameters:
  - spec_path (str | Path): Path to spec YAML file

Returns:
  SpecConfig object with validated configuration

Raises:
  SpecError: If file not found or validation fails

Example Usage:
  from llmhub_cli import load_spec
  
  spec = load_spec("llmhub.spec.yaml")
  
  # Access spec properties
  print(f"Project: {spec.project}")
  print(f"Roles: {list(spec.roles.keys())}")
  
  # Access role details
  for role_name, role_spec in spec.roles.items():
      print(f"  {role_name}: {role_spec.kind} - {role_spec.description}")
```

#### validate_spec

```
Function Signature:
  validate_spec(spec) → ValidationResult

Purpose:
  Validate spec configuration and return detailed results

Parameters:
  - spec (SpecConfig | str | Path): Spec object or path to spec file

Returns:
  ValidationResult object containing:
    - valid (bool): True if valid
    - errors (list[str]): List of validation error messages
    - warnings (list[str]): List of validation warnings

Example Usage:
  from llmhub_cli.spec import validate_spec
  
  result = validate_spec("llmhub.spec.yaml")
  
  if result.valid:
      print("Spec is valid")
  else:
      print("Validation errors:")
      for error in result.errors:
          print(f"  - {error}")
```

### Runtime API

#### load_runtime

```
Function Signature:
  load_runtime(runtime_path) → RuntimeConfig

Purpose:
  Load runtime configuration from YAML file

Parameters:
  - runtime_path (str | Path): Path to runtime YAML file

Returns:
  RuntimeConfig object with runtime configuration

Raises:
  RuntimeError: If file not found or parsing fails

Example Usage:
  from llmhub_cli import load_runtime
  
  runtime = load_runtime("llmhub.yaml")
  
  # Access runtime properties
  print(f"Project: {runtime.project}")
  print(f"Providers: {list(runtime.providers.keys())}")
  
  # Access role configurations
  for role_name, role_config in runtime.roles.items():
      print(f"  {role_name}: {role_config.provider}:{role_config.model}")
```

#### save_runtime

```
Function Signature:
  save_runtime(runtime_path, config) → None

Purpose:
  Save runtime configuration to YAML file

Parameters:
  - runtime_path (str | Path): Path where runtime YAML will be saved
  - config (RuntimeConfig): Runtime configuration to save

Raises:
  RuntimeError: If unable to write file

Example Usage:
  from llmhub_cli import load_spec, generate_runtime_from_spec, save_runtime
  
  # Load spec and generate runtime
  spec = load_spec("llmhub.spec.yaml")
  result = generate_runtime_from_spec(spec)
  
  # Save to file
  save_runtime("llmhub.yaml", result.runtime)
  
  # Save to different environments
  save_runtime("llmhub.dev.yaml", result.runtime)
  save_runtime("llmhub.prod.yaml", result.runtime)
```

## Usage Examples

### Example 1: Query Catalog Programmatically

```
Scenario: Find cheapest models with reasoning capability

Implementation Approach:
  1. Import get_catalog function
  2. Build catalog with reasoning tag filter
  3. Sort by cost_tier
  4. Display top results

Key Functions Used:
  - get_catalog(tags=["reasoning"])
  - Catalog.models filtering and sorting

Expected Workflow:
  - Developer imports function
  - Calls get_catalog with tag filter
  - Iterates through models
  - Applies custom business logic (sorting, filtering)
  - Uses results in application
```

### Example 2: Automated Runtime Generation

```
Scenario: CI/CD pipeline generates runtime config for multiple environments

Implementation Approach:
  1. Load base spec from repository
  2. Generate runtime with specific options
  3. Save to environment-specific files
  4. Optionally validate generated config

Key Functions Used:
  - load_spec(spec_path)
  - generate_runtime_from_spec(spec, options)
  - save_runtime(path, runtime)

Expected Workflow:
  - CI script loads spec
  - Loops through environments (dev, staging, prod)
  - Generates runtime for each with different options
  - Saves to respective config files
  - Commits generated configs to repository
```

### Example 3: Dynamic Model Selection

```
Scenario: Application selects model based on runtime requirements

Implementation Approach:
  1. Build catalog at application startup
  2. Query catalog for models meeting criteria
  3. Generate spec programmatically
  4. Generate runtime from spec
  5. Initialize LLMHub with generated runtime

Key Functions Used:
  - build_catalog()
  - Model filtering logic
  - generate_runtime_from_spec()
  - LLMHub() from runtime package

Expected Workflow:
  - Application determines requirements (cost, quality, capabilities)
  - Queries catalog for suitable models
  - Constructs SpecConfig object programmatically
  - Generates runtime configuration
  - Uses runtime with LLMHub for LLM calls
```

### Example 4: Configuration Validation in Tests

```
Scenario: Unit tests validate spec and runtime configurations

Implementation Approach:
  1. Load spec from test fixtures
  2. Validate spec structure
  3. Generate runtime
  4. Validate runtime structure
  5. Assert expected properties

Key Functions Used:
  - load_spec(fixture_path)
  - validate_spec(spec)
  - generate_runtime_from_spec(spec)
  - load_runtime(runtime_path)

Expected Workflow:
  - Test suite loads test specs
  - Validates all specs are well-formed
  - Generates runtimes for each
  - Asserts properties match expectations
  - Ensures configuration changes don't break generation
```

## Backward Compatibility

### CLI Commands Remain Unchanged

All existing CLI commands continue to work exactly as before:
- `llmhub catalog refresh`
- `llmhub catalog show`
- `llmhub generate`
- `llmhub runtime show`

### Internal Refactoring Strategy

CLI command implementations will be refactored to:
1. Call the newly exposed public functions
2. Add presentation layer on top (formatting, user interaction)
3. Handle CLI-specific error codes and messaging

Example transformation:
```
Before (everything in command file):
  def catalog_refresh():
      # Build catalog logic
      # Format output
      # Handle errors

After (separated concerns):
  def catalog_refresh():
      catalog = build_catalog(force_refresh=True)  # Public function
      # Format output
      # Handle CLI errors
```

### Import Path Stability

New public functions use stable import paths:
- `from llmhub_cli import build_catalog`
- `from llmhub_cli.catalog import get_catalog`
- `from llmhub_cli.generator import generate_runtime_from_spec`

Internal modules remain internal:
- `llmhub_cli.commands.*` (CLI-specific, not for public use)
- `llmhub_cli.generator_hook` (internal implementation)

## Testing Strategy

### Unit Tests for Public Functions

Each exposed function requires unit tests covering:
- Normal operation with valid inputs
- Error handling with invalid inputs
- Edge cases (empty catalogs, missing files, etc.)
- Return value structure and types

### Integration Tests

Test complete workflows:
- Load spec → Generate runtime → Save runtime → Load runtime
- Build catalog → Filter by provider → Query specific models
- Load spec → Validate → Generate → Validate runtime

### Example Code Tests

Ensure all usage examples in documentation work:
- Examples can be executed as scripts
- All imports resolve correctly
- Expected outputs are produced

### Backward Compatibility Tests

Verify CLI commands still work:
- All CLI commands execute without errors
- CLI command outputs remain consistent
- CLI error handling unchanged

## Documentation Requirements

### API Documentation

Each exposed function needs comprehensive docstrings with:
- One-line summary
- Detailed description of purpose
- Parameter descriptions with types and defaults
- Return value description with type
- Raised exceptions
- Usage examples
- Related functions

### Usage Examples

Create example scripts in examples/ directory:
- `catalog_query_example.py`: Querying catalog programmatically
- `runtime_generation_example.py`: Generating runtime configs
- `multi_environment_example.py`: Managing multiple environments
- `validation_example.py`: Validating configurations

### README Updates

Add "Programmatic API" section to main README covering:
- Overview of exposed functions by category
- Quick reference table
- Links to detailed API docs
- Links to examples
- Comparison with CLI usage

### Migration Guide

Create guide for users transitioning from CLI-only to programmatic usage:
- Common CLI commands and their programmatic equivalents
- Benefits of programmatic access
- Integration patterns
- Troubleshooting

## Risk Assessment

### Potential Risks

| Risk | Severity | Mitigation |
|------|----------|------------|
| Breaking existing internal imports | Medium | Maintain internal module structure, only add new public modules |
| API instability in early versions | Medium | Use semantic versioning, clearly document breaking changes |
| Inconsistent behavior between CLI and API | Low | CLI calls public functions, ensuring identical behavior |
| Documentation drift | Low | Include examples as executable tests |
| Performance regression from added layers | Very Low | New modules only re-export, no additional computation |

### Success Criteria

The implementation is successful when:
1. All CLI operations are available as importable functions
2. Developers can build applications without using CLI
3. CLI commands continue to work without modification
4. API documentation is clear and complete
5. Usage examples demonstrate all major use cases
6. All tests pass with no regressions

## Open Questions

**Q1: Should we expose context resolution (project directory detection) as a public function?**

Analysis: The context module determines project root and config file locations. This could be useful for programmatic access but may introduce complexity around working directory handling.

Recommendation: Start without exposing context resolution. Require explicit paths in public APIs. Add context utilities later if user feedback indicates need.

**Q2: Should validate_spec be synchronous or support async validation?**

Analysis: Current validation is synchronous using Pydantic. Async might be useful for future network-based validation (checking if models exist, verifying API keys).

Recommendation: Start with synchronous validation. Add async variant (validate_spec_async) if future requirements emerge.

**Q3: Should we expose the generator pipeline stages individually?**

Analysis: The generator has multiple stages (needs interpretation, catalog filtering, scoring, selection). Exposing stages allows advanced customization but increases API surface.

Recommendation: Initially expose only the end-to-end generate_runtime_from_spec function. Add stage-level access in future versions if users request fine-grained control.

**Q4: How should we handle environment variable loading in programmatic context?**

Analysis: CLI assumes .env file loading. Library users might manage environment differently (e.g., container orchestration, secret managers).

Recommendation: Document that catalog functions respect environment variables but don't automatically load .env files. Provide optional env_file parameter or let users call dotenv.load_dotenv() explicitly before using library functions.
