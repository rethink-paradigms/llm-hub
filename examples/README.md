# LLM Hub Examples

This directory contains examples demonstrating various features and use cases of LLM Hub.

## AI-Native Documentation Example

### `agent_manifest_usage.py`

Demonstrates how AI agents efficiently consume the AI-native manifest to understand and integrate LLM Hub.

**Usage:**

```bash
# Run agent integration simulation
python examples/agent_manifest_usage.py

# Compare manifest vs README approaches
python examples/agent_manifest_usage.py --compare
```

**What it demonstrates:**

1. **Tool Discovery**: Extracting basic tool identity and purpose
2. **Capability Queries**: Finding specific capabilities by ID
3. **Contract Extraction**: Getting input/output contracts for capabilities
4. **Configuration Understanding**: Parsing configuration schema entities
5. **Pattern Following**: Extracting interaction patterns with state transitions
6. **Dependency Validation**: Checking environment prerequisites

**Key Insights:**

- **Token Efficiency**: Manifest-based approach uses ~10x fewer tokens than parsing README
- **Precision**: Structured queries vs full-text search
- **Contracts**: Explicit input/output contracts vs inferring from examples
- **Queryable**: Direct access to specific sections vs sequential reading

**Example Output:**

```
AI Agent Task: Integrate LLM Hub to abstract OpenAI calls
======================================================================

🔍 Step 1: Discover tool identity
   Tool: llm-hub v1.0.3
   Purpose: Config-driven LLM resolver and catalog system...

🔍 Step 2: Query capability for 'runtime.execute.completion'
   Intent: Execute LLM chat completion using role-based configuration
   Input parameters:
     - role (string, required): Logical role identifier
     - messages (array[object], required): Chat message history...

✅ Agent Integration Complete
```

## Future Examples

The following examples are planned for future releases:

### Programmatic API Examples

#### `catalog_programmatic_access.py`

Demonstrates programmatic catalog querying and filtering without using the CLI.

**Usage:**

```bash
python examples/catalog_programmatic_access.py
```

**What it demonstrates:**

1. **Basic Catalog Building**: Loading the full model catalog
2. **Provider Filtering**: Getting models from specific providers
3. **Cost-Quality Search**: Finding cheapest high-quality models
4. **Capability Filtering**: Finding models with specific capabilities (reasoning, vision)
5. **Multi-Modal Models**: Querying vision-capable models
6. **Provider Comparison**: Calculating and comparing provider statistics

**Key Functions:**
- `build_catalog()`: Build full catalog from data sources
- `get_catalog(provider=..., tags=...)`: Filter catalog by criteria
- Accessing model metadata: `model.cost_tier`, `model.quality_tier`, `model.tags`

**Example Code:**

```python
from llmhub_cli import build_catalog, get_catalog

# Get all models
catalog = build_catalog()

# Get OpenAI models only
openai = get_catalog(provider="openai")

# Get models with reasoning capability
reasoning = get_catalog(tags=["reasoning"])

# Find cheapest high-quality models
cheap_quality = [
    m for m in catalog.models
    if m.cost_tier <= 2 and m.quality_tier <= 3
]
```

#### `runtime_generation_programmatic.py`

Demonstrates programmatic runtime generation from spec configurations.

**Usage:**

```bash
python examples/runtime_generation_programmatic.py
```

**What it demonstrates:**

1. **Basic Generation**: Converting spec to runtime programmatically
2. **Generation with Explanations**: Understanding model selection decisions
3. **Saving Runtime**: Persisting generated configs to files
4. **Multi-Environment**: Generating configs for dev/staging/prod
5. **Spec Validation**: Validating specs before generation
6. **Programmatic Spec Creation**: Building specs in code without YAML

**Key Functions:**
- `load_spec(path)`: Load spec from YAML file
- `validate_spec(spec)`: Validate spec structure and constraints
- `generate_runtime_from_spec(spec, options)`: Generate runtime config
- `save_runtime(path, config)`: Save runtime to file
- `load_runtime(path)`: Load runtime from file

**Example Code:**

```python
from llmhub_cli import (
    load_spec,
    generate_runtime_from_spec,
    save_runtime,
)
from llmhub_cli.generator import GeneratorOptions
from llmhub_cli.spec import validate_spec

# Load and validate spec
spec = load_spec("llmhub.spec.yaml")
result = validate_spec(spec)

if result.valid:
    # Generate runtime with explanations
    options = GeneratorOptions(explain=True)
    gen_result = generate_runtime_from_spec(spec, options)
    
    # Save to file
    save_runtime("llmhub.yaml", gen_result.runtime)
    
    # Print explanations
    for role, explanation in gen_result.explanations.items():
        print(f"{role}: {explanation}")
```

### Runtime Library Examples

- **Basic Usage**: Simple completion and embedding calls
- **Hooks and Observability**: Implementing cost tracking and logging hooks
- **Multi-Environment**: Managing dev/staging/prod configurations
- **Error Handling**: Graceful degradation and fallback strategies

### CLI Examples

- **Project Setup**: Initializing new projects with best practices
- **Catalog Exploration**: Querying and filtering the model catalog
- **Spec-Driven Generation**: Converting preferences to runtime configs
- **Testing Workflows**: Validating roles and configurations

### Advanced Patterns

- **A/B Testing**: Running experiments with different models
- **Cost Optimization**: Selecting models based on budget constraints
- **Quality Tuning**: Iterating on quality preferences
- **Custom Generators**: Extending the selection algorithm

## Contributing Examples

Have an interesting use case? Contributions welcome!

1. Create example script with clear documentation
2. Include usage instructions and expected output
3. Add entry to this README
4. Submit a pull request

**Guidelines:**
- Keep examples focused on a single concept
- Include error handling for robustness
- Add comments explaining key steps
- Provide sample output in docstrings or README

## Related Documentation

- [AI-Native Manifest](../.aimanifest/README.md) - How agents consume the manifest
- [Main README](../README.md) - Project overview and quickstart
- [CLI README](../packages/cli/README.md) - CLI reference
- [Runtime README](../packages/runtime/README.md) - Runtime library API

---

**License**: MIT  
**Contact**: info@rethink-paradigms.com
