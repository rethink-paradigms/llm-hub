# API Reference

<cite>
**Referenced Files in This Document**   
- [hub.py](file://packages/llmhub_runtime/src/llmhub_runtime/hub.py)
- [models.py](file://packages/llmhub_runtime/src/llmhub_runtime/models.py)
- [config_loader.py](file://packages/llmhub_runtime/src/llmhub_runtime/config_loader.py)
- [resolver.py](file://packages/llmhub_runtime/src/llmhub_runtime/resolver.py)
- [schema.py](file://packages/cli/src/llmhub_cli/catalog/schema.py)
- [builder.py](file://packages/cli/src/llmhub_cli/catalog/builder.py)
- [cache.py](file://packages/cli/src/llmhub_cli/catalog/cache.py)
- [__init__.py](file://packages/cli/src/llmhub_cli/generator/__init__.py)
- [__init__.py](file://packages/cli/src/llmhub_cli/catalog/__init__.py)
- [__init__.py](file://packages/cli/src/llmhub_cli/spec/__init__.py)
</cite>

## Table of Contents
1. [Runtime Library](#runtime-library)
2. [Generator Module](#generator-module)
3. [Catalog System](#catalog-system)
4. [Spec Module](#spec-module)
5. [Versioning and Stability](#versioning-and-stability)

## Runtime Library

The runtime library provides the core interface for interacting with LLM providers through the `LLMHub` class. It handles configuration loading, role resolution, and API calls to underlying LLM providers.

### LLMHub Class

The `LLMHub` class is the main entry point for the runtime library, providing methods to perform completions and embeddings using configured LLM roles.

**Section sources**
- [hub.py](file://packages/llmhub_runtime/src/llmhub_runtime/hub.py#L17-L189)
- [models.py](file://packages/llmhub_runtime/src/llmhub_runtime/models.py#L28-L40)

#### __init__ Parameters

```python
def __init__(
    self,
    config_path: Optional[str] = None,
    config_obj: Optional[RuntimeConfig] = None,
    strict_env: bool = False,
    on_before_call: Optional[Callable[[CallContext], None]] = None,
    on_after_call: Optional[Callable[[CallResult], None]] = None,
)
```

- `config_path`: Path to the llmhub.yaml configuration file. Required if `config_obj` is not provided.
- `config_obj`: Pre-loaded `RuntimeConfig` object. Required if `config_path` is not provided.
- `strict_env`: If True, validates that all required environment variables exist during initialization.
- `on_before_call`: Hook function that executes before each LLM call, receiving a `CallContext` dictionary.
- `on_after_call`: Hook function that executes after each LLM call, receiving a `CallResult` dictionary.

**Raises:**
- `ValueError`: If neither or both `config_path` and `config_obj` are provided.
- `EnvVarMissingError`: If `strict_env` is True and a required environment variable is missing.

#### completion() Method

```python
def completion(
    self,
    role: str,
    messages: List[Dict[str, Any]],
    params_override: Optional[Dict[str, Any]] = None,
) -> Any
```

Performs a chat completion using the specified role configuration.

**Parameters:**
- `role`: The logical role name defined in the configuration.
- `messages`: List of message dictionaries with 'role' and 'content' keys.
- `params_override`: Optional dictionary of parameters to override the role's default parameters.

**Returns:**
- The raw response from the underlying LLM provider via any-llm.

**Raises:**
- `ImportError`: If the any-llm-sdk package is not installed.
- Various exceptions from the underlying LLM provider.

#### embedding() Method

```python
def embedding(
    self,
    role: str,
    input: Union[str, List[str]],
    params_override: Optional[Dict[str, Any]] = None,
) -> Any
```

Generates embeddings for the given input using the specified role configuration.

**Parameters:**
- `role`: The logical role name defined in the configuration.
- `input`: Input text or list of texts to generate embeddings for.
- `params_override`: Optional dictionary of parameters to override the role's default parameters.

**Returns:**
- The raw response from the underlying LLM provider via any-llm.

**Raises:**
- `ImportError`: If the any-llm-sdk package is not installed.
- Various exceptions from the underlying LLM provider.

### Hook Function Signatures

The runtime library supports pre-call and post-call hooks for monitoring, logging, or modifying behavior.

#### CallContext

The `CallContext` type is a dictionary containing information about an upcoming LLM call:

```python
CallContext = Dict[str, Any]
```

**Keys:**
- `role`: The logical role name being called.
- `provider`: The actual LLM provider (e.g., "openai", "anthropic").
- `model`: The specific model identifier (e.g., "gpt-4-turbo").
- `mode`: The operation mode ("chat", "embedding", etc.).
- `params`: Dictionary of API parameters to be sent.
- `messages`: List of chat messages (for completion calls).
- `input`: Input text(s) (for embedding calls).

#### CallResult

The `CallResult` type is a dictionary containing information about a completed LLM call:

```python
CallResult = Dict[str, Any]
```

**Keys:**
- `role`: The logical role name that was called.
- `provider`: The actual LLM provider used.
- `model`: The specific model that was called.
- `mode`: The operation mode.
- `success`: Boolean indicating whether the call succeeded.
- `error`: Exception object if the call failed, otherwise None.
- `response`: The response from the LLM provider if successful, otherwise None.

## Generator Module

The generator module provides functionality to convert high-level specifications into concrete runtime configurations.

### Main Entry Points

The generator module exposes several entry points through its `__init__.py` file.

**Section sources**
- [__init__.py](file://packages/cli/src/llmhub_cli/generator/__init__.py#L52-L118)

#### generate_machine_config Function

```python
def generate_machine_config(
    spec_path: str,
    hub: LLMHub,
    output_path: Optional[str] = None,
    catalog_override: Optional[List[CanonicalModel]] = None,
    catalog_ttl_hours: int = 24,
    force_catalog_refresh: bool = False,
    selector_options: Optional[SelectorOptions] = None
) -> MachineConfig
```

Main end-to-end function that converts a human-written specification into a machine-readable configuration.

**Parameters:**
- `spec_path`: Path to the llmhub.spec.yaml file.
- `hub`: LLMHub instance used for LLM calls during generation.
- `output_path`: Optional path to write the generated llmhub.yaml file.
- `catalog_override`: Optional list of CanonicalModel objects to use instead of loading the catalog.
- `catalog_ttl_hours`: Cache TTL in hours for the model catalog.
- `force_catalog_refresh`: If True, forces rebuilding the catalog cache.
- `selector_options`: Options for controlling model selection behavior.

**Returns:**
- `MachineConfig` object ready for runtime use.

**Raises:**
- `GeneratorError`: If any step in the generation process fails.

#### generate_runtime_from_spec Function

```python
def generate_runtime_from_spec(
    spec,
    options: Optional[GeneratorOptions] = None
) -> GenerationResult
```

Generates a runtime configuration from a spec configuration using either heuristic-only mode or LLM-assisted selection.

**Parameters:**
- `spec`: SpecConfig object with role definitions and preferences.
- `options`: Optional GeneratorOptions to control generation behavior:
  - `no_llm` (bool): Use heuristic-only mode without LLM assistance.
  - `explain` (bool): Include explanations for model selections.

**Returns:**
- `GenerationResult` object containing:
  - `runtime` (RuntimeConfig): Generated runtime configuration with concrete provider/model mappings for each role.
  - `explanations` (dict[str, str]): Role selection explanations (only populated if options.explain=True).

**Example:**
```python
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
```

**Section sources**
- [__init__.py](file://packages/cli/src/llmhub_cli/generator/__init__.py#L126-L183)

## Catalog System

The catalog system provides a comprehensive database of available LLM models with enriched metadata, pricing, quality scores, and capabilities.

### Catalog Class

The `Catalog` class represents the complete collection of available models with their metadata.

**Section sources**
- [schema.py](file://packages/cli/src/llmhub_cli/catalog/schema.py#L117-L122)
- [builder.py](file://packages/cli/src/llmhub_cli/catalog/builder.py#L302-L388)

#### Catalog Schema

```python
class Catalog(BaseModel):
    catalog_version: int = 1
    built_at: str
    models: list[CanonicalModel] = Field(default_factory=list)
```

**Attributes:**
- `catalog_version`: Version number of the catalog format.
- `built_at`: ISO timestamp when the catalog was built.
- `models`: List of `CanonicalModel` objects representing available models.

### Catalog Methods

The catalog system provides several methods for loading, refreshing, and querying models.

#### build_catalog Function

```python
def build_catalog(
    ttl_hours: int = 24,
    force_refresh: bool = False
) -> Catalog
```

Main entry point for building the complete model catalog.

**Parameters:**
- `ttl_hours`: Cache TTL in hours. If the cache is younger than this, it will be used.
- `force_refresh`: If True, ignores the cache and rebuilds the catalog from source data.

**Returns:**
- `Catalog` object containing all available models with enriched metadata.

**Process:**
1. Loads .env file to ensure API keys are available.
2. Checks for a fresh cached catalog.
3. Fetches data from multiple sources (any-llm, models.dev, LMArena).
4. Fuses the data sources using ID mapping.
5. Computes global statistics for tier derivation.
6. Derives canonical models with quality, reasoning, creative, and cost tiers.
7. Saves the catalog to cache.
8. Returns the complete catalog.

#### get_catalog Function

```python
def get_catalog(
    ttl_hours: int = 24,
    force_refresh: bool = False,
    provider: Optional[str] = None,
    tags: Optional[List[str]] = None
) -> Catalog
```

Convenience function that builds the catalog and applies filtering in one call.

**Parameters:**
- `ttl_hours`: Cache TTL in hours, default 24.
- `force_refresh`: If True, ignore cache and rebuild, default False.
- `provider`: Optional provider name to filter by (e.g., "openai").
- `tags`: Optional list of tags to filter by (models must have all tags).

**Returns:**
- `Catalog` object with filtered models (or all models if no filters).

**Example:**
```python
>>> from llmhub_cli import get_catalog
>>> 
>>> # Get all models
>>> catalog = get_catalog()
>>> 
>>> # Get all OpenAI models
>>> openai_catalog = get_catalog(provider="openai")
>>> print(f"Found {len(openai_catalog.models)} OpenAI models")
>>> 
>>> # Get models with reasoning capability
>>> reasoning_catalog = get_catalog(tags=["reasoning"])
>>> for model in reasoning_catalog.models:
...     print(f"{model.provider}:{model.model_id} - Tier {model.reasoning_tier}")
>>> 
>>> # Get OpenAI models with vision support
>>> vision_catalog = get_catalog(provider="openai", tags=["vision"])
>>> 
>>> # Force fresh rebuild with filtering
>>> fresh_catalog = get_catalog(force_refresh=True, provider="anthropic")
```

**Section sources**
- [__init__.py](file://packages/cli/src/llmhub_cli/catalog/__init__.py#L12-L84)

#### load_cached_catalog Function

```python
def load_cached_catalog(ttl_hours: int = 24) -> Optional[Catalog]
```

Loads a cached catalog if it exists and is fresh.

**Parameters:**
- `ttl_hours`: Maximum age in hours for the cache to be considered fresh.

**Returns:**
- `Catalog` object if a fresh cache exists, otherwise `None`.

#### clear_cache Function

```python
def clear_cache() -> bool
```

Clears the catalog cache.

**Returns:**
- `True` if cache was cleared, `False` if no cache existed.

## Spec Module

The spec module provides programmatic access to spec file operations, allowing developers to load, validate, and work with spec configurations without using the CLI.

### Main Entry Points

The spec module exposes functions through its `__init__.py` file for loading and validating specification files.

**Section sources**
- [__init__.py](file://packages/cli/src/llmhub_cli/spec/__init__.py#L30-L207)

#### load_spec Function

```python
def load_spec(spec_path: Union[str, Path]) -> SpecConfig
```

Loads and validates a spec configuration from a YAML file.

**Parameters:**
- `spec_path`: Path to the spec YAML file (string or Path object).

**Returns:**
- `SpecConfig` object with validated configuration containing:
  - `project`: Project name.
  - `env`: Environment name (dev, staging, prod, etc.).
  - `providers`: Dictionary of provider configurations.
  - `roles`: Dictionary of role specifications.
  - `defaults`: Optional default configurations.

**Raises:**
- `SpecError`: If file not found, cannot be parsed, or validation fails.

**Example:**
```python
>>> from llmhub_cli.spec import load_spec
>>> 
>>> # Load spec file
>>> spec = load_spec("llmhub.spec.yaml")
>>> 
>>> # Access spec properties
>>> print(f"Project: {spec.project}")
>>> print(f"Roles: {list(spec.roles.keys())}")
>>> 
>>> # Iterate through roles
>>> for role_name, role_spec in spec.roles.items():
...     print(f"  {role_name}: {role_spec.kind} - {role_spec.description}")
```

#### validate_spec Function

```python
def validate_spec(spec: Union[SpecConfig, str, Path]) -> ValidationResult
```

Validates a spec configuration and returns detailed results.

**Parameters:**
- `spec`: Either a `SpecConfig` object or path to a spec file.

**Returns:**
- `ValidationResult` object containing:
  - `valid` (bool): True if spec is valid.
  - `errors` (list[str]): List of validation error messages.
  - `warnings` (list[str]): List of validation warnings.

**Example:**
```python
>>> from llmhub_cli.spec import validate_spec
>>> 
>>> # Validate from file path
>>> result = validate_spec("llmhub.spec.yaml")
>>> 
>>> if result.valid:
...     print("Spec is valid")
... else:
...     print("Validation errors:")
...     for error in result.errors:
...         print(f"  - {error}")
>>> 
>>> # Validate existing SpecConfig object
>>> from llmhub_cli.spec import load_spec
>>> spec = load_spec("llmhub.spec.yaml")
>>> result = validate_spec(spec)
```

#### ValidationResult Class

```python
class ValidationResult(BaseModel):
    valid: bool
    errors: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
```

Represents the result of spec validation with success status, errors, and warnings.

## Versioning and Stability

The LLM Hub ecosystem follows semantic versioning principles with stability guarantees for public APIs.

### Runtime Library Stability

The runtime library (`llmhub_runtime`) provides stable APIs with backward compatibility guarantees:

- The `LLMHub` class interface is stable and will maintain backward compatibility within major versions.
- The `RuntimeConfig` and `ResolvedCall` models are stable and will not have breaking changes within major versions.
- Hook interfaces (`CallContext` and `CallResult`) are stable and will maintain backward compatibility.

### Generator Module Stability

The generator module provides stable entry points with defined compatibility:

- The `generate_machine_config` and `generate_runtime_from_spec` functions are primary stable interfaces.
- The `ProjectSpec`, `RoleNeed`, `SelectionResult`, `MachineConfig`, `GeneratorOptions`, and `GenerationResult` models are stable.
- Subproblem APIs may evolve between minor versions with appropriate deprecation notices.

### Catalog System Stability

The catalog system maintains backward compatibility for data models:

- The `Catalog` and `CanonicalModel` schemas are stable.
- Field additions are non-breaking and will not remove existing fields within major versions.
- Tier derivation algorithms may be refined between versions, but the tier scale (1-5) remains consistent.

### Spec Module Stability

The spec module provides stable programmatic access to specification operations:

- The `load_spec` and `validate_spec` functions are stable public interfaces.
- The `SpecConfig`, `ProviderSpec`, `RoleSpec`, and `PreferencesSpec` models are stable.
- Validation rules and error reporting through `ValidationResult` are stable.

**Section sources**
- [__init__.py](file://packages/llmhub_runtime/src/llmhub_runtime/__init__.py#L1-L6)
- [__init__.py](file://packages/cli/src/llmhub_cli/catalog/__init__.py#L1-L17)
- [__init__.py](file://packages/cli/src/llmhub_cli/generator/__init__.py#L120-L145)
- [__init__.py](file://packages/cli/src/llmhub_cli/spec/__init__.py#L196-L207)