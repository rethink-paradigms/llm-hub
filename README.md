# Resource Orchestrator

Central service to resolve logical roles (e.g. `llm.preprocess`, `store.vector.facts`) into concrete model/storage configs per project + environment.

## Setup

1.  **Install Dependencies**:
    ```bash
    pip install pyyaml pydantic
    ```

2.  **Environment Variables**:
    You must set API keys for the auth profiles defined in `config/providers.yaml`.
    
    ```bash
    export RO_AUTH_OPENAI_DEFAULT_API_KEY="sk-..."
    export RO_AUTH_GEMINI_DEFAULT_API_KEY="AIza..."
    export RO_AUTH_ANTHROPIC_DEFAULT_API_KEY="sk-ant-..."
    ```

## Usage

### CLI

**Resolve LLM Role**:
```bash
python3 -m src.sp8_cli.cli resolve-llm --project memory --env dev --role llm.preprocess
```

**Resolve Storage Role**:
```bash
python3 -m src.sp8_cli.cli resolve-store --project memory --env dev --role store.vector.facts
```

**Export Config**:
```bash
python3 -m src.sp8_cli.cli export-config --project memory --env dev --format env
```

## Adding Providers

1.  Add entry to `config/providers.yaml`.
2.  Implement adapter in `src/sp3_model_catalog/adapters.py` (if new type).
3.  Set `RO_AUTH_<PROFILE>_API_KEY`.
