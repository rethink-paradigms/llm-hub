# AI-Native Manifest Quick Reference

Quick lookup guide for the LLM Hub AI-native manifest structure.

## File Location

`/llmhub.aimanifest.yaml` (repository root)

## Top-Level Sections

```yaml
manifest_version: "1.0"
manifest_schema: "https://github.com/ai-native-docs/aimanifest/v1"

tool_identity:        # Basic tool metadata
capabilities:         # What the tool can do
configuration_schema: # Configuration entities
interaction_patterns: # Common workflows
dependencies:         # Requirements and provides
error_taxonomy:       # Error codes and recovery
performance_characteristics: # Latency and resource usage
metadata:            # Manifest metadata
```

## Quick Queries

### Find a Capability

```python
capabilities = manifest['capabilities']
cap = [c for c in capabilities if c['capability_id'] == 'runtime.execute.completion'][0]
```

**Available Capabilities**:
- `runtime.resolve.role`
- `runtime.execute.completion`
- `runtime.execute.embedding`
- `runtime.validate.environment`
- `cli.init.project`
- `cli.generate.runtime_config`
- `catalog.build`
- `catalog.query`
- `cli.test.role`
- `cli.validate.environment`

### Find a Configuration Entity

```python
schema = manifest['configuration_schema']
entity = [e for e in schema if e['entity_name'] == 'RuntimeConfig'][0]
```

**Available Entities**:
- `SpecConfig`
- `SpecProviderConfig`
- `RoleSpec`
- `Preferences`
- `RuntimeConfig`
- `ProviderConfig`
- `RoleConfig`
- `RoleDefaultsConfig`
- `CanonicalModel`

### Find an Interaction Pattern

```python
patterns = manifest['interaction_patterns']
pattern = [p for p in patterns if p['pattern_id'] == 'role_based_completion'][0]
```

**Available Patterns**:
- `role_based_completion`
- `spec_to_runtime_generation`
- `catalog_discovery`

### Get Environment Dependencies

```python
env_deps = manifest['dependencies']['environment_dependencies']
```

**Required Variables** (conditional):
- `OPENAI_API_KEY`
- `ANTHROPIC_API_KEY`
- `GEMINI_API_KEY`
- `DEEPSEEK_API_KEY`
- `QWEN_API_KEY`
- `MISTRAL_API_KEY`

## Capability Structure

Each capability has:

```yaml
- capability_id: "unique.hierarchical.id"
  intent: "What this capability achieves"
  input_contract:
    - name: parameter_name
      type: string | array | object | ...
      required: true | false
      description: "What this parameter does"
  output_contract:
    - name: output_name
      type: return_type
      description: "What this output contains"
  constraints:
    - "Prerequisite or limitation"
  failure_modes:
    - error: ErrorName
      condition: "When this error occurs"
  cost_model:
    latency: "Timing estimate"
    financial: "Cost estimate (if applicable)"
```

## Configuration Entity Structure

Each configuration entity has:

```yaml
- entity_name: ConfigEntityName
  file_name: config_file.yaml  # Optional
  purpose: "What this entity configures"
  schema:
    - field: field_name
      type: field_type
      required: true | false
      semantic: "What this field means"
      example: "Example value"  # Optional
  validation_rules:
    - "Validation constraint"
  related_entities:
    - RelatedEntityName
```

## Interaction Pattern Structure

Each pattern has:

```yaml
- pattern_id: pattern_identifier
  intent: "What workflow this achieves"
  entry_conditions:
    - "Prerequisite for starting"
  state_transitions:
    - step: 1
      action: "What happens"
      result: "Outcome"
  exit_conditions:
    - outcome: success | failure
      condition: "When this outcome occurs"
      returns: "What is returned"
  side_effects:
    - "Observable effect"
```

## Common Agent Workflows

### Workflow 1: Understand Capability

```python
# 1. Load manifest
manifest = yaml.safe_load(open('llmhub.aimanifest.yaml'))

# 2. Find capability
cap = next(c for c in manifest['capabilities'] 
           if c['capability_id'] == 'runtime.execute.completion')

# 3. Extract contracts
inputs = cap['input_contract']
outputs = cap['output_contract']
constraints = cap['constraints']
failures = cap['failure_modes']
```

### Workflow 2: Generate Configuration

```python
# 1. Find configuration entity
entity = next(e for e in manifest['configuration_schema']
              if e['entity_name'] == 'RuntimeConfig')

# 2. Extract schema
schema = entity['schema']

# 3. Generate valid config
config = {}
for field in schema:
    if field['required']:
        # Populate required fields
        config[field['field']] = generate_value(field)
```

### Workflow 3: Follow Workflow

```python
# 1. Find interaction pattern
pattern = next(p for p in manifest['interaction_patterns']
               if p['pattern_id'] == 'role_based_completion')

# 2. Check entry conditions
for condition in pattern['entry_conditions']:
    validate(condition)

# 3. Execute state transitions
for step in pattern['state_transitions']:
    execute(step)

# 4. Handle exit conditions
for exit_cond in pattern['exit_conditions']:
    if matches(exit_cond['condition']):
        handle(exit_cond['outcome'])
```

## Token Estimation

**Full manifest**: ~36KB = ~9,148 tokens

**Typical agent queries** (by section):
- Tool identity: ~100 tokens
- Single capability: ~200 tokens
- Configuration entity: ~150 tokens
- Interaction pattern: ~250 tokens
- Environment deps: ~100 tokens

**Total for integration task**: ~800-1,500 tokens (vs. ~4,700 for README)

## Validation

```bash
# Validate manifest
make validate-manifest

# Or directly
python scripts/validate_manifest.py
```

**Validation checks**:
- ✅ YAML syntax
- ✅ Version sync (manifest matches packages)
- ✅ Required sections present
- ✅ Structure validity

## Example Usage

See [examples/agent_manifest_usage.py](../examples/agent_manifest_usage.py)

```bash
# Run agent simulation
python examples/agent_manifest_usage.py

# Compare approaches
python examples/agent_manifest_usage.py --compare
```

## Related Documentation

- [Full README](./.aimanifest/README.md) - Complete AI-native docs guide
- [Design Document](../.qoder/quests/ai-native-documentation-concept.md) - Concept and rationale
- [Implementation Summary](../AI_NATIVE_DOCS.md) - What was built and why

---

**Version**: 1.0.3  
**Schema**: aimanifest-v1.0  
**Last Updated**: December 1, 2025
