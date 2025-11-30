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
