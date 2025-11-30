# Getting Started

<cite>
**Referenced Files in This Document**
- [README.md](file://README.md)
- [packages/llmhub/README.md](file://packages/llmhub/README.md)
- [packages/llmhub/pyproject.toml](file://packages/llmhub/pyproject.toml)
- [Makefile](file://Makefile)
- [packages/llmhub/src/llmhub/cli.py](file://packages/llmhub/src/llmhub/cli.py)
- [packages/llmhub/src/llmhub/commands/setup_cmd.py](file://packages/llmhub/src/llmhub/commands/setup_cmd.py)
- [packages/llmhub/src/llmhub/commands/runtime_cmd.py](file://packages/llmhub/src/llmhub/commands/runtime_cmd.py)
- [packages/llmhub/src/llmhub/env_manager.py](file://packages/llmhub/src/llmhub/env_manager.py)
- [packages/llmhub/src/llmhub/commands/catalog_cmd.py](file://packages/llmhub/src/llmhub/commands/catalog_cmd.py)
- [packages/llmhub/src/llmhub/commands/test_cmd.py](file://packages/llmhub/src/llmhub/commands/test_cmd.py)
- [packages/llmhub/src/llmhub/spec_models.py](file://packages/llmhub/src/llmhub/spec_models.py)
- [packages/llmhub_runtime/src/llmhub_runtime/hub.py](file://packages/llmhub_runtime/src/llmhub_runtime/hub.py)
- [packages/llmhub/src/llmhub/context.py](file://packages/llmhub/src/llmhub/context.py)
</cite>

## Table of Contents
1. [Introduction](#introduction)
2. [Installation](#installation)
3. [Environment Setup](#environment-setup)
4. [Project Initialization](#project-initialization)
5. [Configuration Management](#configuration-management)
6. [Runtime Generation](#runtime-generation)
7. [Testing and Validation](#testing-and-validation)
8. [Python Runtime Usage](#python-runtime-usage)
9. [Common Pitfalls and Troubleshooting](#common-pitfalls-and-troubleshooting)
10. [Best Practices](#best-practices)

## Introduction

LLM Hub is a production-grade system for managing large language models through declarative configuration rather than hardcoded provider/model names. It provides a unified runtime that resolves logical "roles" to actual LLM providers and models, plus a sophisticated catalog system that enriches models with cost, quality, and capability metadata.

### Key Benefits

- **Decouple business logic from model implementation**: Reference logical roles ("preprocess", "inference", "embedding") instead of vendor-specific model strings
- **Enable config-driven model selection**: Change models by editing YAML files, not code
- **Support intelligent model selection**: The catalog system provides rich metadata for automatic model selection
- **Standardize LLM access**: All LLM calls go through a consistent interface backed by any-llm

## Installation

### From PyPI (Recommended)

```bash
pip install rethink-llmhub llmhub-runtime
```

This installs both the CLI tool and the runtime library with all dependencies.

### From Source (Development)

```bash
# Clone the repository
git clone https://github.com/rethink-paradigms/llm-hub.git
cd llm-hub

# Install both packages in editable mode
pip install -e packages/llmhub_runtime
pip install -e packages/llmhub

# Or use the Makefile
make install
```

### Requirements

- **Python**: 3.10 or higher
- **any-llm**: Automatically installed with `llmhub-runtime`
- **Provider API keys**: Set as environment variables (see below)

**Section sources**
- [README.md](file://README.md#L100-L122)
- [packages/llmhub/README.md](file://packages/llmhub/README.md#L70-L106)
- [packages/llmhub/pyproject.toml](file://packages/llmhub/pyproject.toml#L26-L36)
- [Makefile](file://Makefile#L16-L18)

## Environment Setup

### Setting API Keys

LLM Hub requires provider API keys to be set as environment variables. The exact keys depend on which providers you enable:

```bash
# Common providers
export OPENAI_API_KEY="sk-..."
export ANTHROPIC_API_KEY="sk-ant-..."
export GEMINI_API_KEY="..."
export DEEPSEEK_API_KEY="..."
export QWEN_API_KEY="..."
export MISTRAL_API_KEY="..."
export COHERE_API_KEY="..."
```

### Using .env Files

You can also use a `.env` file with `python-dotenv` for convenient environment variable management:

```bash
# Copy the example template
cp .env.example .env

# Edit the .env file
nano .env
```

The `.env.example` file is automatically generated during project initialization and contains placeholders for all required API keys.

### Environment Variable Validation

LLM Hub performs strict validation of environment variables. You can enable this during runtime initialization:

```python
from llmhub_runtime import LLMHub

# This will fail if any required API keys are missing
hub = LLMHub(config_path="llmhub.yaml", strict_env=True)
```

**Section sources**
- [README.md](file://README.md#L129-L144)
- [packages/llmhub/src/llmhub/env_manager.py](file://packages/llmhub/src/llmhub/env_manager.py#L46-L71)

## Project Initialization

### Quick Start with `llmhub init`

Initialize a new LLM Hub project with minimal defaults:

```bash
# Navigate to your project directory
cd your-project-directory

# Quick initialization
llmhub init
```

This creates:
- `llmhub.spec.yaml`: High-level specification of roles and preferences
- `.env.example`: Template for required environment variables

**Expected output:**
```
✓ Minimal spec created at llmhub.spec.yaml
✓ Environment example created at .env.example

Next steps:
  1. Edit llmhub.spec.yaml to add more roles
  2. Set OPENAI_API_KEY environment variable
  3. Run: llmhub generate
```

### Interactive Setup with `llmhub setup`

For more customization, use the interactive setup:

```bash
# Interactive setup
llmhub setup
```

The setup wizard guides you through:
1. Project name and environment selection
2. Provider selection (OpenAI, Anthropic, Gemini, Mistral, Cohere)
3. Standard role scaffolding (preprocess, inference, embedding, tools)
4. Preference configuration for each role

**Section sources**
- [packages/llmhub/src/llmhub/commands/setup_cmd.py](file://packages/llmhub/src/llmhub/commands/setup_cmd.py#L121-L161)
- [packages/llmhub/src/llmhub/commands/setup_cmd.py](file://packages/llmhub/src/llmhub/commands/setup_cmd.py#L16-L118)

## Configuration Management

### Understanding Configuration Files

LLM Hub uses two types of configuration files:

#### 1. Spec File (`llmhub.spec.yaml`)

The human-friendly specification declares:
- Project metadata and environment
- Enabled providers and their API keys
- Logical roles and their preferences
- Default configurations

**Example spec structure:**
```yaml
project: my-app
env: dev

providers:
  openai:
    enabled: true
    env_key: OPENAI_API_KEY
  anthropic:
    enabled: true
    env_key: ANTHROPIC_API_KEY

roles:
  llm.inference:
    kind: chat
    description: Main reasoning model for answering questions
    preferences:
      cost: medium
      latency: medium
      quality: high
      providers:
        - openai
        - anthropic

defaults:
  providers:
    - openai
    - anthropic
```

#### 2. Runtime Config (`llmhub.yaml`)

The machine-optimized runtime configuration contains:
- Actual provider/model mappings
- Optimized parameters for each role
- Provider configurations

**Section sources**
- [README.md](file://README.md#L360-L498)
- [packages/llmhub/src/llmhub/spec_models.py](file://packages/llmhub/src/llmhub/spec_models.py#L59-L66)

## Runtime Generation

### Generating Runtime Configuration

Convert your spec into a runtime configuration:

```bash
# Generate runtime from spec
llmhub generate
```

This analyzes your spec and generates `llmhub.yaml` with:
- Optimal model selections based on preferences
- Appropriate parameters for each role
- Provider configurations

### Generation Options

```bash
# Dry run (preview without writing)
llmhub generate --dry-run

# Show model selection explanations
llmhub generate --explain

# Force overwrite existing runtime
llmhub generate --force

# Use heuristic-only mode (no LLM-assisted generation)
llmhub generate --no-llm
```

### Catalog Management

Before generating, you can build and inspect the model catalog:

```bash
# Refresh the catalog (fetch latest data)
llmhub catalog refresh

# Show available models
llmhub catalog show

# Filter by provider
llmhub catalog show --provider openai

# Show detailed info
llmhub catalog show --details
```

**Section sources**
- [packages/llmhub/src/llmhub/commands/runtime_cmd.py](file://packages/llmhub/src/llmhub/commands/runtime_cmd.py#L13-L68)
- [packages/llmhub/src/llmhub/commands/catalog_cmd.py](file://packages/llmhub/src/llmhub/commands/catalog_cmd.py#L16-L127)

## Testing and Validation

### Testing Roles Interactively

Test a role by sending a sample prompt:

```bash
# Interactive testing
llmhub test

# Test specific role with prompt
llmhub test --role llm.inference --prompt "Hello, world!"

# Output raw JSON response
llmhub test --role llm.inference --json
```

### Health Check with `llmhub doctor`

Run a comprehensive health check:

```bash
# Full health check
llmhub doctor

# Skip network test calls
llmhub doctor --no-network
```

The doctor command validates:
- Spec file existence and validity
- Runtime file existence and validity
- Environment variables
- Network connectivity for test calls

**Section sources**
- [packages/llmhub/src/llmhub/commands/test_cmd.py](file://packages/llmhub/src/llmhub/commands/test_cmd.py#L18-L232)
- [packages/llmhub/src/llmhub/commands/test_cmd.py](file://packages/llmhub/src/llmhub/commands/test_cmd.py#L125-L232)

## Python Runtime Usage

### Basic Initialization

```python
from llmhub_runtime import LLMHub

# Initialize hub with machine config
hub = LLMHub(config_path="llmhub.yaml")
```

### Making Completion Calls

```python
# Basic completion call
response = hub.completion(
    role="llm.inference",
    messages=[
        {"role": "user", "content": "Explain quantum entanglement in simple terms."}
    ]
)

print(response)
```

### Parameter Overrides

```python
# Override parameters for a specific call
response = hub.completion(
    role="llm.inference",
    messages=[{"role": "user", "content": "Write a haiku about code."}],
    params_override={"temperature": 1.0, "max_tokens": 100}
)
```

### Using Embeddings

```python
# Generate embeddings
embeddings = hub.embedding(
    role="llm.embedding",
    input=["hello world", "goodbye world"]
)
```

### Hooks for Logging and Observability

```python
def log_before(ctx):
    print(f"Calling {ctx['provider']}:{ctx['model']} for role {ctx['role']}")

def log_after(result):
    print(f"Call {'succeeded' if result['success'] else 'failed'}")

hub = LLMHub(
    config_path="llmhub.yaml",
    on_before_call=log_before,
    on_after_call=log_after
)
```

### Strict Environment Validation

```python
# Fail fast if any required API keys are missing
hub = LLMHub(config_path="llmhub.yaml", strict_env=True)
```

**Section sources**
- [README.md](file://README.md#L219-L281)
- [packages/llmhub_runtime/src/llmhub_runtime/hub.py](file://packages/llmhub_runtime/src/llmhub_runtime/hub.py#L17-L189)

## Common Pitfalls and Troubleshooting

### Missing API Keys

**Problem**: "Missing environment variable" errors
**Solution**: 
```bash
# Check what's missing
llmhub env check

# Add to .env file
echo "OPENAI_API_KEY=sk-..." >> .env
```

### Uninitialized Projects

**Problem**: "Spec file not found" or "Runtime file not found"
**Solution**:
```bash
# Initialize project
llmhub init

# Or use interactive setup
llmhub setup
```

### Unknown Role Errors

**Problem**: "Unknown role" errors
**Solution**:
```bash
# List available roles
llmhub roles

# Add missing role
llmhub add-role your-role-name

# Regenerate runtime
llmhub generate
```

### Network Connectivity Issues

**Problem**: Network-related failures during testing
**Solution**:
- Verify API keys are correct
- Check internet connectivity
- Ensure provider services are available

### Version Compatibility

**Problem**: Python version or dependency conflicts
**Solution**:
- Ensure Python 3.10+ is installed
- Use virtual environments
- Check dependency versions in `pyproject.toml`

**Section sources**
- [packages/llmhub/src/llmhub/commands/test_cmd.py](file://packages/llmhub/src/llmhub/commands/test_cmd.py#L112-L118)
- [packages/llmhub/src/llmhub/env_manager.py](file://packages/llmhub/src/llmhub/env_manager.py#L46-L71)

## Best Practices

### Version Control

```bash
# Track these files
git add llmhub.spec.yaml
git add llmhub.yaml
git add .env.example

# Don't track these
echo ".env" >> .gitignore
```

### Environment Management

- Use `.env.example` for documentation
- Never commit actual `.env` files
- Use different keys for dev/prod environments

### Role Naming Conventions

```yaml
# ✅ Good - descriptive, hierarchical
llm.user.summarize
llm.admin.analytics
llm.public.search

# ❌ Bad - vague, flat
summarizer
model1
gpt
```

### Regular Validation

```bash
# Add to pre-commit hooks
llmhub spec validate
llmhub env check --env-file .env.example
```

### Testing Before Deployment

```bash
# Test critical roles
llmhub test --role llm.inference
llmhub test --role llm.embedding
llmhub doctor --no-network  # CI/CD
```

### Multiple Environments

```bash
# Development
llmhub generate --dry-run > llmhub.dev.yaml

# Production  
llmhub generate --force > llmhub.prod.yaml

# In application
import os
env = os.getenv("ENV", "dev")
hub = LLMHub(config_path=f"llmhub.{env}.yaml")
```

**Section sources**
- [packages/llmhub/README.md](file://packages/llmhub/README.md#L609-L653)
- [README.md](file://README.md#L148-L217)