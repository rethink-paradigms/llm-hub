# Generator Module

The Generator converts human-written specifications into machine-readable LLM configurations.

## Quick Start

```python
from llmhub.generator import generate_machine_config
from llmhub_runtime import LLMHub

# Initialize runtime (with a generator role configured)
hub = LLMHub(config_path="llmhub.yaml")

# Generate machine config from human spec
machine_config = generate_machine_config(
    spec_path="llmhub.spec.yaml",
    hub=hub
)

# The machine config can now be used with LLMHub
```

## What It Does

The Generator takes a user-friendly spec file like:

```yaml
project: my-app
env: production

roles:
  analyst:
    kind: chat
    description: "Analyze user feedback and extract insights"
    preferences:
      quality: high
      cost: medium
```

And produces a machine-readable config like:

```yaml
project: my-app
env: production

providers:
  openai:
    env_key: OPENAI_API_KEY

roles:
  analyst:
    provider: openai
    model: gpt-4o
    mode: chat
    params:
      temperature: 0.7
```

## Architecture

The Generator is split into 10 subproblems (SP1-SP10):

- **SP1**: Parse human spec YAML
- **SP2**: Use LLM to interpret needs
- **SP3**: Define canonical RoleNeed schema
- **SP4**: Load model catalog
- **SP5**: Filter candidates by constraints
- **SP6**: Calculate scoring weights
- **SP7**: Score and rank models
- **SP8**: Relax constraints if needed
- **SP9**: Orchestrate per-role selection
- **SP10**: Emit final machine config

Each subproblem has its own folder with a `spec.md` defining inputs, outputs, and interfaces.

## Key Features

- **Deterministic**: Same spec + catalog = same output
- **LLM-powered interpretation**: Natural language role descriptions
- **Intelligent selection**: Multi-factor scoring (quality, cost, latency, etc.)
- **Automatic fallbacks**: Relaxation engine when no perfect match exists
- **Catalog-driven**: Uses enriched model metadata from Catalog module

## Testing

```bash
# Run all generator tests
pytest tests/generator/

# Run specific subproblem test
pytest tests/generator/test_sp1_spec_schema.py

# Run end-to-end test
pytest tests/generator/test_generate_e2e.py
```

## Documentation

See [`spec.md`](./spec.md) for detailed architecture and specifications.

Each subproblem folder contains its own `spec.md` with detailed documentation.
