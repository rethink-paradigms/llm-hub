# LLMHub CLI

> A powerful command-line tool for managing LLM configurations through human-friendly specs and intelligent runtime generation.

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## What is LLMHub CLI?

LLMHub CLI is a development tool that separates **what you want from your LLMs** (preferences, constraints) from **how they execute** (specific models, parameters). It generates optimized runtime configurations from human-friendly specification files.

### The Problem It Solves

**Before LLMHub:**
```python
# Scattered, hardcoded LLM configs throughout your codebase
from openai import OpenAI

# In file1.py
client = OpenAI()
response = client.chat.completions.create(
    model="gpt-4",  # Hardcoded!
    temperature=0.7,  # Duplicated config!
    messages=[...]
)

# In file2.py - using different params for same purpose
response = client.chat.completions.create(
    model="gpt-4",  # Same model, different params
    temperature=0.5,  # Inconsistent!
    max_tokens=1000,
    messages=[...]
)
```

**Problems:**
- ❌ Models hardcoded across multiple files
- ❌ Inconsistent parameters for same use case
- ❌ Hard to swap providers (OpenAI → Anthropic)
- ❌ Different configs for dev/staging/prod environments
- ❌ No central config management

**With LLMHub:**
```yaml
# llmhub.spec.yaml - Single source of truth
roles:
  llm.inference:
    kind: chat
    description: Main reasoning engine
    preferences:
      quality: high
      cost: medium
```

```python
# Your application - clean and maintainable
from llmhub_runtime import LLMHub

hub = LLMHub(config_path="llmhub.yaml")
response = hub.completion(role="llm.inference", messages=[...])
```

**Benefits:**
- ✅ One config file, consistent behavior
- ✅ Swap models by editing YAML (no code changes)
- ✅ Environment-specific configs (dev/prod)
- ✅ Version controlled LLM decisions
- ✅ Easy testing and validation

## Installation

### Prerequisites
- Python 3.10 or higher
- pip or poetry

### Install from PyPI

```bash
pip install llmhub
```

This automatically installs the required dependencies:
- `llmhub-runtime` - Runtime execution library
- `typer` - CLI framework
- `rich` - Beautiful terminal output
- `pydantic` - Data validation
- `python-dotenv` - Environment management

### Install for Development

```bash
# Clone the repository
git clone https://github.com/your-org/llm-hub.git
cd llm-hub/packages/llmhub

# Install in editable mode
pip install -e .
```

### Verify Installation

```bash
llmhub --version
llmhub --help
```

## Quick Start

### 1. Initialize Your Project

```bash
cd your-project
llmhub init
```

This creates:
- `llmhub.spec.yaml` - Your LLM specification
- `.env.example` - Environment variable template

**Output:**
```
✓ Minimal spec created at llmhub.spec.yaml
✓ Environment example created at .env.example

Next steps:
  1. Edit llmhub.spec.yaml to add more roles
  2. Set OPENAI_API_KEY environment variable
  3. Run: llmhub generate
```

### 2. Configure Environment

```bash
# Copy and edit .env
cp .env.example .env

# Add your API keys
echo "OPENAI_API_KEY=sk-..." >> .env
echo "ANTHROPIC_API_KEY=sk-ant-..." >> .env
```

### 3. Generate Runtime Config

```bash
llmhub generate
```

This analyzes your spec and generates `llmhub.yaml` with:
- Optimal model selections based on preferences
- Appropriate parameters for each role
- Provider configurations

### 4. Test Your Setup

```bash
# Run health check
llmhub doctor

# Test a specific role
llmhub test --role llm.inference --prompt "Hello, world!"
```

### 5. Use in Your Application

```python
from llmhub_runtime import LLMHub

# Initialize hub with generated config
hub = LLMHub(config_path="llmhub.yaml")

# Call by role name
response = hub.completion(
    role="llm.inference",
    messages=[{"role": "user", "content": "Explain AI"}]
)

print(response)
```

## Core Concepts

### Spec vs Runtime

**Spec (`llmhub.spec.yaml`)** - What you want:
```yaml
roles:
  llm.summarize:
    kind: chat
    description: Summarize long documents
    preferences:
      cost: low        # Prefer cheaper models
      latency: low     # Prefer faster models
      quality: medium  # Good enough quality
```

**Runtime (`llmhub.yaml`)** - How it runs:
```yaml
roles:
  llm.summarize:
    provider: openai
    model: gpt-4o-mini  # Selected based on preferences
    mode: chat
    params:
      temperature: 0.3
      max_tokens: 1024
```

### Role-Based Design

Instead of calling specific models, you call **logical roles**:

```python
# ❌ Tightly coupled
response = openai.chat(model="gpt-4", ...)

# ✅ Loosely coupled
response = hub.completion(role="llm.inference", ...)
```

Benefits:
- Swap models without code changes
- Consistent behavior for same purpose
- Environment-specific configurations
- Easier testing and mocking

### Preference-Based Selection

Define **what you need**, not **which model**:

```yaml
llm.analytics:
  kind: chat
  preferences:
    quality: high    # Prioritize accuracy
    cost: low        # But keep costs down
    latency: medium  # Response time is okay
    providers: [openai, anthropic]  # Allowed providers
```

The generator selects the best model matching your criteria.

## Configuration Files

### llmhub.spec.yaml

Human-friendly specification of your LLM needs:

```yaml
project: my-app
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
    description: Clean and normalize user input
    preferences:
      cost: low
      latency: low
      quality: medium
  
  llm.inference:
    kind: chat
    description: Main reasoning and response generation
    preferences:
      quality: high
      cost: medium
      providers: [anthropic, openai]
  
  llm.embedding:
    kind: embedding
    description: Generate embeddings for search
    preferences:
      cost: low
      quality: medium

defaults:
  providers: [openai]
```

### llmhub.yaml

Machine-optimized runtime configuration:

```yaml
project: my-app
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
  
  llm.embedding:
    provider: openai
    model: text-embedding-3-small
    mode: embedding
    params: {}
```

## CLI Commands

### Project Setup

```bash
# Quick initialization with defaults
llmhub init

# Interactive setup with guided questions
llmhub setup

# Check project status
llmhub status

# Show resolved file paths
llmhub path
```

### Spec Management

```bash
# View current spec
llmhub spec show

# Validate spec file
llmhub spec validate

# List all roles
llmhub roles

# Add a new role
llmhub add-role llm.translate

# Edit existing role
llmhub edit-role llm.inference

# Remove a role
llmhub rm-role llm.old-role
```

### Runtime Generation

```bash
# Generate runtime from spec
llmhub generate

# Dry run (preview without writing)
llmhub generate --dry-run

# Force overwrite existing runtime
llmhub generate --force

# Show model selection explanations
llmhub generate --explain

# View generated runtime
llmhub runtime show

# Compare spec vs runtime
llmhub runtime diff
```

### Environment Management

```bash
# Sync .env.example from spec
llmhub env sync

# Check for missing environment variables
llmhub env check

# Check with custom .env file
llmhub env check --env-file .env.production
```

### Testing & Validation

```bash
# Test a role interactively
llmhub test

# Test specific role with prompt
llmhub test --role llm.inference --prompt "Hello!"

# Output raw JSON response
llmhub test --role llm.inference --json

# Run comprehensive health check
llmhub doctor

# Health check without network calls
llmhub doctor --no-network
```

## Advanced Usage

### Multiple Environments

Maintain separate configs for different environments:

```bash
# Development
llmhub generate --dry-run > llmhub.dev.yaml

# Production
llmhub generate --force > llmhub.prod.yaml
```

In your application:
```python
import os
env = os.getenv("ENV", "dev")
hub = LLMHub(config_path=f"llmhub.{env}.yaml")
```

### Forcing Specific Models

Override generator with explicit model choices:

```yaml
roles:
  llm.critical:
    kind: chat
    description: Critical production workload
    force_provider: anthropic
    force_model: claude-3-5-sonnet-20241022
    preferences:
      quality: high
```

### Custom Parameters

Pass model-specific parameters:

```yaml
roles:
  llm.creative:
    kind: chat
    description: Creative writing assistant
    mode_params:
      temperature: 0.9
      top_p: 0.95
      presence_penalty: 0.6
      frequency_penalty: 0.3
```

### Integration with CI/CD

```yaml
# .github/workflows/validate-llm-config.yml
name: Validate LLM Config

on: [push, pull_request]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.10'
      - run: pip install llmhub
      - run: llmhub spec validate
      - run: llmhub env check
```

## Workflow Examples

### Example 1: Adding a New Feature

You need to add translation functionality:

```bash
# 1. Add role to spec
llmhub add-role llm.translate
# Select: kind=chat, cost=low, quality=high

# 2. Regenerate runtime
llmhub generate

# 3. Test it
llmhub test --role llm.translate --prompt "Translate 'Hello' to Spanish"

# 4. Use in code
```

```python
response = hub.completion(
    role="llm.translate",
    messages=[{
        "role": "user",
        "content": "Translate 'Hello World' to French"
    }]
)
```

### Example 2: Swapping Providers

Switch from OpenAI to Anthropic for main inference:

```bash
# 1. Edit spec (just change preferences)
llmhub edit-role llm.inference
# Update: providers=[anthropic]

# 2. Regenerate
llmhub generate

# 3. Verify
llmhub runtime show

# Application code remains unchanged!
```

### Example 3: Cost Optimization

Reduce costs by using cheaper models where quality isn't critical:

```bash
# 1. Edit roles in spec
# Change: llm.preprocess → cost: low
# Change: llm.summarize → cost: low

# 2. Regenerate
llmhub generate --explain

# 3. Review changes
llmhub runtime diff

# 4. Test to ensure quality is acceptable
llmhub test --role llm.preprocess
```

## Troubleshooting

### Common Issues

**Issue: "Spec file not found"**
```bash
# Initialize project first
llmhub init
```

**Issue: "Missing environment variable"**
```bash
# Check what's missing
llmhub env check

# Add to .env
echo "OPENAI_API_KEY=sk-..." >> .env
```

**Issue: "Runtime file not found"**
```bash
# Generate runtime from spec
llmhub generate
```

**Issue: "Unknown role error"**
```bash
# List available roles
llmhub roles

# Add missing role
llmhub add-role your-role-name
```

### Debug Mode

For verbose output:
```bash
# Check file paths
llmhub path

# Validate configurations
llmhub spec validate
llmhub doctor

# Test with dry-run
llmhub generate --dry-run --explain
```

## Best Practices

### 1. Version Control
```bash
# Track these files
git add llmhub.spec.yaml
git add llmhub.yaml
git add .env.example

# Don't track these
echo ".env" >> .gitignore
```

### 2. Environment Variables
- Use `.env.example` for documentation
- Never commit actual `.env` files
- Use different keys for dev/prod

### 3. Role Naming
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

### 4. Regular Validation
```bash
# Add to pre-commit hook
llmhub spec validate
llmhub env check --env-file .env.example
```

### 5. Testing
```bash
# Test critical roles before deployment
llmhub test --role llm.inference
llmhub test --role llm.embedding
llmhub doctor --no-network  # CI/CD
```

## Architecture

LLMHub CLI is built with modularity in mind:

```
llmhub/
├── context.py          # Project context resolution
├── spec_models.py      # Spec schema & validation
├── runtime_io.py       # Runtime config I/O
├── env_manager.py      # Environment management
├── ux.py              # CLI output & prompts
├── generator_hook.py   # Spec → Runtime generation
├── commands/          # Command implementations
│   ├── setup_cmd.py
│   ├── spec_cmd.py
│   ├── runtime_cmd.py
│   ├── env_cmd.py
│   └── test_cmd.py
└── cli.py             # Main CLI entry point
```

## Contributing

We welcome contributions! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes with tests
4. Run tests: `pytest tests/`
5. Submit a pull request

## Roadmap

- [ ] Async API support
- [ ] Streaming interface
- [ ] Model performance analytics
- [ ] Cost tracking and budgets
- [ ] Multi-project management
- [ ] Web UI for configuration
- [ ] Integration with popular frameworks

## Support

- **Documentation**: [GitHub Wiki](https://github.com/your-org/llm-hub/wiki)
- **Issues**: [GitHub Issues](https://github.com/your-org/llm-hub/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-org/llm-hub/discussions)

## License

MIT License - see [LICENSE](LICENSE) file for details.

---

**Made with ❤️ for developers building with LLMs**
