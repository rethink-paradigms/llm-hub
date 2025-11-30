# Changelog - rethink-llmhub

All notable changes to the CLI package will be documented in this file.

## [1.1.0] - 2024-12-01

### Changed
- **BREAKING**: Import namespace changed from `llmhub` to `llmhub_cli`
- **BREAKING**: Package directory moved from `packages/llmhub/` to `packages/cli/`
- **BREAKING**: Generator reorganized from SP1-SP10 flat structure to functional grouping:
  - `sp1_spec_schema` → `generator.spec`
  - `sp2_needs_interpreter` + `sp3_needs_schema` → `generator.needs`
  - `sp4_catalog_view` → `generator.catalog_view`
  - `sp5-sp9` → `generator.selection`
  - `sp10_machine_config_emitter` → `generator.emitter`
- **BREAKING**: Command modules renamed (dropped `_cmd` suffix):
  - `setup_cmd.py` → `setup.py`
  - `spec_cmd.py` → `spec.py`
  - `runtime_cmd.py` → `runtime.py`
  - `env_cmd.py` → `env.py`
  - `catalog_cmd.py` → `catalog.py`
  - `test_cmd.py` → `test.py`
- **BREAKING**: Catalog sources reorganized into `catalog/sources/` subdirectory
- Dependency updated: `llmhub-runtime` → `rethink-llmhub-runtime`

### Migration Guide

#### For Users (CLI usage - NO CHANGES)
The `llmhub` command remains the same:
```bash
llmhub init
llmhub generate
llmhub catalog show
# ... all commands work as before
```

#### For Developers (Import changes required)
If you were importing from `llmhub` package:

**Old imports:**
```python
from llmhub.catalog import builder
from llmhub.commands import setup_cmd
from llmhub.generator.sp1_spec_schema import parser
from llmhub.generator.sp5_filter_candidates import filter_candidates
```

**New imports:**
```python
from llmhub_cli.catalog import builder
from llmhub_cli.commands import setup
from llmhub_cli.generator.spec import parser
from llmhub_cli.generator.selection import filter_candidates
```

#### Generator Module Path Changes
- `sp1_spec_schema` → `spec`
- `sp2_needs_interpreter.interpreter` → `needs.interpreter`
- `sp3_needs_schema.parser` → `needs.schema`
- `sp4_catalog_view.loader` → `catalog_view.loader`
- `sp5_filter_candidates.filter` → `selection.filter`
- `sp6_weights.calculator` → `selection.weights`
- `sp7_scoring_engine.scorer` → `selection.scorer`
- `sp8_relaxation_engine.relaxer` → `selection.relaxer`
- `sp9_selector_orchestrator.orchestrator` → `selection.selector`
- `sp10_machine_config_emitter.builder` → `emitter.builder`

## [1.0.3] - Previous Release
- Catalog system implementation
- Generator pipeline
- CLI commands
