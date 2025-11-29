# LLM Hub

**Config-driven LLM resolver and catalog on top of any-llm**

LLM Hub is a production-grade system for managing large language models (LLMs) through declarative configuration rather than hardcoded provider/model names. It provides a unified runtime that resolves logical "roles" to actual LLM providers and models, plus a sophisticated catalog system that enriches models with cost, quality, and capability metadata.

---

## What is LLM Hub?

LLM Hub addresses a core challenge in LLM application development: **making model selection a configuration concern, not a code concern**.

Instead of writing:
```python
response = openai.chat.completions.create(
    model="gpt-4o",
    messages=[...]
)
```

You write:
```python
response = hub.completion(
    role="llm.inference",
    messages=[...]
)
```

The mapping from `"llm.inference"` to a specific provider/model lives in a declarative config file (`llmhub.yaml`), making it trivial to:
- Switch models without code changes
- A/B test different models
- Use different models per environment (dev vs prod)
- Let generators or optimization tools select models based on preferences

### Why it exists

- **Decouple business logic from model implementation**: Your application code references logical roles ("preprocess", "inference", "embedding"), not vendor-specific model strings.
- **Enable config-driven model selection**: Change models by editing a YAML file, not code.
- **Support intelligent model selection**: The catalog system provides rich metadata (cost tiers, quality scores, capabilities) that generators can use to automatically select optimal models based on declared preferences.
- **Standardize LLM access**: All LLM calls go through a single, consistent interface backed by [any-llm](https://github.com/llmhub/any-llm), which handles provider-specific quirks.

---

## Features Overview

### Runtime

The **runtime** is a lightweight Python library that:
- Loads machine configuration from `llmhub.yaml`
- Resolves logical role names (e.g., `"llm.inference"`) to concrete `provider:model` pairs
- Delegates actual LLM calls to [any-llm](https://github.com/llmhub/any-llm)
- Supports hooks for logging, observability, and cost tracking

**Key capabilities:**
- Chat completions and embeddings
- Environment-based configuration (dev, staging, prod)
- Parameter overrides per call
- Strict environment variable validation (optional)
- Before/after call hooks for instrumentation

### CLI

The **CLI** provides commands for:
- **Project initialization**: `llmhub init`, `llmhub setup`
- **Spec management**: Define high-level roles with preferences (cost, latency, quality)
- **Runtime generation**: `llmhub generate` — converts spec → runtime config
- **Catalog management**: `llmhub catalog show`, `llmhub catalog refresh`
- **Testing & validation**: `llmhub test`, `llmhub doctor`

### Catalog

The **catalog** is a local model database that:
- **Discovers** callable models via any-llm (which models are accessible on this machine)
- **Enriches** them with metadata from:
  - [models.dev](https://models.dev): pricing, limits, modalities, capabilities
  - [LMArena arena-catalog](https://github.com/lmarena/arena-catalog): quality scores and rankings
- **Derives** normalized tiers (1-5 scale) for cost, quality, reasoning, and creativity
- **Caches** the catalog to disk with TTL (default 24h) for fast access

**Catalog structure:**
- Each model becomes a `CanonicalModel` with fields like:
  - `provider`, `model_id`, `family`, `display_name`
  - `cost_tier`, `quality_tier`, `reasoning_tier`, `creative_tier` (1=best, 5=worst)
  - `arena_score`, `context_tokens`, `price_input_per_million`, `supports_tool_call`, etc.
  - `tags`: e.g., `["reasoning", "vision", "tools"]`

The catalog is used by:
- **Generators** (future): to select models that match spec preferences
- **CLI commands**: to display available models and their metadata
- **Future UI**: for interactive model exploration

### Future / WIP

- **Generator**: Automatically select optimal models based on spec preferences (partially implemented)
- **Web UI**: Interactive catalog browser and config editor
- **SaaS / Cloud**: Hosted catalog and model recommendation service

---

## Installation

### From PyPI (when published)

```bash
pip install rethink-llmhub llmhub-runtime
```

### From source (current development)

```bash
# Clone the repo
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
- **any-llm**: Installed automatically with `llmhub-runtime`
- **Provider API keys**: Set as environment variables (see below)

### Environment Variables

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

You can also use a `.env` file with `python-dotenv`.

---

## Quickstart – CLI

### 1. Initialize a project

```bash
# Quick init with minimal defaults
llmhub init

# Or interactive setup with full customization
llmhub setup
```

This creates:
- `llmhub.spec.yaml`: High-level specification of roles and preferences
- `.env.example`: Template for required environment variables

### 2. Configure providers

Set your API keys:

```bash
export OPENAI_API_KEY="sk-..."
export ANTHROPIC_API_KEY="sk-ant-..."
```

Or copy `.env.example` to `.env` and fill in your keys.

### 3. Generate runtime config

```bash
llmhub generate
```

This converts your spec into `llmhub.yaml` (the runtime config) by selecting concrete models based on your preferences.

**Options:**
- `--dry-run`: Preview what would be generated
- `--explain`: Show reasoning for model selections
- `--no-llm`: Use heuristic-only mode (no LLM-assisted generation)

### 4. Build and inspect the catalog

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

**Expected output:**
- Summary of models by provider
- Tables with model IDs, cost tiers, quality tiers
- Metadata like arena scores and tags

### 5. Test a role

```bash
llmhub test
```

Interactively tests a role by sending a sample prompt and displaying the response.

---

## Quickstart – Python Runtime Usage

### Basic example

```python
from llmhub_runtime import LLMHub

# Initialize hub with machine config
hub = LLMHub(config_path="llmhub.yaml")

# Resolve and call a role
response = hub.completion(
    role="llm.inference",
    messages=[
        {"role": "user", "content": "Explain quantum entanglement in simple terms."}
    ]
)

print(response)
```

### With parameter overrides

```python
response = hub.completion(
    role="llm.inference",
    messages=[{"role": "user", "content": "Write a haiku about code."}],
    params_override={"temperature": 1.0, "max_tokens": 100}
)
```

### Using embeddings

```python
embeddings = hub.embedding(
    role="llm.embedding",
    input=["hello world", "goodbye world"]
)
```

### With hooks for logging

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

### Strict environment validation

```python
# Fail fast if any required API keys are missing
hub = LLMHub(config_path="llmhub.yaml", strict_env=True)
```

---

## Catalog – How It Works

The catalog is the intelligence layer of LLM Hub. It combines three data sources to build a comprehensive model database:

### Data Sources

1. **any-llm** (local discovery)
   - Probes which models are actually callable on this machine
   - Uses your configured API keys to detect available models
   - Provides `provider:model_id` pairs

2. **models.dev** ([https://models.dev/api.json](https://models.dev/api.json))
   - Public API with rich metadata for popular LLMs
   - Provides: pricing (per million tokens), context limits, capabilities (tool calling, structured output, reasoning), modalities (text, image, audio), release dates, knowledge cutoffs

3. **LMArena arena-catalog** ([https://github.com/lmarena/arena-catalog](https://github.com/lmarena/arena-catalog))
   - Crowdsourced quality scores from human evaluations
   - Provides: ELO-style ratings, confidence intervals, category-specific scores

### Fusion Process

The catalog builder:
1. Fetches all three data sources
2. **Fuses** them using ID mapping (handles provider/model name variations)
3. Computes **global statistics** (quantiles for cost and quality)
4. **Derives tiers** (1-5 scale) for each model:
   - `cost_tier`: Based on price quantiles (1=cheapest, 5=most expensive)
   - `quality_tier`: Based on arena score quantiles or provider reputation (1=best, 5=worst)
   - `reasoning_tier`: Quality tier adjusted for reasoning support
   - `creative_tier`: Currently same as quality tier (future: tuned for creative tasks)
5. Generates **tags**: `reasoning`, `tools`, `vision`, `open-weights`, etc.

### Caching

- Cache location: `~/.config/llmhub/catalog.json` (macOS/Linux) or `%APPDATA%\llmhub\catalog.json` (Windows)
- Default TTL: 24 hours
- Force refresh: `llmhub catalog refresh`

### Canonical Model Schema

Each model in the catalog is a `CanonicalModel` with these key fields:

| Field | Type | Description |
|-------|------|-------------|
| `canonical_id` | str | Unique identifier (e.g., `openai:gpt-4o`) |
| `provider` | str | Provider name (e.g., `openai`) |
| `model_id` | str | Model identifier (e.g., `gpt-4o`) |
| `family` | str | Model family (e.g., `gpt-4`) |
| `display_name` | str | Human-friendly name |
| `cost_tier` | int | 1-5 (1=cheapest) |
| `quality_tier` | int | 1-5 (1=best) |
| `reasoning_tier` | int | 1-5 (1=best for reasoning) |
| `creative_tier` | int | 1-5 (1=best for creativity) |
| `arena_score` | float | LMArena rating |
| `price_input_per_million` | float | Cost per 1M input tokens |
| `price_output_per_million` | float | Cost per 1M output tokens |
| `context_tokens` | int | Max context window |
| `supports_tool_call` | bool | Function/tool calling support |
| `supports_reasoning` | bool | Extended reasoning (e.g., o1, o3) |
| `supports_structured_output` | bool | JSON schema output |
| `input_modalities` | list[str] | e.g., `["text", "image"]` |
| `output_modalities` | list[str] | e.g., `["text"]` |
| `tags` | list[str] | e.g., `["reasoning", "vision"]` |

### CLI Commands

| Command | Description |
|---------|-------------|
| `llmhub catalog refresh` | Force rebuild catalog from sources (ignores cache) |
| `llmhub catalog show` | Display cached catalog |
| `llmhub catalog show --provider <name>` | Filter by provider |
| `llmhub catalog show --details` | Show extra columns (arena score, tags) |

---

## Configuration Reference (High-Level)

LLM Hub uses two config files:

### 1. Spec File: `llmhub.spec.yaml` (human-facing)

This is the **high-level specification** of your project's LLM needs. It declares:
- Which providers to use
- What logical roles your app needs
- Preferences for each role (cost, latency, quality)

**Example:**

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
  llm.preprocess:
    kind: chat
    description: Fast preprocessing model to normalize input
    preferences:
      cost: low
      latency: low
      quality: medium
      providers:
        - openai

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

  llm.embedding:
    kind: embedding
    description: Vector embeddings for retrieval
    preferences:
      cost: low
      latency: low
      quality: medium
      providers:
        - openai

defaults:
  providers:
    - openai
    - anthropic
```

**Fields:**
- `project`: Project name
- `env`: Environment (dev, staging, prod)
- `providers`: Map of provider configs with API key env vars
- `roles`: Map of role names to role specs
  - `kind`: `chat`, `embedding`, `image`, `audio`, `tool`
  - `description`: What this role does
  - `preferences`: Hints for model selection
    - `cost`, `latency`, `quality`: `low`, `medium`, `high`
    - `providers`: Allowed providers for this role
  - `force_provider`, `force_model`: Override automatic selection
  - `mode_params`: Default params for this role
- `defaults`: Fallback preferences

### 2. Runtime Config: `llmhub.yaml` (machine-facing)

This is the **concrete runtime configuration** generated from the spec. It contains actual provider/model mappings.

**Example:**

```yaml
project: my-app
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

  llm.embedding:
    provider: openai
    model: text-embedding-3-small
    mode: embedding
    params:
      embedding_dim: 1536

defaults:
  provider: openai
  model: gpt-4o-mini
  mode: chat
  params:
    temperature: 0.3
    max_tokens: 1024
```

**Fields:**
- `project`, `env`: Same as spec
- `providers`: Map of provider configs (env vars only)
- `roles`: Map of role names to concrete configs
  - `provider`: Actual provider to use
  - `model`: Actual model ID
  - `mode`: LLM mode (chat, embedding, etc.)
  - `params`: Model parameters (temperature, max_tokens, etc.)
- `defaults`: Fallback role config

**Workflow:**
1. Edit `llmhub.spec.yaml` to declare roles and preferences
2. Run `llmhub generate` to produce `llmhub.yaml`
3. Runtime loads `llmhub.yaml` and resolves roles

---

## Tests and Test Execution Reports

### Running Tests

LLM Hub uses `pytest` for testing. Both packages have test suites:

```bash
# Test runtime library
cd packages/llmhub_runtime
pytest

# Test CLI and catalog
cd packages/llmhub
pytest

# Or run all tests from root
pytest packages/
```

### Test Execution Reports (TER)

LLM Hub includes a Test Execution Report (TER) system that generates structured JSON reports and optional Markdown summaries for each test run.

**Run tests with reporting:**

```bash
python -m llmhub.tools.run_tests_with_report

# Or use the Makefile shortcut
make test-report
```

This will:
- Execute the full test suite
- Generate a report in `reports/test-execution/`
- Files named: `TER-YYYYMMDD-HHMM-<short_sha>.json` (and optional `.md`)

**Report structure (JSON):**
- `project`, `run_id`, `commit`, `branch`, `timestamp`
- `environment`: Python version, OS, llmhub version
- `summary`: `total_tests`, `passed`, `failed`, `skipped`, `duration_seconds`, `status`
- `suites`: Array of test suites, each with:
  - `name`, `path`, `summary`, `tests[]`
  - Each test: `id`, `status`, `duration_seconds`, `tags`, `error` or `null`

**Interpreting reports:**
- Check `summary.status`: `"passed"` means all tests passed
- Check `summary.failed`: Number of failed tests
- Drill into `suites` for per-test details

Reports provide a historical record of test runs, useful for CI/CD pipelines, regression tracking, and debugging.

---

## Roadmap / Contributing

### Planned Features

- **Generator v2**: LLM-assisted model selection based on catalog + preferences
- **Web UI**: Interactive catalog browser, config editor, and model comparisons
- **SaaS offering**: Hosted catalog with live updates and model recommendations
- **Observability integrations**: Built-in support for LangSmith, Arize, etc.
- **Cost tracking**: Automatic cost estimation and budget alerts
- **A/B testing**: Multi-variant runtime configs for experimentation

### Contributing

Contributions are welcome! Key areas to explore:

- **Catalog sources**: Add more data sources (e.g., HuggingFace, Replicate)
- **Tier tuning**: Improve tier derivation algorithms
- **Provider support**: Expand any-llm provider coverage
- **Documentation**: Examples, tutorials, use cases

**Where to look in the codebase:**
- `packages/llmhub_runtime/src/llmhub_runtime/`: Core runtime library
- `packages/llmhub/src/llmhub/catalog/`: Catalog system
- `packages/llmhub/src/llmhub/commands/`: CLI commands
- `packages/llmhub/src/llmhub/generator_hook.py`: Generator logic (WIP)

### Release Process

The project uses an automated release script that handles version bumping, building, and PyPI uploads.

**Setup:**
1. Copy `.env.example` to `.env`
2. Add your PyPI API tokens:
   ```bash
   PYPI_API_TOKEN=pypi-...
   PYPI_TEST_API_TOKEN=pypi-...  # Optional, for TestPyPI
   ```

**Release both packages:**
```bash
# Bump patch version (0.1.5 -> 0.1.6)
python scripts/release.py patch

# Bump minor version (0.1.5 -> 0.2.0)
python scripts/release.py minor

# Bump major version (0.1.5 -> 1.0.0)
python scripts/release.py major

# Set specific version
python scripts/release.py --version 0.2.0
```

**Release individual packages:**
```bash
# Release only llmhub-runtime
python scripts/release.py patch --package llmhub-runtime

# Release only llmhub
python scripts/release.py minor --package llmhub
```

The script will:
1. Load PyPI tokens from `.env` (or prompt if not found)
2. Update version in `pyproject.toml` files
3. Build distribution packages
4. Verify package integrity
5. Optionally upload to TestPyPI first
6. Upload to production PyPI
7. Provide git commands for tagging

---

## License

MIT License - see individual package `pyproject.toml` files for details.

---

## Credits

Built by [Rethink Paradigms](https://rethinkparadigms.com).

Powered by:
- [any-llm](https://github.com/llmhub/any-llm): Universal LLM client
- [models.dev](https://models.dev): Model metadata API
- [LMArena](https://github.com/lmarena/arena-catalog): Crowdsourced quality scores
