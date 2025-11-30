#!/usr/bin/env python3
"""
Example: AI Agent consuming the AI-native manifest.

This script demonstrates how an AI agent would efficiently extract
capability information from the manifest compared to parsing a README.
"""

import yaml
from pathlib import Path
from typing import Dict, Any, List


def load_manifest(manifest_path: Path) -> Dict[str, Any]:
    """Load the AI-native manifest."""
    with open(manifest_path, 'r') as f:
        return yaml.safe_load(f)


def discover_tool_identity(manifest: Dict[str, Any]) -> Dict[str, Any]:
    """Extract basic tool identity (minimal overhead)."""
    identity = manifest['tool_identity']
    return {
        'tool_name': identity['tool_name'],
        'version': identity['version'],
        'purpose': identity['purpose'],
        'categories': identity['categories'],
    }


def find_capability(manifest: Dict[str, Any], capability_id: str) -> Dict[str, Any]:
    """Find a specific capability by ID."""
    capabilities = manifest['capabilities']
    for cap in capabilities:
        if cap.get('capability_id') == capability_id:
            return cap
    return None


def extract_capability_contract(capability: Dict[str, Any]) -> Dict[str, Any]:
    """Extract input/output contract from capability."""
    return {
        'capability_id': capability['capability_id'],
        'intent': capability['intent'],
        'input_contract': capability['input_contract'],
        'output_contract': capability['output_contract'],
        'constraints': capability.get('constraints', []),
        'failure_modes': capability.get('failure_modes', []),
    }


def find_configuration_entity(manifest: Dict[str, Any], entity_name: str) -> Dict[str, Any]:
    """Find a configuration schema entity by name."""
    schema = manifest['configuration_schema']
    for entity in schema:
        if entity.get('entity_name') == entity_name:
            return entity
    return None


def extract_interaction_pattern(manifest: Dict[str, Any], pattern_id: str) -> Dict[str, Any]:
    """Extract an interaction pattern by ID."""
    patterns = manifest['interaction_patterns']
    for pattern in patterns:
        if pattern.get('pattern_id') == pattern_id:
            return pattern
    return None


def get_environment_dependencies(manifest: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Extract required environment variables."""
    deps = manifest['dependencies']
    return deps.get('environment_dependencies', [])


def simulate_agent_task():
    """
    Simulate an AI agent task: "Use LLM Hub to abstract OpenAI calls"
    
    This demonstrates the workflow an agent would follow to understand
    and integrate LLM Hub efficiently.
    """
    
    print("=" * 70)
    print("AI Agent Task: Integrate LLM Hub to abstract OpenAI calls")
    print("=" * 70)
    print()
    
    # Load manifest
    repo_root = Path(__file__).parent.parent
    manifest_path = repo_root / 'llmhub.aimanifest.yaml'
    
    print(f"📥 Loading manifest from: {manifest_path}")
    manifest = load_manifest(manifest_path)
    print(f"✅ Manifest loaded ({len(str(manifest))} characters)")
    print()
    
    # Step 1: Discover tool identity
    print("🔍 Step 1: Discover tool identity")
    identity = discover_tool_identity(manifest)
    print(f"   Tool: {identity['tool_name']} v{identity['version']}")
    print(f"   Purpose: {identity['purpose']}")
    print(f"   Categories: {', '.join(identity['categories'])}")
    print()
    
    # Step 2: Find completion capability
    print("🔍 Step 2: Query capability for 'runtime.execute.completion'")
    capability = find_capability(manifest, 'runtime.execute.completion')
    if capability:
        contract = extract_capability_contract(capability)
        print(f"   Intent: {contract['intent']}")
        print(f"   Input parameters:")
        for param in contract['input_contract']:
            required = "required" if param.get('required') else "optional"
            print(f"     - {param['name']} ({param['type']}, {required}): {param['description']}")
        print(f"   Constraints: {len(contract['constraints'])} constraint(s)")
        print(f"   Failure modes: {len(contract['failure_modes'])} mode(s)")
    print()
    
    # Step 3: Understand configuration
    print("🔍 Step 3: Query configuration schema for 'RuntimeConfig'")
    runtime_config = find_configuration_entity(manifest, 'RuntimeConfig')
    if runtime_config:
        print(f"   Purpose: {runtime_config['purpose']}")
        print(f"   File: {runtime_config.get('file_name', 'N/A')}")
        print(f"   Fields: {len(runtime_config['schema'])} field(s)")
        for field in runtime_config['schema'][:3]:  # Show first 3
            print(f"     - {field['field']} ({field['type']}): {field['semantic']}")
    print()
    
    # Step 4: Get interaction pattern
    print("🔍 Step 4: Extract interaction pattern 'role_based_completion'")
    pattern = extract_interaction_pattern(manifest, 'role_based_completion')
    if pattern:
        print(f"   Intent: {pattern['intent']}")
        print(f"   State transitions: {len(pattern['state_transitions'])} step(s)")
        print(f"   Entry conditions: {len(pattern['entry_conditions'])} condition(s)")
        print(f"   Exit conditions: {len(pattern['exit_conditions'])} outcome(s)")
    print()
    
    # Step 5: Check environment dependencies
    print("🔍 Step 5: Validate environment prerequisites")
    env_deps = get_environment_dependencies(manifest)
    print(f"   Required environment variables: {len(env_deps)} variable(s)")
    for dep in env_deps[:3]:  # Show first 3
        print(f"     - {dep['name']} ({dep['condition']})")
    print()
    
    # Summary
    print("=" * 70)
    print("✅ Agent Integration Complete")
    print("=" * 70)
    print()
    print("Agent now understands:")
    print("  ✅ What LLM Hub does (tool identity)")
    print("  ✅ How to call completions (capability contract)")
    print("  ✅ What configuration is needed (RuntimeConfig schema)")
    print("  ✅ Workflow to follow (role_based_completion pattern)")
    print("  ✅ Prerequisites required (environment variables)")
    print()
    print("Token efficiency estimate:")
    print("  - Manifest approach: ~1,500 tokens")
    print("  - README approach: ~15,000 tokens")
    print("  - Efficiency gain: ~10x")
    print()


def compare_approaches():
    """
    Compare manifest-based vs README-based approaches.
    """
    
    print("=" * 70)
    print("Comparison: Manifest vs README Approach")
    print("=" * 70)
    print()
    
    repo_root = Path(__file__).parent.parent
    manifest_path = repo_root / 'llmhub.aimanifest.yaml'
    readme_path = repo_root / 'README.md'
    
    # Load both files
    with open(manifest_path, 'r') as f:
        manifest_content = f.read()
    
    with open(readme_path, 'r') as f:
        readme_content = f.read()
    
    # Rough token estimation (1 token ≈ 4 characters)
    manifest_tokens = len(manifest_content) // 4
    readme_tokens = len(readme_content) // 4
    
    print("File Sizes:")
    print(f"  Manifest: {len(manifest_content):,} characters (~{manifest_tokens:,} tokens)")
    print(f"  README:   {len(readme_content):,} characters (~{readme_tokens:,} tokens)")
    print()
    
    print("Information Density:")
    print(f"  Manifest: Structured, queryable, contract-based")
    print(f"  README:   Narrative, sequential, example-based")
    print()
    
    print("For task: 'Integrate LLM Hub for OpenAI abstraction'")
    print(f"  Manifest: Extract 5 sections = ~1,500 tokens")
    print(f"  README:   Parse entire doc = ~{readme_tokens:,} tokens")
    print(f"  Efficiency: {readme_tokens / 1500:.1f}x improvement")
    print()
    
    print("Agent Capabilities:")
    print("  Manifest:")
    print("    ✅ Semantic search by capability ID")
    print("    ✅ Extract exact contracts (input/output)")
    print("    ✅ Query configuration requirements")
    print("    ✅ Follow structured patterns")
    print()
    print("  README:")
    print("    ⚠️  Full-text search (less precise)")
    print("    ⚠️  Parse prose for contracts (error-prone)")
    print("    ⚠️  Infer configuration from examples")
    print("    ⚠️  Extract patterns from narratives")
    print()


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == '--compare':
        compare_approaches()
    else:
        simulate_agent_task()
        print()
        print("💡 Run with --compare to see detailed comparison")
        print()
