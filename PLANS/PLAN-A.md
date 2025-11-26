# PLAN-A.md  
Unified LLM Orchestrator – Core Engine (Config + Resolution + Unified Run API)

## 1. Objective

Implement the core execution engine of the unified LLM Orchestrator as a single library that:

- Reads a config file for one project/env.
- Resolves provider + model selection for a given `(project, env, role)`.
- Exposes a single `run()` function that apps call.
- Calls providers through a minimal adapter layer.

No UI, no dynamic discovery, no recommendations, no advanced logic in PLAN-A.  
Just the backbone needed for real usage and examples.

---

## 2. Directory Structure (initial skeleton)

orchestrator/  
  plan/  
    PLAN-A.md  
  src/  
    config/  
      loader.py  
      schema.py  
    resolution/  
      resolver.py  
    providers/  
      base.py  
      openai_adapter.py  
      gemini_adapter.py  
      anthropic_adapter.py  
      deepseek_adapter.py  
      qwen_adapter.py  
      openrouter_adapter.py  
    runtime/  
      llm_client.py  
      types.py  
    utils/  
      env.py  
      errors.py  
  examples/  
    minimal_app/  
      llm_orchestrator.yaml  
      llm_bindings.py  

Adapters can stay minimal/mocked for now but must expose the correct interface shape.

---

## 3. Config Structure (YAML Schema v1 for PLAN-A)

### File: `llm_orchestrator.yaml`

This is the only required config file for PLAN-A.  
Single-project, single-env, explicit bindings (no discovery yet).

Example:

project: my_project  
env: dev  

providers:  
  openai:  
    auth_profile: openai_default  
    api_base: https://api.openai.com/v1  
  gemini:  
    auth_profile: gemini_default  
    api_base: https://generativelanguage.googleapis.com  
  anthropic:  
    auth_profile: anthropic_default  
    api_base: https://api.anthropic.com  

roles:  
  llm.preprocess:  
    provider: openai  
    model: gpt-4.1-mini  
  llm.inference:  
    provider: openai  
    model: gpt-4.1  
  llm.embedding:  
    provider: openai  
    model: text-embedding-3-large  

PLAN-A keeps this explicit. Later plans can switch to selectors and dynamic discovery.

---

## 4. I/O Expectations

### Input to the orchestrator core

- Path to `llm_orchestrator.yaml`.
- At runtime: a `run()` call with:
  - `role: str`
  - `messages: List[Message]` where `Message = { "role": "system"|"user"|"assistant", "content": str }`.
  - Optional `params_override: dict` for temperature/max_tokens etc.

### Output to the app

Standardized `LLMResponse` object:

- `content: str` – primary text output.  
- `raw: Any` – full native provider response.  
- `provider: str` – provider name used.  
- `model: str` – model ID used.  

---

## 5. Sub-Problems (SP1–SP5)

### SP1 — Config Loader

Responsibility:  
- Read YAML config from disk.  
- Validate it against a Pydantic schema.  
- Provide a typed `OrchestratorConfig` object.

Input:  
- `config_path: str`  

Output:  
- `OrchestratorConfig(project, env, providers, roles)`  

Key fields:  
- `providers: Dict[str, ProviderConfig]`  
- `roles: Dict[str, RoleBinding]`  

---

### SP2 — Auth Resolver

Responsibility:  
- Map `auth_profile` to an API key using environment variables.

Convention:  
- For `auth_profile = "openai_default"`  
  env var name = `ORCH_AUTH_OPENAI_DEFAULT_API_KEY`  

Input:  
- `auth_profile: str`  

Output:  
- `api_key: str`  

Error:  
- If env var missing, raise a clear, typed error.

---

### SP3 — Provider Adapter Interface

Responsibility:  
- Define a common interface to call any provider given a model and messages.

Types:  
- Base class `BaseProviderAdapter` with:  
  `run_chat(model: str, messages: List[Message], params: dict) -> LLMResponse`  
- For PLAN-A, at least one real implementation should exist (OpenAI). Others can be stubbed but must follow the same signature.

Files:  
- `providers/base.py` – abstract base class and helpers.  
- `providers/openai_adapter.py` – minimal real call to OpenAI.  
- `providers/gemini_adapter.py`, `anthropic_adapter.py`, etc. – stubs or simple placeholders.

Input:  
- `model: str`, `messages: List[Message]`, `params: dict`, `api_key: str`, `api_base: str`.  

Output:  
- `LLMResponse`.

---

### SP4 — Resolution Layer

Responsibility:  
- Given `(project, env, role)` (implicitly from config), find provider + model + auth_profile + api_base.  
- Use SP2 to resolve API key.  
- Build a `ResolvedLLMConfig` used by runtime.

Input:  
- `config: OrchestratorConfig`  
- `role: str`  

Output:  
- `ResolvedLLMConfig(provider: str, model: str, api_key: str, api_base: str)`  

Error cases:  
- Role not defined.  
- Provider for that role not defined.  
- Auth profile missing or env var missing.

---

### SP5 — Runtime LLM Client

Responsibility:  
- Public entrypoint used by apps.  
- Provide:

  - `get_llm_client(config_path: str) -> LLMClient`  
  - `LLMClient.run(role: str, messages: List[Message], params_override: dict | None) -> LLMResponse`

Flow inside `run()`:

1. Ensure config is loaded (SP1), maybe cached.  
2. Use SP4 to resolve role → `ResolvedLLMConfig`.  
3. Select correct provider adapter from `providers/` based on `provider` name.  
4. Call the adapter’s `run_chat()` with model, messages, params.  
5. Return unified `LLMResponse`.

Files:  
- `runtime/types.py` – Message, LLMResponse, ResolvedLLMConfig, etc.  
- `runtime/llm_client.py` – actual client implementation.

---

## 6. Acceptance Criteria

PLAN-A is complete when:

1. `get_llm_client(config_path)` returns a client that can:  
   - Call at least one real provider (OpenAI) successfully.  
   - Use `role` lookup from YAML.  

2. Config errors are handled cleanly:  
   - Invalid YAML → clear error.  
   - Missing role → clear error.  
   - Missing provider entry → clear error.  
   - Missing auth env var → clear error.

3. All provider adapters expose the same interface (even if some are stubs).

4. The example app in `examples/minimal_app/` can:

   - Load `llm_orchestrator.yaml`.  
   - Use `llm_bindings.py` to call `client.run(role="llm.preprocess", messages=[...])`.  
   - Print/inspect the LLM response.

5. A minimal README exists explaining:

   - How to install requirements.  
   - How to set `ORCH_AUTH_*` env vars.  
   - How to write `llm_orchestrator.yaml`.  
   - How to run the example.

---

## 7. Out of Scope for PLAN-A

The following are explicitly deferred to later plans:

- Dynamic model discovery and catalogs.  
- Scoring and recommendations.  
- Multi-project / multi-env aggregation.  
- UI or web dashboard.  
- Fallback models, routing logic, or A/B testing.  
- Memory integration (mem0, OpenMemory).  
- Partial memory exposures and MCP/IDE connectors.

PLAN-A is only about:  
Config → Resolution → Unified run() → Real provider call.

---

## 8. Path to PLAN-B

Once PLAN-A is stable:

- Introduce a separate Model Catalog module that:  
  - discovers models per provider,  
  - attaches metadata (speed, cost, quality bands).  

- Extend the YAML to allow role-level selection rules instead of hard-coded models.  

- Let the resolution layer use the catalog + rules to pick best-fit models at runtime or deploy-time.

PLAN-A should be clean enough to tag as version `v0.1.0` of the project.

# END OF PLAN-A.md