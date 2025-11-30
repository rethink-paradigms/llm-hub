# AI-Native Documentation for LLM Hub

This directory contains AI-native documentation for LLM Hub—structured, machine-first capability metadata optimized for AI agent consumption.

## What is AI-Native Documentation?

Traditional documentation is optimized for human reading: verbose, narrative, elaborative. AI agents waste significant context window tokens parsing lengthy prose to extract capability information.

**AI-native documentation** provides the same information in a structured, queryable format that agents can consume efficiently—typically using **10x fewer tokens** for equivalent understanding.

## The Manifest File

**Location**: `/llmhub.aimanifest.yaml` (repository root)

This YAML file contains everything an AI agent needs to understand and integrate LLM Hub:

### Structure Overview

1. **Tool Identity** - Basic metadata (name, version, purpose, runtime requirements)
2. **Capabilities Graph** - Hierarchical tree of what the tool can do
3. **Configuration Schema** - Structured description of configuration entities
4. **Interaction Patterns** - Common workflows as state machines
5. **Dependency Graph** - What the tool requires and provides
6. **Error Taxonomy** - Structured error codes and recovery strategies
7. **Performance Characteristics** - Latency, throughput, resource usage

### Key Features

- **Contract-Based**: Input/output contracts for all capabilities
- **Constraint-Aware**: Explicit failure modes and prerequisites
- **Cost-Transparent**: Latency and resource costs documented
- **Hook-Enabled**: Observability and extension points described
- **Queryable**: Structured format enables semantic search

## Usage for AI Agents

### Discovery Phase

When an AI agent encounters LLM Hub, it should:

1. **Retrieve manifest**: Read `llmhub.aimanifest.yaml`
2. **Parse capabilities**: Scan the `capabilities` section to determine if the tool matches task requirements
3. **Filter relevant capabilities**: Extract only the capabilities needed for the current task
4. **Extract interaction patterns**: Identify the workflow pattern that matches the task

### Integration Phase

Use the manifest to:

1. **Validate prerequisites**: Check `dependencies.environment_dependencies` for required environment variables
2. **Understand configuration**: Parse `configuration_schema` to generate valid config files
3. **Execute pattern**: Follow `state_transitions` in the relevant interaction pattern
4. **Handle errors**: Reference `error_taxonomy` for recovery strategies

### Example: Agent Task

**Task**: "Use LLM Hub to abstract OpenAI calls in my application"

**Agent workflow**:

1. Read `llmhub.aimanifest.yaml` (~1,500 tokens vs. ~15,000 tokens for full README)
2. Query `capabilities` → find `runtime.execute.completion`
3. Extract input/output contracts, constraints, failure modes
4. Query `configuration_schema` → find `RuntimeConfig` and `RoleConfig`
5. Query `interaction_patterns` → find `role_based_completion`
6. Follow state transitions to implement integration
7. Reference `error_taxonomy` for error handling

**Token efficiency**: ~90% reduction vs. traditional documentation

## Manifest Schema Compliance

This manifest follows the **aimanifest-v1.0** schema, a proposed standard for AI-native documentation.

### Schema Version: 1.0

**Core Sections** (required):
- Tool Identity
- Capabilities Graph
- Configuration Schema
- Interaction Patterns
- Dependency Graph

**Extended Sections** (optional):
- Error Taxonomy
- Performance Characteristics
- Security Model
- Versioning Policy

## For Human Developers

While optimized for AI consumption, the manifest remains **human-readable** for quick reference:

- YAML format with clear structure
- Semantic field names
- Inline descriptions
- Example values where helpful

**For deep learning**, use the traditional documentation:
- [Main README](../README.md) - Overview, installation, quickstart
- [CLI README](../packages/cli/README.md) - CLI command reference
- [Runtime README](../packages/runtime/README.md) - Runtime library API
- [Project Wiki](https://github.com/rethink-paradigms/llm-hub/wiki) - Comprehensive guides

## Maintenance

The manifest is a **first-class artifact** and should be:

- ✅ Updated with every release
- ✅ Version-synced with package versions
- ✅ Validated in CI/CD
- ✅ Reviewed for accuracy during API changes

### Update Checklist

When adding/changing capabilities:

1. [ ] Update corresponding capability in `capabilities` section
2. [ ] Add/update configuration schema entities if needed
3. [ ] Document new interaction patterns
4. [ ] Update error taxonomy for new error types
5. [ ] Increment `manifest_version` if schema changes
6. [ ] Validate YAML syntax

### Validation

```bash
# Validate YAML syntax
python -c "import yaml; yaml.safe_load(open('llmhub.aimanifest.yaml'))"

# Check version sync
grep version llmhub.aimanifest.yaml
grep version packages/runtime/pyproject.toml
grep version packages/cli/pyproject.toml
```

## Distribution

The manifest is distributed:

1. **In repository**: At repository root for easy discovery
2. **In PyPI packages**: Included in both `rethink-llmhub` and `rethink-llmhub-runtime`
3. **Via HTTP**: Accessible at package URLs
4. **Version-tagged**: Manifest version matches package version

## Feedback and Contributions

This is an experimental format. Feedback welcome:

- Open issues for manifest inaccuracies
- Suggest improvements to schema
- Share agent integration experiences

**Goal**: Establish AI-native documentation as a standard practice across the software ecosystem.

## Related Resources

- [Design Document](../.qoder/quests/ai-native-documentation-concept.md) - Full concept and rationale
- [aimanifest Schema](https://github.com/ai-native-docs/aimanifest) - Proposed standard (hypothetical)
- [LLM Hub Documentation](../README.md) - Traditional human documentation

---

**License**: MIT  
**Maintained by**: Rethink Paradigms  
**Contact**: info@rethink-paradigms.com
