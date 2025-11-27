# LLM Orchestrator (PLAN-A)

Core engine for resolving logical LLM roles into concrete provider/model calls with a single `run()` API.

## Install Requirements

```bash
pip install openai pydantic pyyaml
```

## Configure Auth

Set env vars for each auth profile referenced in your config (profile names are uppercased and sanitized):

```bash
export ORCH_AUTH_OPENAI_DEFAULT_API_KEY="sk-..."
```

## Write Config

Place a `llm_orchestrator.yaml` with providers and role bindings. Example (`orchestrator/examples/minimal_app/llm_orchestrator.yaml`):

```yaml
project: my_project
env: dev

providers:
  openai:
    auth_profile: openai_default
    api_base: https://api.openai.com/v1

roles:
  llm.preprocess:
    provider: openai
    model: gpt-4.1-mini
```

## Run the Minimal Example

```bash
python orchestrator/examples/minimal_app/llm_bindings.py
```

The script loads the YAML config, resolves the `llm.preprocess` role, and executes a chat request via the OpenAI adapter.
