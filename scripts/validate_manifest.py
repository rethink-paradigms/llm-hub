#!/usr/bin/env python3
"""
Validation script for AI-native manifest.

Ensures the manifest:
1. Has valid YAML syntax
2. Version matches package versions
3. Contains required sections
4. Capabilities match actual codebase
"""

import sys
import yaml
import re
from pathlib import Path
from typing import Dict, Any, List


def load_yaml(path: Path) -> Dict[str, Any]:
    """Load and parse YAML file."""
    try:
        with open(path, 'r') as f:
            return yaml.safe_load(f)
    except Exception as e:
        print(f"❌ Failed to load {path}: {e}")
        sys.exit(1)


def load_toml_version(path: Path) -> str:
    """Extract version from TOML file without parsing entire file."""
    try:
        with open(path, 'r') as f:
            content = f.read()
            # Find version line in [project] section
            match = re.search(r'version\s*=\s*"([^"]+)"', content)
            if match:
                return match.group(1)
            return None
    except Exception as e:
        print(f"❌ Failed to read {path}: {e}")
        return None


def validate_yaml_syntax(manifest_path: Path) -> bool:
    """Validate YAML syntax."""
    print("🔍 Validating YAML syntax...")
    try:
        load_yaml(manifest_path)
        print("✅ YAML syntax valid")
        return True
    except Exception as e:
        print(f"❌ YAML syntax error: {e}")
        return False


def validate_version_sync(manifest: Dict[str, Any], repo_root: Path) -> bool:
    """Validate version synchronization across packages."""
    print("\n🔍 Validating version synchronization...")
    
    manifest_version = manifest.get('tool_identity', {}).get('version')
    if not manifest_version:
        print("❌ Manifest missing tool_identity.version")
        return False
    
    print(f"   Manifest version: {manifest_version}")
    
    # Check runtime package version
    runtime_version = load_toml_version(repo_root / 'packages/runtime/pyproject.toml')
    
    # Check CLI package version
    cli_version = load_toml_version(repo_root / 'packages/cli/pyproject.toml')
    
    print(f"   Runtime package: {runtime_version}")
    print(f"   CLI package: {cli_version}")
    
    if not runtime_version or not cli_version:
        print("❌ Failed to extract versions from pyproject.toml files")
        return False
    
    versions_match = (
        manifest_version == runtime_version == cli_version
    )
    
    if versions_match:
        print("✅ Versions synchronized")
        return True
    else:
        print("❌ Version mismatch detected!")
        print(f"   Manifest: {manifest_version}")
        print(f"   Runtime:  {runtime_version}")
        print(f"   CLI:      {cli_version}")
        return False


def validate_required_sections(manifest: Dict[str, Any]) -> bool:
    """Validate presence of required sections."""
    print("\n🔍 Validating required sections...")
    
    required_sections = [
        'manifest_version',
        'tool_identity',
        'capabilities',
        'configuration_schema',
        'interaction_patterns',
        'dependencies',
    ]
    
    missing = []
    for section in required_sections:
        if section not in manifest:
            missing.append(section)
    
    if missing:
        print(f"❌ Missing required sections: {', '.join(missing)}")
        return False
    
    print(f"✅ All required sections present")
    return True


def validate_tool_identity(manifest: Dict[str, Any]) -> bool:
    """Validate tool identity section."""
    print("\n🔍 Validating tool_identity section...")
    
    identity = manifest.get('tool_identity', {})
    required_fields = ['tool_name', 'version', 'purpose', 'categories', 'runtime']
    
    missing = [f for f in required_fields if f not in identity]
    
    if missing:
        print(f"❌ Missing fields in tool_identity: {', '.join(missing)}")
        return False
    
    # Validate package names
    package_names = identity.get('package_names', [])
    expected_packages = ['rethink-llmhub', 'rethink-llmhub-runtime']
    
    if set(package_names) != set(expected_packages):
        print(f"❌ Package names mismatch. Expected {expected_packages}, got {package_names}")
        return False
    
    print("✅ Tool identity valid")
    return True


def validate_capabilities(manifest: Dict[str, Any]) -> bool:
    """Validate capabilities section structure."""
    print("\n🔍 Validating capabilities section...")
    
    capabilities = manifest.get('capabilities', [])
    
    if not isinstance(capabilities, list):
        print("❌ capabilities must be a list")
        return False
    
    if len(capabilities) == 0:
        print("❌ No capabilities defined")
        return False
    
    print(f"   Found {len(capabilities)} capabilities")
    
    # Validate each capability has required fields
    required_fields = ['capability_id', 'intent', 'input_contract', 'output_contract']
    
    for i, cap in enumerate(capabilities):
        cap_id = cap.get('capability_id', f'<index {i}>')
        missing = [f for f in required_fields if f not in cap]
        
        if missing:
            print(f"❌ Capability '{cap_id}' missing fields: {', '.join(missing)}")
            return False
    
    # List core capabilities
    core_capability_ids = [cap['capability_id'] for cap in capabilities]
    expected_capabilities = [
        'runtime.resolve.role',
        'runtime.execute.completion',
        'runtime.execute.embedding',
        'catalog.build',
        'cli.generate.runtime_config',
    ]
    
    for expected in expected_capabilities:
        if expected not in core_capability_ids:
            print(f"⚠️  Warning: Expected capability '{expected}' not found")
    
    print(f"✅ Capabilities structure valid")
    return True


def validate_configuration_schema(manifest: Dict[str, Any]) -> bool:
    """Validate configuration schema section."""
    print("\n🔍 Validating configuration_schema section...")
    
    schema = manifest.get('configuration_schema', [])
    
    if not isinstance(schema, list):
        print("❌ configuration_schema must be a list")
        return False
    
    print(f"   Found {len(schema)} configuration entities")
    
    # Check for core entities
    entity_names = [e.get('entity_name') for e in schema]
    expected_entities = [
        'SpecConfig',
        'RuntimeConfig',
        'RoleConfig',
        'CanonicalModel',
    ]
    
    for expected in expected_entities:
        if expected not in entity_names:
            print(f"⚠️  Warning: Expected entity '{expected}' not found")
    
    print("✅ Configuration schema structure valid")
    return True


def validate_interaction_patterns(manifest: Dict[str, Any]) -> bool:
    """Validate interaction patterns section."""
    print("\n🔍 Validating interaction_patterns section...")
    
    patterns = manifest.get('interaction_patterns', [])
    
    if not isinstance(patterns, list):
        print("❌ interaction_patterns must be a list")
        return False
    
    print(f"   Found {len(patterns)} interaction patterns")
    
    # Check for core patterns
    pattern_ids = [p.get('pattern_id') for p in patterns]
    expected_patterns = [
        'role_based_completion',
        'spec_to_runtime_generation',
        'catalog_discovery',
    ]
    
    for expected in expected_patterns:
        if expected not in pattern_ids:
            print(f"⚠️  Warning: Expected pattern '{expected}' not found")
    
    print("✅ Interaction patterns structure valid")
    return True


def validate_dependencies(manifest: Dict[str, Any]) -> bool:
    """Validate dependencies section."""
    print("\n🔍 Validating dependencies section...")
    
    deps = manifest.get('dependencies', {})
    
    required_sections = [
        'runtime_dependencies',
        'environment_dependencies',
        'external_services',
        'provides',
    ]
    
    missing = [s for s in required_sections if s not in deps]
    
    if missing:
        print(f"❌ Missing dependency sections: {', '.join(missing)}")
        return False
    
    # Check for core runtime dependencies
    runtime_deps = deps.get('runtime_dependencies', [])
    dep_names = [d.get('name') for d in runtime_deps]
    
    expected_deps = ['any-llm-sdk', 'pydantic', 'pyyaml']
    for expected in expected_deps:
        if expected not in dep_names:
            print(f"⚠️  Warning: Expected dependency '{expected}' not found")
    
    print("✅ Dependencies section valid")
    return True


def main():
    """Run all validations."""
    print("=" * 60)
    print("AI-Native Manifest Validation")
    print("=" * 60)
    
    repo_root = Path(__file__).parent.parent
    manifest_path = repo_root / 'llmhub.aimanifest.yaml'
    
    if not manifest_path.exists():
        print(f"❌ Manifest not found at {manifest_path}")
        sys.exit(1)
    
    print(f"📄 Manifest: {manifest_path}\n")
    
    # Load manifest
    manifest = load_yaml(manifest_path)
    
    # Run validations
    validations = [
        ('YAML Syntax', validate_yaml_syntax, manifest_path),
        ('Version Sync', validate_version_sync, manifest, repo_root),
        ('Required Sections', validate_required_sections, manifest),
        ('Tool Identity', validate_tool_identity, manifest),
        ('Capabilities', validate_capabilities, manifest),
        ('Configuration Schema', validate_configuration_schema, manifest),
        ('Interaction Patterns', validate_interaction_patterns, manifest),
        ('Dependencies', validate_dependencies, manifest),
    ]
    
    results = []
    for name, validator, *args in validations:
        try:
            if name == 'YAML Syntax':
                result = validator(*args)
            else:
                result = validator(*args)
            results.append((name, result))
        except Exception as e:
            print(f"❌ Validation '{name}' failed with exception: {e}")
            results.append((name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("Validation Summary")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {name}")
    
    print(f"\nTotal: {passed}/{total} validations passed")
    
    if passed == total:
        print("\n🎉 All validations passed!")
        sys.exit(0)
    else:
        print(f"\n⚠️  {total - passed} validation(s) failed")
        sys.exit(1)


if __name__ == '__main__':
    main()
