#!/usr/bin/env python3
"""
Script to update all import statements in the CLI package from llmhub to llmhub_cli
and update old SP module paths to new reorganized structure.
"""

import os
import re
from pathlib import Path

# Mapping of old SP import paths to new functional grouping paths
IMPORT_MAPPINGS = {
    # Catalog (stays the same except namespace)
    r'from llmhub\.catalog': r'from llmhub_cli.catalog',
    r'import llmhub\.catalog': r'import llmhub_cli.catalog',
    
    # Commands (update module names - drop _cmd suffix)
    r'from llmhub\.commands import setup_cmd': r'from llmhub_cli.commands import setup',
    r'from llmhub\.commands import spec_cmd': r'from llmhub_cli.commands import spec',
    r'from llmhub\.commands import runtime_cmd': r'from llmhub_cli.commands import runtime',
    r'from llmhub\.commands import env_cmd': r'from llmhub_cli.commands import env',
    r'from llmhub\.commands import test_cmd': r'from llmhub_cli.commands import test',
    r'from llmhub\.commands import catalog_cmd': r'from llmhub_cli.commands import catalog',
    r'from \.commands import (setup_cmd|spec_cmd|runtime_cmd|env_cmd|test_cmd|catalog_cmd)': r'from .commands import \1',
    
    # Generator SP1 - Spec Schema
    r'from llmhub\.generator\.sp1_spec_schema': r'from llmhub_cli.generator.spec',
    r'import llmhub\.generator\.sp1_spec_schema': r'import llmhub_cli.generator.spec',
    
    # Generator SP2 - Needs Interpreter  
    r'from llmhub\.generator\.sp2_needs_interpreter': r'from llmhub_cli.generator.needs',
    r'import llmhub\.generator\.sp2_needs_interpreter': r'import llmhub_cli.generator.needs',
    
    # Generator SP3 - Needs Schema
    r'from llmhub\.generator\.sp3_needs_schema': r'from llmhub_cli.generator.needs',
    r'import llmhub\.generator\.sp3_needs_schema': r'import llmhub_cli.generator.needs',
    
    # Generator SP4 - Catalog View
    r'from llmhub\.generator\.sp4_catalog_view': r'from llmhub_cli.generator.catalog_view',
    r'import llmhub\.generator\.sp4_catalog_view': r'import llmhub_cli.generator.catalog_view',
    
    # Generator SP5 - Filter Candidates
    r'from llmhub\.generator\.sp5_filter_candidates': r'from llmhub_cli.generator.selection',
    r'import llmhub\.generator\.sp5_filter_candidates': r'import llmhub_cli.generator.selection',
    
    # Generator SP6 - Weights
    r'from llmhub\.generator\.sp6_weights': r'from llmhub_cli.generator.selection',
    r'import llmhub\.generator\.sp6_weights': r'import llmhub_cli.generator.selection',
    
    # Generator SP7 - Scoring Engine
    r'from llmhub\.generator\.sp7_scoring_engine': r'from llmhub_cli.generator.selection',
    r'import llmhub\.generator\.sp7_scoring_engine': r'import llmhub_cli.generator.selection',
    
    # Generator SP8 - Relaxation Engine
    r'from llmhub\.generator\.sp8_relaxation_engine': r'from llmhub_cli.generator.selection',
    r'import llmhub\.generator\.sp8_relaxation_engine': r'import llmhub_cli.generator.selection',
    
    # Generator SP9 - Selector Orchestrator
    r'from llmhub\.generator\.sp9_selector_orchestrator': r'from llmhub_cli.generator.selection',
    r'import llmhub\.generator\.sp9_selector_orchestrator': r'import llmhub_cli.generator.selection',
    
    # Generator SP10 - Machine Config Emitter
    r'from llmhub\.generator\.sp10_machine_config_emitter': r'from llmhub_cli.generator.emitter',
    r'import llmhub\.generator\.sp10_machine_config_emitter': r'import llmhub_cli.generator.emitter',
    
    # General generator namespace
    r'from llmhub\.generator': r'from llmhub_cli.generator',
    r'import llmhub\.generator': r'import llmhub_cli.generator',
    
    # Core modules
    r'from llmhub\.spec_models': r'from llmhub_cli.spec_models',
    r'from llmhub\.context': r'from llmhub_cli.context',
    r'from llmhub\.runtime_io': r'from llmhub_cli.runtime_io',
    r'from llmhub\.env_manager': r'from llmhub_cli.env_manager',
    r'from llmhub\.ux': r'from llmhub_cli.ux',
    r'from llmhub\.generator_hook': r'from llmhub_cli.generator_hook',
    
    # Tools
    r'from llmhub\.tools': r'from llmhub_cli.tools',
}

# Additional specific import fixes
SPECIFIC_IMPORTS = {
    'filter_candidates': 'filter',
    'derive_weights': 'weights',
    'score_candidates': 'scorer',
    'relax_and_select': 'relaxer',
    'SelectionResult': 'selector_models',
}

def update_file(filepath: Path):
    """Update imports in a single file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Apply all import mappings
        for old_pattern, new_replacement in IMPORT_MAPPINGS.items():
            content = re.sub(old_pattern, new_replacement, content)
        
        # Additional fixes for specific imports that moved
        # Fix SP module references that need updated import names
        content = re.sub(r'sp1_spec_schema\.', 'spec.', content)
        content = re.sub(r'sp2_needs_interpreter\.', 'needs.', content)
        content = re.sub(r'sp3_needs_schema\.', 'needs.', content)
        content = re.sub(r'sp4_catalog_view\.', 'catalog_view.', content)
        content = re.sub(r'sp5_filter_candidates\.', 'selection.', content)
        content = re.sub(r'sp6_weights\.', 'selection.', content)
        content = re.sub(r'sp7_scoring_engine\.', 'selection.', content)
        content = re.sub(r'sp8_relaxation_engine\.', 'selection.', content)
        content = re.sub(r'sp9_selector_orchestrator\.', 'selection.', content)
        content = re.sub(r'sp10_machine_config_emitter\.', 'emitter.', content)
        
        # Update command module references (drop _cmd suffix)
        content = re.sub(r'\bsetup_cmd\.', 'setup.', content)
        content = re.sub(r'\bspec_cmd\.', 'spec.', content)
        content = re.sub(r'\bruntime_cmd\.', 'runtime.', content)
        content = re.sub(r'\benv_cmd\.', 'env.', content)
        content = re.sub(r'\btest_cmd\.', 'test.', content)
        content = re.sub(r'\bcatalog_cmd\.', 'catalog.', content)
        
        # Only write if content changed
        if content != original_content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Updated: {filepath}")
            return True
        return False
    except Exception as e:
        print(f"Error processing {filepath}: {e}")
        return False

def main():
    """Update all Python files in the CLI package."""
    cli_dir = Path("/Users/samanvayayagsen/project/rethink-paradigms/llm-hub/packages/cli/src/llmhub_cli")
    
    if not cli_dir.exists():
        print(f"CLI directory not found: {cli_dir}")
        return
    
    updated_count = 0
    for py_file in cli_dir.rglob("*.py"):
        if update_file(py_file):
            updated_count += 1
    
    # Also update test files
    test_dir = Path("/Users/samanvayayagsen/project/rethink-paradigms/llm-hub/packages/cli/tests")
    if test_dir.exists():
        for py_file in test_dir.rglob("*.py"):
            if update_file(py_file):
                updated_count += 1
    
    print(f"\nTotal files updated: {updated_count}")

if __name__ == "__main__":
    main()
