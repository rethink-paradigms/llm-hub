# LLMHub Monorepo

A modular system for managing LLM configurations through human-friendly specs and machine-optimized runtime configs.

## What is LLMHub?

LLMHub simplifies LLM integration by separating **what you want** (spec) from **how it runs** (runtime). Instead of hardcoding provider names and model strings throughout your application, you define logical roles that the system maps to concrete models.

**Key Benefits:**
- 🎯 **Role-based abstraction** - Call LLMs by purpose, not by provider/model
- 🔄 **Easy model swapping** - Change models without touching application code
- 🛠️ **Multi-provider support** - Works with any provider supported by any-llm
- 📝 **Version control friendly** - YAML configs that are git-friendly and reviewable
- 🧪 **Built-in testing** - Validate your LLM setup before deployment

## Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  llmhub.spec    │ ──> │   llmhub CLI     │ ──> │  llmhub.yaml    │
│  (human spec)   │     │   (generator)    │     │  (runtime)      │
└─────────────────┘     └──────────────────┘     └─────────────────┘
                                                           │
                                                           v
                                                  ┌─────────────────┐
                                                  │ llmhub-runtime  │
                                                  │  (execution)    │
                                                  └─────────────────┘
                                                           │
                                                           v
                                                    ┌─────────────┐
                                                    │   any-llm   │
                                                    │ (providers) │
                                                    └─────────────┘
```

## Packages

### 1. [llmhub-runtime](packages/llmhub_runtime)

The lightweight runtime library that executes LLM calls based on runtime configs.

**Key Features:**
- Load and validate `llmhub.yaml` runtime configs
- Resolve logical roles to concrete provider/model/params
- Execute calls via `any-llm` SDK
- Support for completions, embeddings, and more
- Optional hooks for logging and metrics

**Installation:**
```bash
pip install llmhub-runtime
```

**Quick Example:**
```python
from llmhub_runtime import LLMHub

hub = LLMHub(config_path="llmhub.yaml")
response = hub.completion(
    role="llm.inference",
    messages=[{"role": "user", "content": "Hello!"}]
)
```

### 2. [llmhub](packages/llmhub)

The CLI tool for managing LLM specs and generating runtime configurations.

**Key Features:**
- Interactive and non-interactive project setup
- Spec file management (roles, providers, preferences)
- Intelligent spec → runtime generation
- Environment variable management
- Built-in testing and health checks
- Beautiful CLI with rich output

**Installation:**
```bash
pip install llmhub
```

**Quick Start:**
```bash
# Initialize a new project
llmhub init

# Generate runtime config
llmhub generate

# Test your setup
llmhub test
```

## Quick Start Guide

### 1. Install packages

```bash
pip install llmhub llmhub-runtime
```

### 2. Initialize your project

```bash
cd your-project
llmhub init
```

This creates:
- `llmhub.spec.yaml` - Your human-friendly spec
- `.env.example` - Environment variable template

### 3. Set up environment

```bash
cp .env.example .env
# Edit .env and add your API keys
export OPENAI_API_KEY="your-key-here"
```

### 4. Generate runtime config

```bash
llmhub generate
```

This creates `llmhub.yaml` from your spec.

### 5. Use in your application

```python
from llmhub_runtime import LLMHub

hub = LLMHub(config_path="llmhub.yaml")

# Call by role, not by provider/model
response = hub.completion(
    role="llm.inference",
    messages=[{"role": "user", "content": "Explain quantum computing"}]
)
```

## Example Workflow

**Spec (llmhub.spec.yaml):**
```yaml
project: my-ai-app
env: production

providers:
  openai:
    enabled: true
    env_key: OPENAI_API_KEY
  anthropic:
    enabled: true
    env_key: ANTHROPIC_API_KEY

roles:
  llm.preprocess:
    kind: chat
    description: Fast preprocessing for user input
    preferences:
      cost: low
      latency: low
      quality: medium

  llm.inference:
    kind: chat
    description: Main reasoning engine
    preferences:
      cost: medium
      quality: high
      providers: [anthropic, openai]
```

**Generated Runtime (llmhub.yaml):**
```yaml
project: my-ai-app
env: production

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
```

**Application Code:**
```python
from llmhub_runtime import LLMHub

hub = LLMHub(config_path="llmhub.yaml")

# Preprocess user input
preprocessed = hub.completion(
    role="llm.preprocess",
    messages=[{"role": "user", "content": user_input}]
)

# Main inference
result = hub.completion(
    role="llm.inference",
    messages=conversation_history
)
```

## Why LLMHub?

### Problem: Hardcoded LLM Dependencies

Traditional approach:
```python
# Tightly coupled to specific providers
from openai import OpenAI
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
response = client.chat.completions.create(
    model="gpt-4",  # Hardcoded!
    messages=messages,
    temperature=0.7  # Scattered configs!
)
```

### Solution: Role-Based Abstraction

With LLMHub:
```python
# Decoupled from providers
from llmhub_runtime import LLMHub
hub = LLMHub(config_path="llmhub.yaml")
response = hub.completion(
    role="llm.inference",  # Logical role!
    messages=messages
)
```

**Benefits:**
- ✅ Swap `gpt-4` → `claude-3-5-sonnet` by editing YAML, no code changes
- ✅ Different models for dev/staging/prod environments
- ✅ Centralized configuration management
- ✅ Easy A/B testing of different models
- ✅ Version control for LLM choices

## CLI Commands

```bash
# Project setup
llmhub init              # Quick start with defaults
llmhub setup             # Interactive setup

# Spec management
llmhub spec show         # View current spec
llmhub spec validate     # Validate spec file
llmhub roles             # List all roles
llmhub add-role NAME     # Add a new role
llmhub edit-role NAME    # Edit existing role

# Runtime generation
llmhub generate          # Generate runtime from spec
llmhub runtime show      # View runtime config
llmhub runtime diff      # Compare spec vs runtime

# Environment
llmhub env sync          # Update .env.example
llmhub env check         # Check for missing vars

# Testing
llmhub test              # Test a role
llmhub doctor            # Health check

# Utilities
llmhub status            # Project status
llmhub path              # Show resolved paths
```

## Development

### Repository Structure

```
llm-hub/
├── packages/
│   ├── llmhub_runtime/     # Runtime execution library
│   │   ├── src/
│   │   ├── tests/
│   │   └── pyproject.toml
│   └── llmhub/             # CLI tool
│       ├── src/
│       ├── tests/
│       └── pyproject.toml
└── README.md
```

### Running Tests

```bash
# Test runtime package
cd packages/llmhub_runtime
python -m pytest tests/

# Test CLI package
cd packages/llmhub
python -m pytest tests/
```

### Installing for Development

```bash
# Install both packages in editable mode
cd packages/llmhub_runtime
pip install -e .

cd ../llmhub
pip install -e .
```

## Contributing

Contributions are welcome! Please ensure:
- All tests pass
- Code follows existing patterns
- New features include tests
- Update relevant documentation

## License

MIT License - See LICENSE file for details

## Support

For issues, questions, or contributions:
- Open an issue on GitHub
- Check existing documentation
- Review example configurations

---

**Built with ❤️ for developers who want flexible, maintainable LLM integrations**
