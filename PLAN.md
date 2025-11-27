# PLAN-runtime.md — LLMHub Runtime

## 0. Context & Goals

This plan defines the implementation of **`llmhub_runtime`**, a small Python library that lets applications call LLMs **by role name** using a **YAML runtime config**, while delegating all provider-specific logic to **[`any-llm`](TODO: insert any-llm docs URL here)**.

The goals:

- Provide a **stable, lightweight runtime** that:
  - Loads a runtime config file (`llmhub.yaml`).
  - Resolves a **role** (e.g. `llm.inference`) to `{provider, model, mode, params}`.
  - Calls the correct provider via `any-llm` (chat + embedding).
- Be usable both:
  - Inside any **user project** (e.g. memory system, agents, backends).
  - Inside the future **LLM Hub CLI/Web** as its own internal LLM caller.
- Keep concerns clear:
  - This runtime does **no** model discovery, scoring, UI, or spec → runtime generation.
  - It only reads **already-resolved** `llmhub.yaml` and executes calls.

This doc is the **single source of truth** for the `llmhub_runtime` package.

---

## 1. Tech Stack & External Dependencies

### Language & runtime

- Python ≥ 3.10

### Core dependencies

- `any-llm`
  - Used for all provider-specific LLM calls (chat/completion & embeddings).
  - Runtime must **not** re-implement SDK integrations; it should use `any-llm`.
- `PyYAML`
  - For loading the `llmhub.yaml` runtime config.
- `pydantic` (v1 or v2, v2 preferred)
  - For schema validation + type-safe runtime configuration models.

### Testing & tooling (baseline)

- `pytest` for unit tests.
- `mypy` (optional but recommended) for basic type checking.
- `ruff` or `flake8` (optional) for linting.

---

## 2. Runtime Config Schema (llmhub.yaml)

This runtime config is **generated** by higher-level tools and treated as **read-only** by `llmhub_runtime`.

### Expected structure (v0)

Example:

    # llmhub.yaml
    # GENERATED FILE – DO NOT EDIT BY HAND
    project: memory
    env: dev

    providers:
      openai:
        env_key: OPENAI_API_KEY
      anthropic:
        env_key: ANTHROPIC_API_KEY
      mistral:
        env_key: MISTRAL_API_KEY
      openrouter:
        env_key: OPENROUTER_API_KEY

    roles:
      llm.preprocess:
        provider: openai
        model: gpt-4o-mini
        mode: chat
        params:
          temperature: 0.2
          max_tokens: 512

      llm.memwrite:
        provider: anthropic
        model: claude-3-5-sonnet-20241022
        mode: chat
        params:
          temperature: 0.3
          max_tokens: 1024

      llm.memread:
        provider: anthropic
        model: claude-3-5-sonnet-20241022
        mode: chat
        params:
          temperature: 0.5
          max_tokens: 2048

      llm.inference:
        provider: openai
        model: gpt-4.1
        mode: chat
        params:
          temperature: 0.7
          max_tokens: 2048

      llm.embedding:
        provider: openai
        model: text-embedding-3-small
        mode: embedding
        params:
          embedding_dim: 1536

    defaults:
      # optional fallback if a role is missing; may be omitted by generator
      provider: openai
      model: gpt-4o-mini
      mode: chat
      params:
        temperature: 0.3
        max_tokens: 1024

### Semantics

- `project`: logical project name (for logging / debugging).
- `env`: environment (e.g. `dev`, `staging`, `prod`).
- `providers`:
  - key = provider id as understood by `any-llm` (e.g. `"openai"`, `"anthropic"`).
  - `env_key` (optional): name of the environment variable for that provider’s API key.
    - Runtime may use this for validation.
- `roles`:
  - key = role name (e.g. `"llm.inference"`).
  - `provider`: provider id (must match a key in `providers`).
  - `model`: full model name as expected by `any-llm`.
  - `mode`: `"chat"`, `"embedding"`, `"image"`, `"audio"`, `"tool"`, `"other"`.
  - `params`: default LLM parameters (temperature, max_tokens, etc.).
- `defaults` (optional):
  - Global fallback role binding used when:
    - A requested role is missing and we choose not to hard-fail.

---

## 3. Package Layout (llmhub_runtime)

Target layout under `src/llmhub_runtime`:

    src/llmhub_runtime/
      __init__.py
      models.py
      config_loader.py
      resolver.py
      hub.py
      errors.py

Additionally:

    tests/
      test_config_loader.py
      test_resolver.py
      test_hub_basic.py

The following sections describe **each module as a subproblem** with a spec sheet (inputs, outputs, description, interfaces).

---

## 4. Subproblem Spec Sheets

### SP1 — Models & Runtime Schema (`models.py`)

**Goal:** Define strong, validated Python representations of the runtime config and resolved calls.

#### Inputs

- Raw Python dictionaries resulting from YAML loading (from `config_loader`).
- Should match the high-level schema of `llmhub.yaml`.

#### Outputs

- Validated Pydantic models:
  - `RuntimeConfig`
  - `ProviderConfig`
  - `RoleConfig`
  - `RoleDefaultsConfig` (for `defaults`)
  - `ResolvedCall`
  - Enums for `LLMMode` where needed.

#### Description

- Central definition of all types the runtime works with.
- Ensures `llmhub.yaml` values conform to expectations.
- Provides helpful error messages when required fields are missing or invalid.

#### Model Interfaces

- `class LLMMode(str, Enum)`:
  - Values: `"chat"`, `"embedding"`, `"image"`, `"audio"`, `"tool"`, `"other"`.

- `class ProviderConfig(BaseModel)`:
  - Fields:
    - `env_key: Optional[str] = None`

- `class RoleConfig(BaseModel)`:
  - Fields:
    - `provider: str`
    - `model: str`
    - `mode: LLMMode`
    - `params: Dict[str, Any] = {}`

- `class RoleDefaultsConfig(BaseModel)`:
  - Same fields as `RoleConfig` but used for global `defaults`.

- `class RuntimeConfig(BaseModel)`:
  - Fields:
    - `project: str`
    - `env: str`
    - `providers: Dict[str, ProviderConfig]`
    - `roles: Dict[str, RoleConfig]`
    - `defaults: Optional[RoleDefaultsConfig] = None`

- `class ResolvedCall(BaseModel)`:
  - Fields:
    - `role: str`
    - `provider: str`
    - `model: str`
    - `mode: LLMMode`
    - `params: Dict[str, Any]`

#### Notes

- Validation should be strict enough to catch common mistakes, but not over-constrained.
- Use Pydantic’s `model_validate` / `validate_model` patterns as appropriate.

---

### SP2 — Config Loader (`config_loader.py`)

**Goal:** Load and validate `llmhub.yaml` into a `RuntimeConfig` instance.

#### Inputs

- File path to `llmhub.yaml` (string).
- Optionally, a Python `dict` already parsed from YAML.

#### Outputs

- A fully validated `RuntimeConfig` object.
- Raises `ConfigError` (from `errors.py`) on invalid configs.

#### Description

- Single entry point for reading runtime configuration from disk.
- Handles YAML parsing and wraps validation errors into domain-specific exceptions.

#### Interfaces

- `def load_runtime_config(path: str) -> RuntimeConfig`:
  - Steps:
    - Open and read YAML.
    - Use `yaml.safe_load`.
    - Validate via `RuntimeConfig.model_validate(...)`.
    - On any validation/parsing failures, raise `ConfigError`.

- `def parse_runtime_config(data: Dict[str, Any]) -> RuntimeConfig`:
  - For in-memory use (e.g. tests or future CLI).
  - Same validation logic without file I/O.

#### Notes

- No knowledge of `any-llm` here.
- This module should be pure configuration handling.

---

### SP3 — Role Resolver (`resolver.py`)

**Goal:** Map a logical `role` name to a concrete `{provider, model, mode, params}`.

#### Inputs

- A `RuntimeConfig` object.
- A `role` string.
- Optional `params_override: Dict[str, Any]`.

#### Outputs

- A `ResolvedCall` instance populated with:
  - `role`
  - `provider`
  - `model`
  - `mode`
  - merged `params` (role defaults + override).

#### Description

- Encapsulates all logic for:
  - Ensuring the role exists.
  - Verifying that the provider referenced by the role is defined in `providers`.
  - Falling back to `defaults` when the role is missing, if configured.
- This is where decisions about “hard fail vs fallback” live.

#### Interfaces

- `def resolve_role(config: RuntimeConfig, role: str, params_override: Optional[Dict[str, Any]] = None) -> ResolvedCall`:
  - Behaviour:
    - If `role` in `config.roles`:
      - Base = `config.roles[role]`.
    - Else if `config.defaults` is not None:
      - Base = `config.defaults`.
    - Else:
      - Raise `UnknownRoleError`.
    - Verify `base.provider` exists in `config.providers`, else `UnknownProviderError`.
    - Merge `params = {**base.params, **(params_override or {})}`.
    - Return `ResolvedCall(...)`.

#### Notes

- Keep resolver fully stateless and pure; side-effect free.
- Logging (if needed) should be done at a higher level (hub).

---

### SP4 — Errors (`errors.py`)

**Goal:** Provide clear, domain-specific exceptions used throughout the runtime.

#### Inputs

- Errors from YAML parsing, Pydantic validation, or runtime resolution issues.

#### Outputs

- Meaningful Python exceptions with human-readable messages.

#### Description

- Wraps generic errors into a small set of public exception types.

#### Interfaces

- `class LLMHubRuntimeError(Exception)`:
  - Base class for all runtime errors.

- `class ConfigError(LLMHubRuntimeError)`:
  - For invalid or unreadable configs.

- `class UnknownRoleError(LLMHubRuntimeError)`:
  - When an unknown role is requested and no default is configured.

- `class UnknownProviderError(LLMHubRuntimeError)`:
  - When a role references a provider that isn’t defined in `providers`.

- `class EnvVarMissingError(LLMHubRuntimeError)`:
  - If runtime chooses to validate `env_key` and the required env var is missing (optional behaviour).

#### Notes

- All modules (`config_loader`, `resolver`, `hub`) should raise these errors rather than generic exceptions.

---

### SP5 — LLMHub Client (`hub.py`)

**Goal:** Provide the main public API (`LLMHub`) that applications use to perform LLM calls by role.

#### Inputs

- `RuntimeConfig` (via file or in-memory).
- `role` names.
- Chat messages / embedding inputs.
- Optional per-call param overrides.
- Optional hooks for logging/metrics.

#### Outputs

- LLM responses from `any-llm` (for chat/embedding).
- Streamed chunks (if streaming is implemented later).

#### Description

- This is the primary interface that user code uses.
- It:
  - Loads/parses config (delegating to `config_loader`).
  - Resolves roles (delegating to `resolver`).
  - Calls `any-llm` for chat and embeddings.
  - Optionally validates environment variables based on `env_key`.

#### Public Interfaces

`class LLMHub:`

Constructor:

    def __init__(
        self,
        config_path: Optional[str] = None,
        config_obj: Optional[RuntimeConfig] = None,
        strict_env: bool = False,
        on_before_call: Optional[Callable[[CallContext], None]] = None,
        on_after_call: Optional[Callable[[CallResult], None]] = None,
    )

- Exactly one of `config_path` or `config_obj` must be provided.
- `strict_env`:
  - If `True`, check that all `env_key` vars exist on init and raise `EnvVarMissingError` if not.
  - If `False`, skip env validation (let provider/any-llm fail).
- `on_before_call` / `on_after_call`:
  - Hooks for logging/metrics (can be `None`).

Methods (sync):

    def completion(
        self,
        role: str,
        messages: List[Dict[str, Any]],
        params_override: Optional[Dict[str, Any]] = None,
    ) -> Any: ...

    def embedding(
        self,
        role: str,
        input: Union[str, List[str]],
        params_override: Optional[Dict[str, Any]] = None,
    ) -> Any: ...

Methods (async) – v0 or v0.1:

    async def acompletion(...): ...
    async def aembedding(...): ...

Optional streaming (future):

    def stream_completion(...): -> Iterator[Any]
    async def astream_completion(...): -> AsyncIterator[Any]

`CallContext` / `CallResult` (internal types, could be defined in `models.py` or `hub.py`):

- `CallContext`:
  - `role`, `provider`, `model`, `mode`, `params`, `messages` or `input`.
- `CallResult`:
  - `role`, `provider`, `model`, `mode`, `duration_ms`, `success`, `error` (if any), and the raw response.

#### Internal behaviour

- On init:
  - Load/validate config via `config_loader` if `config_path` is provided.
  - Optionally validate env vars (`strict_env`).
- On `completion`:
  1. Resolve role → `ResolvedCall` via `resolver`.
  2. Compose `CallContext`, call `on_before_call` if provided.
  3. Call `any_llm.completion(provider=..., model=..., messages=..., **params)`.
  4. Compose `CallResult`, call `on_after_call` if provided.
  5. Return raw `any-llm` response.
- On `embedding`:
  - Similar, but calls `any_llm.embedding`.

#### Notes

- Do **not** re-wrap `any-llm` responses into custom types; just pass them through.
- Keep this module as thin as possible; all mapping logic lives in `resolver`.

---

### SP6 — Tests (basic coverage)

**Goal:** Ensure the core behaviour is correct and stable.

#### Inputs

- Sample `llmhub.yaml` configs (stored under `tests/fixtures`).
- Mock / patched `any_llm` calls.

#### Outputs

- Unit tests verifying behaviour:
  - Correct config loading and validation.
  - Resolution logic (role → provider/model/params).
  - Error handling for missing roles/providers.
  - `LLMHub` wiring (ensuring it calls `any_llm` with expected arguments).

#### Notes

- Use mocking (e.g. `unittest.mock`) to avoid making real network calls.
- Cover both success paths and failure paths (invalid config, unknown roles, missing env).

---

## 5. Implementation Order

Recommended order of implementation:

1. **SP1**: `models.py`
2. **SP2**: `config_loader.py`
3. **SP4**: `errors.py` (can be done alongside SP1/2)
4. **SP3**: `resolver.py`
5. **SP5**: `hub.py`
6. **SP6**: Tests

At each step:

- Ensure the module imports cleanly.
- Add minimal tests to validate behaviour.

---

## 6. README.md Content for llmhub_runtime

The project must include a `README.md` that explains:

- What `llmhub_runtime` is.
- How the config works.
- Basic usage examples.
- Internal architecture at a glance.

### README.md — Draft Content

(This is to be written into `README.md` in the repository.)

    # llmhub_runtime

    `llmhub_runtime` is a small Python library that lets you call LLMs **by role** using a simple YAML config (`llmhub.yaml`), while delegating all provider-specific logic to [`any-llm`](TODO: insert any-llm docs URL here).

    It is designed to be:

    - **Runtime-light** – minimal dependencies, no discovery logic.
    - **Provider-agnostic** – supports any provider that `any-llm` supports.
    - **Role-centric** – your application code never handles provider/model strings directly.

    `llmhub_runtime` is intended for:

    - Application backends (e.g. memory systems, agents, tools).
    - The future `llmhub` CLI/Web tool, which will generate `llmhub.yaml` and then use this runtime internally.

    ## Installation

        pip install llmhub-runtime any-llm

    (Exact package name to be confirmed when publishing.)

    ## Runtime Config: `llmhub.yaml`

    `llmhub_runtime` reads a **generated** config file, typically named `llmhub.yaml`:

        project: memory
        env: dev

        providers:
          openai:
            env_key: OPENAI_API_KEY
          anthropic:
            env_key: ANTHROPIC_API_KEY

        roles:
          llm.preprocess:
            provider: openai
            model: gpt-4o-mini
            mode: chat
            params:
              temperature: 0.2
              max_tokens: 512

          llm.inference:
            provider: anthropic
            model: claude-3-5-sonnet-20241022
            mode: chat
            params:
              temperature: 0.7
              max_tokens: 2048

    You typically do **not** edit this by hand; it is generated by higher-level tools (e.g. `llmhub` CLI/Web).

    ## Basic Usage

        from llmhub_runtime import LLMHub

        hub = LLMHub(config_path="llmhub.yaml")

        response = hub.completion(
            role="llm.inference",
            messages=[{"role": "user", "content": "Hello"}],
        )

        print(response)

    Embeddings:

        embedding = hub.embedding(
            role="llm.embedding",
            input="Hello world",
        )

    To override parameters per call:

        response = hub.completion(
            role="llm.inference",
            messages=[...],
            params_override={"temperature": 0.1},
        )

    ## Architecture Overview

    `llmhub_runtime` is intentionally small and has three main layers:

    1. **Config layer**  
       - `models.py` – Pydantic models for `RuntimeConfig`, `ProviderConfig`, `RoleConfig`, `ResolvedCall`.  
       - `config_loader.py` – loads and validates `llmhub.yaml`.

    2. **Resolution layer**  
       - `resolver.py` – maps a logical `role` name to `{provider, model, mode, params}`, with optional fallback from `defaults`.

    3. **Execution layer**  
       - `hub.py` – exposes the `LLMHub` class:
         - Resolves roles.
         - Calls `any-llm` (`completion` / `embedding`) with the resolved settings.
         - Optional hooks for logging/metrics.

    All domain-specific errors live in `errors.py`.

    ## Design Principles

    - **No provider logic** – `llmhub_runtime` never talks to provider SDKs directly; it only calls `any-llm`.
    - **No discovery or scoring** – it assumes `llmhub.yaml` already contains concrete provider/model choices.
    - **Role-first** – application code only sees role names; you can swap models by editing/generating `llmhub.yaml` without changing app code.

    ## Roadmap

    - Async APIs (`acompletion`, `aembedding`).
    - Streaming interfaces.
    - More modes (`image`, `audio`, `tool`).
    - Tight integration with the `llmhub` CLI/Web for config generation.

---

## 7. Final Notes

- This plan is **only** for the `llmhub_runtime` package.
- The future `llmhub` CLI/Web tool will:
  - Work with `llmhub.spec.yaml` (human-facing spec).
  - Use `llmhub_runtime` internally for its own LLM calls.
  - Generate `llmhub.yaml` files consumed by this runtime.

All implementation should strictly follow the structure and interfaces described above.