# Changelog - rethink-llmhub-runtime

All notable changes to the runtime package will be documented in this file.

## [1.0.3] - 2024-12-01

### Changed
- **BREAKING**: Package renamed from `llmhub-runtime` to `rethink-llmhub-runtime`
- **BREAKING**: Package directory moved from `packages/llmhub_runtime/` to `packages/runtime/`
- Import namespace remains `llmhub_runtime` (no code changes required)

### Migration Guide
If you were using:
```bash
pip install llmhub-runtime
```

Now use:
```bash
pip install rethink-llmhub-runtime
```

**No code changes required** - all imports remain `from llmhub_runtime import ...`

## [1.0.2] - Previous Release
- Initial stable release
- Core runtime functionality
- LLM Hub execution engine
