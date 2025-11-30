# API Reference

<cite>
**Referenced Files in This Document**   
- [hub.py](file://packages/llmhub_runtime/src/llmhub_runtime/hub.py)
- [models.py](file://packages/llmhub_runtime/src/llmhub_runtime/models.py)
- [config_loader.py](file://packages/llmhub_runtime/src/llmhub_runtime/config_loader.py)
- [resolver.py](file://packages/llmhub_runtime/src/llmhub_runtime/resolver.py)
- [schema.py](file://packages/llmhub/src/llmhub/catalog/schema.py)
- [builder.py](file://packages/llmhub/src/llmhub/catalog/builder.py)
- [cache.py](file://packages/llmhub/src/llmhub/catalog/cache.py)
- [__init__.py](file://packages/llmhub/src/llmhub/generator/__init__.py)
- [sp9_selector_orchestrator/models.py](file://packages/llmhub/src/llmhub/generator/sp9_selector_orchestrator/models.py)
</cite>

## Table of Contents
1. [Runtime Library](#runtime-library)
2. [Generator Module](#generator-module)
3. [Catalog System](#catalog-system)
4. [Versioning and Stability](#versioning-and-stability)

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
- [__init__.py](file://packages/llmhub/src/llmhub/generator/__init__.py#L52-L118)

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

## Catalog System

The catalog system provides a comprehensive database of available LLM models with enriched metadata, pricing, quality scores, and capabilities.

### Catalog Class

The `Catalog` class represents the complete collection of available models with their metadata.

**Section sources**
- [schema.py](file://packages/llmhub/src/llmhub/catalog/schema.py#L117-L122)
- [builder.py](file://packages/llmhub/src/llmhub/catalog/builder.py#L302-L388)

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
1. Loads .env file to ensure API keys are available
2. Checks for a fresh cached catalog
3. Fetches data from multiple sources (any-llm, models.dev, LMArena)
4. Fuses the data sources using ID mapping
5. Computes global statistics for tier derivation
6. Derives canonical models with quality, reasoning, creative, and cost tiers
7. Saves the catalog to cache
8. Returns the complete catalog

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

## Versioning and Stability

The LLM Hub ecosystem follows semantic versioning principles with stability guarantees for public APIs.

### Runtime Library Stability

The runtime library (`llmhub_runtime`) provides stable APIs with backward compatibility guarantees:

- The `LLMHub` class interface is stable and will maintain backward compatibility within major versions.
- The `RuntimeConfig` and `ResolvedCall` models are stable and will not have breaking changes within major versions.
- Hook interfaces (`CallContext` and `CallResult`) are stable and will maintain backward compatibility.

### Generator Module Stability

The generator module provides stable entry points with defined compatibility:

- The `generate_machine_config` function is the primary stable interface.
- The `ProjectSpec`, `RoleNeed`, `SelectionResult`, and `MachineConfig` models are stable.
- Subproblem APIs may evolve between minor versions with appropriate deprecation notices.

### Catalog System Stability

The catalog system maintains backward compatibility for data models:

- The `Catalog` and `CanonicalModel` schemas are stable.
- Field additions are non-breaking and will not remove existing fields within major versions.
- Tier derivation algorithms may be refined between versions, but the tier scale (1-5) remains consistent.

**Section sources**
- [__init__.py](file://packages/llmhub_runtime/src/llmhub_runtime/__init__.py#L1-L6)
- [__init__.py](file://packages/llmhub/src/llmhub/catalog/__init__.py#L1-L17)
- [__init__.py](file://packages/llmhub/src/llmhub/generator/__init__.py#L120-L145)