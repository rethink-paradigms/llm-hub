# PLAN-cli-core.md — LLMHub CLI (Core, No Web)

## 0. Context & Goals

This plan defines the **LLMHub CLI core**: a project-local command-line tool that manages a human-friendly LLM spec (`llmhub.spec.yaml`), converts it into a machine runtime config (`llmhub.yaml`), and helps manage environment variables and basic tests.

The focus of this plan:

- CLI UX and behaviour inside a **single project directory**.
- File-level operations and structure:
  - `llmhub.spec.yaml`  (human / agent spec)
  - `llmhub.yaml`       (machine runtime, consumed by `llmhub_runtime`)
  - `.env.example`      (environment key hints).
- A clean, modular internal architecture:
  - Context resolver
  - Spec IO & model
  - Runtime IO & integration with `llmhub_runtime`
  - Env manager
  - UX helpers
  - Commands layer
  - Generator integration hook (as a black box).

**Out of scope for this plan:**

- Web UI (HTTP server, browser UI).
- Multi-project registry (`~/.config/llmhub/`).
- The internal logic of the spec → runtime generator (model selection engine).

The goal is that once this plan is implemented:

- Running `llmhub` in a project gives a clear, helpful CLI.
- You can initialize a spec, edit roles, generate runtime, sync `.env.example`, and test LLM calls.
- The spec → runtime conversion is wired via a clear integration interface so we can later plug in a sophisticated generator without changing CLI structure.

---

## 1. Tech Stack & Dependencies

### Language & runtime

- Python ≥ 3.10

### Core libraries

- `typer` (or `click`) — for CLI command routing.  
  - Assume `typer` for this plan (nice DX + async support if needed).
- `PyYAML` — for reading/writing YAML.
- `pydantic` (v2 preferred) — for spec and runtime schemas, validation.
- `llmhub_runtime` — dependency; used for `test` and `doctor`.
- `any-llm` — **only** used by the generator hook (which is abstract in this plan). This plan assumes the CLI *can* depend on `any-llm`, but generator internals are defined elsewhere.

### Optional (but recommended)

- `rich` — for nicer tables and colored output (UX helpers).
- `python-dotenv` — for loading `.env` files in `env check` / `test`, if desired.
- `pytest` — for tests.
- `mypy` & `ruff` — for static checking / linting (optional, but sensible).

---

## 2. Package & Repo Layout (CLI Package Only)

This plan targets a **second package** alongside `llmhub_runtime`, e.g.:

```text
packages/
  llmhub_runtime/
    ... (already implemented) ...

  llmhub/
    pyproject.toml
    setup.cfg
    README.md
    src/
      llmhub/
        __init__.py
        cli.py              # Typer app entry
        context.py          # SP1: project context resolver
        spec_models.py      # SP2: spec schema + IO
        runtime_io.py       # SP3: runtime IO (or reuse runtime models)
        env_manager.py      # SP4: .env.example + env checking
        ux.py               # SP5: printing & interactive prompts
        commands/
          __init__.py
          setup_cmd.py      # setup, init, status
          spec_cmd.py       # roles, add-role, edit-role, rm-role, spec show/validate
          runtime_cmd.py    # generate, runtime show, diff
          env_cmd.py        # env sync, env check
          test_cmd.py       # test, doctor
        generator_hook.py   # SP7: abstraction over spec -> runtime
    tests/
      test_context.py
      test_spec_models.py
      test_env_manager.py
      test_cli_smoke.py

PyPI entry point:

In packages/llmhub/pyproject.toml:

[project.scripts]
llmhub = "llmhub.cli:app"

Where app is a typer.Typer() instance.

⸻

3. File Types & Schemas

3.1 Human spec: llmhub.spec.yaml

Goal: simple, structured file that humans/agents can write. It describes:
	•	Project context.
	•	Providers (which vendors are allowed, and env variables).
	•	Roles (logical LLM roles + preferences).

Example:

project: memory
env: dev

providers:
  openai:
    enabled: true
    env_key: OPENAI_API_KEY
  anthropic:
    enabled: true
    env_key: ANTHROPIC_API_KEY

roles:
  llm.preprocess:
    kind: chat
    description: >
      Fast, cheap preprocessing model to normalize user input, rewrite questions, etc.
    preferences:
      latency: low     # low | medium | high
      cost: low        # low | medium | high
      quality: medium  # low | medium | high
      providers: [openai, anthropic]

  llm.inference:
    kind: chat
    description: >
      Main reasoning model for final answers.
    preferences:
      latency: medium
      cost: medium
      quality: high
      providers: [anthropic, openai]

  llm.embedding:
    kind: embedding
    description: >
      Vector embeddings for memory retrieval.
    preferences:
      cost: low
      quality: medium
      providers: [openai]

defaults:
  providers:
    - openai

Key points:
	•	project, env — metadata (informational, used in logs and env examples).
	•	providers — each provider id may have:
	•	enabled: bool — whether this provider is considered.
	•	env_key: str — environment variable name for the API key.
	•	(v1+) additional fields like base_url, notes.
	•	roles — map role name → role spec:
	•	kind: enum "chat" | "embedding" | "image" | "audio" | "tool" | "other".
	•	description: free text, used by generator for intent.
	•	preferences:
	•	latency: "low" | "medium" | "high" (optional).
	•	cost:    "low" | "medium" | "high" (optional).
	•	quality: "low" | "medium" | "high" (optional).
	•	providers: list of provider ids; if absent, fall back to global defaults.
	•	Optional overrides:
	•	force_provider: str   — if set, generator must use only this provider.
	•	force_model: str      — if set, generator must use exactly this model (validated).
	•	mode_params: dict     — free-form JSON settings that should be copied into runtime params.
	•	defaults.providers — global default providers if a role does not specify.

This schema is implemented as SpecConfig in spec_models.py.

3.2 Machine runtime: llmhub.yaml

Machine-readable config, already defined by llmhub_runtime. Example:

project: memory
env: dev

providers:
  openai:
    env_key: OPENAI_API_KEY
  anthropic:
    env_key: ANTHROPIC_API_KEY

roles:
  llm.preprocess:
    provider: openai
    model: gpt-4o-mini
    mode: chat
    params:
      temperature: 0.2
      max_tokens: 256

  llm.inference:
    provider: anthropic
    model: claude-3-5-sonnet-20241022
    mode: chat
    params:
      temperature: 0.7
      max_tokens: 2048

  llm.embedding:
    provider: openai
    model: text-embedding-3-small
    mode: embedding
    params: {}

	•	CLI will treat this as opaque for most operations (except printing & simple diff).
	•	Exact schema is in llmhub_runtime.models.RuntimeConfig; CLI should reuse or mirror this.

3.3 Environment example: .env.example

Generated from the spec’s providers block:

# LLMHub generated .env.example for project: memory (env: dev)

# OpenAI API key
OPENAI_API_KEY=

# Anthropic API key
ANTHROPIC_API_KEY=

	•	CLI never writes .env directly, only .env.example.
	•	Optional CLI flag to also generate .env.local for quick dev.

⸻

4. High-Level Behaviour: Commands & Flows

At a high level, the CLI should support:
	•	First-time setup:
	•	llmhub setup — interactive spec creation + env hints.
	•	llmhub init  — non-interactive minimal spec creation.
	•	Spec lifecycle:
	•	llmhub spec show       — pretty-print spec roles & providers.
	•	llmhub spec validate   — schema validation.
	•	llmhub roles           — list roles.
	•	llmhub add-role NAME   — add role interactively.
	•	llmhub edit-role NAME  — interactive edit.
	•	llmhub rm-role NAME    — remove role.
	•	Runtime lifecycle:
	•	llmhub generate        — spec → runtime (calls generator hook).
	•	llmhub runtime show    — pretty-print runtime.
	•	llmhub diff            — high-level diff spec vs runtime roles.
	•	Environment management:
	•	llmhub env sync        — sync .env.example from spec.
	•	llmhub env check       — check for missing env vars.
	•	Testing & health:
	•	llmhub test            — run a test call using a role.
	•	llmhub doctor          — composite validation + env + test.
	•	General:
	•	llmhub status          — summary status.
	•	llmhub path            — show resolved paths.

CLI UX rules:
	•	Running llmhub with no subcommand should:
	•	Resolve project context.
	•	Print a friendly status.
	•	Suggest common next commands (setup, generate, test).

⸻

5. Subproblem Spec Sheets (Modules)

SP1 — Project Context Resolver (context.py)

Goal: Resolve where we are and which files to operate on.

Inputs
	•	cwd or user-given path (string / Path).
	•	Optional overrides from CLI flags:
	•	--root
	•	--spec-path
	•	--runtime-path
	•	--env-example-path

Outputs
	•	ProjectContext object:
	•	root: Path                  — project root dir.
	•	spec_path: Path             — path to llmhub.spec.yaml (non-existing allowed).
	•	runtime_path: Path          — path to llmhub.yaml (non-existing allowed).
	•	env_example_path: Path      — path to .env.example (non-existing allowed).

Description
	•	Walk upwards from start path to detect project root:
	•	Priority: directory containing llmhub.spec.yaml, else .git, else pyproject.toml (configurable).
	•	If user passes --root, treat that as root.
	•	Derive default spec/runtime/env-example paths from root, unless overridden.

Interfaces
	•	class ProjectContext(BaseModel):
	•	Fields as above.
	•	def resolve_context(start: Path | None = None, overrides: Optional[ContextOverrides] = None) -> ProjectContext:
	•	ContextOverrides may contain explicit paths.

Notes
	•	Provide clear errors when project root cannot be resolved.
	•	All CLI commands should call this first to avoid scattering path logic.

⸻

SP2 — Spec Model & IO (spec_models.py)

Goal: Define SpecConfig and helpers to load/save llmhub.spec.yaml.

Inputs
	•	YAML data from file (llmhub.spec.yaml).
	•	Programmatic spec modifications (from commands).

Outputs
	•	Validated SpecConfig object.
	•	Updated spec file on disk.

Description
	•	Pydantic models representing:
	•	SpecProviderConfig
	•	Preferences
	•	RoleSpec
	•	SpecConfig
	•	Enforce schema but allow forward-compatible extension (ignore extra fields).

Interfaces
	•	Models:

class PreferenceLevel(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"

class RoleKind(str, Enum):
    chat = "chat"
    embedding = "embedding"
    image = "image"
    audio = "audio"
    tool = "tool"
    other = "other"

class SpecProviderConfig(BaseModel):
    enabled: bool = True
    env_key: Optional[str] = None
    # future: base_url, notes, etc.

class Preferences(BaseModel):
    latency: Optional[PreferenceLevel] = None
    cost: Optional[PreferenceLevel] = None
    quality: Optional[PreferenceLevel] = None
    providers: Optional[list[str]] = None

class RoleSpec(BaseModel):
    kind: RoleKind
    description: str
    preferences: Preferences = Preferences()
    force_provider: Optional[str] = None
    force_model: Optional[str] = None
    mode_params: dict[str, Any] = Field(default_factory=dict)

class SpecDefaults(BaseModel):
    providers: list[str] = Field(default_factory=list)

class SpecConfig(BaseModel):
    project: str
    env: str
    providers: dict[str, SpecProviderConfig]
    roles: dict[str, RoleSpec]
    defaults: Optional[SpecDefaults] = None


	•	IO helpers:

def load_spec(path: Path) -> SpecConfig:
    # parse YAML, validate, raise SpecError on failure

def save_spec(path: Path, spec: SpecConfig) -> None:
    # write pretty YAML (preserving key order where possible)


	•	Error class:

class SpecError(Exception):
    ...



Notes
	•	YAML writer: prefer stable ordering (project, env, providers, roles, defaults).
	•	For v0, we can ignore preserving comments.

⸻

SP3 — Runtime IO (runtime_io.py)

Goal: Encapsulate loading/saving llmhub.yaml and bridging to llmhub_runtime.

Inputs
	•	Runtime YAML (llmhub.yaml).
	•	RuntimeConfig type from llmhub_runtime (or a local mirror).

Outputs
	•	RuntimeConfig object.
	•	Updated runtime file on disk.

Description
	•	Provide a minimal API:
	•	to load runtime for printing/diff/test;
	•	to save runtime generated by the generator hook.

Interfaces
	•	If reusing llmhub_runtime models:

from llmhub_runtime.models import RuntimeConfig

class RuntimeError(Exception):
    ...

def load_runtime(path: Path) -> RuntimeConfig:
    # raise RuntimeError if file missing or invalid

def save_runtime(path: Path, runtime: RuntimeConfig) -> None:
    # write YAML in stable format


	•	For projects without llmhub.yaml yet, commands should handle “file not found” gracefully.

⸻

SP4 — Env Manager (env_manager.py)

Goal: Generate .env.example and check environment variables required by providers in the spec/runtime.

Inputs
	•	SpecConfig (providers + env_key).
	•	Optional .env file path (for checks).
	•	OS environment variables.

Outputs
	•	.env.example file on disk.
	•	List of missing env keys for reporting.

Description
	•	.env.example generator:
	•	For each provider in spec.providers:
	•	If env_key is set, include commented description and blank value.
	•	Env checker:
	•	Determine required keys (from spec or runtime).
	•	Check os.environ.
	•	Optionally, load .env using python-dotenv before checking.

Interfaces

class MissingEnvVar(BaseModel):
    provider: str
    env_key: str

def generate_env_example(spec: SpecConfig, path: Path, overwrite: bool = True) -> None:
    ...

def check_env(spec: SpecConfig, load_dotenv_path: Optional[Path] = None) -> list[MissingEnvVar]:
    ...

Notes
	•	overwrite=True is acceptable for .env.example, but should be clear in CLI output.
	•	CLI should never modify actual .env unless explicitly requested in future versions.

⸻

SP5 — UX Helpers (ux.py)

Goal: Provide reusable functions for nice output and simple interactive prompts.

Inputs
	•	Data structures to display (roles, providers, diff results, etc.).
	•	User input via stdin.

Outputs
	•	Pretty-printed tables & messages.
	•	User selections (strings/booleans).

Description
Abstractions:
	•	Output helpers:
	•	print_status(context, spec_exists, runtime_exists, env_example_exists, issues)
	•	print_roles_table(roles: dict[str, RoleSpec])
	•	print_runtime_roles(runtime_roles)
	•	print_env_check_results(missing_env_vars).
	•	Input helpers:
	•	confirm(prompt: str, default: bool = True) -> bool
	•	select_from_list(prompt: str, options: list[str]) -> str
	•	multi_select_from_list(prompt: str, options: list[str]) -> list[str]
	•	Simple editing prompts for role fields.

Implementation can start with:
	•	typer.echo, input() for interactive mode.
	•	Optionally rich.table / rich.prompt for nicer UX.

Interfaces (examples)

def print_roles_table(spec: SpecConfig) -> None: ...
def print_runtime_roles(runtime: RuntimeConfig) -> None: ...
def print_env_check_results(missing: list[MissingEnvVar]) -> None: ...
def confirm(prompt: str, default: bool = True) -> bool: ...

Notes
	•	Keep this module independent of business logic.
	•	Avoid heavy TUI frameworks in v0.

⸻

SP6 — Commands Layer (commands/*.py)

Goal: Implement CLI commands by orchestrating SP1–SP5 and SP7.

Each subfile will define one or more functions that are wired to Typer.

SP6.1 — Setup & Status (setup_cmd.py)
Commands:
	•	llmhub setup
	•	llmhub init
	•	llmhub status
	•	llmhub path

llmhub setup
	•	Flow:
	1.	Resolve context.
	2.	If spec exists: ask if user wants to reuse or re-init.
	3.	Interactive Q&A:
	•	Ask for project name & env (defaults from folder name, “dev”).
	•	Ask which providers to enable (list a predefined set: openai, anthropic, gemini, mistral, etc.).
	•	Ask which standard roles to scaffold (preprocess / inference / embedding / tools / image).
	•	Ask basic preferences per role (cost/latency/quality).
	4.	Build a SpecConfig object in memory.
	5.	Save spec via save_spec.
	6.	Call generate_env_example to create .env.example.
	7.	Print summary + next steps.

llmhub init
	•	Non-interactive:
	•	Create minimal default SpecConfig:
	•	project = basename(root)
	•	env = dev
	•	providers = only openai enabled with env_key=OPENAI_API_KEY.
	•	roles = llm.inference only, with generic description.
	•	Save spec.
	•	Generate .env.example.
	•	Not prompt user.

llmhub status
	•	Show:
	•	resolved paths,
	•	whether files exist,
	•	spec validity,
	•	runtime validity (if exists),
	•	count of roles & providers.

llmhub path
	•	Print resolved paths in a compact format (JSON or human-readable).

SP6.2 — Spec Commands (spec_cmd.py)
Commands:
	•	llmhub spec show
	•	llmhub spec validate
	•	llmhub roles
	•	llmhub add-role NAME
	•	llmhub edit-role NAME
	•	llmhub rm-role NAME

Behaviours:
	•	All commands:
	•	Resolve context.
	•	Load spec (error if missing, prompt to run setup).

spec show
	•	Pretty-print entire spec (providers + roles) using ux.print_roles_table and provider summary.

spec validate
	•	load_spec and catch validation errors:
	•	Print [OK] or detailed errors.

roles
	•	List only roles: name, kind, main preferences, provider hints.

add-role NAME
	•	Load spec.
	•	If role already exists, warn and exit or offer to edit instead.
	•	Prompt:
	•	kind (chat/embedding/…).
	•	description (short).
	•	providers (choose from spec.providers where enabled).
	•	preferences (cost/latency/quality).
	•	Append to spec.roles and save_spec.

edit-role NAME
	•	Load spec.
	•	If role missing, error.
	•	Show current config.
	•	Interactive step-by-step toggle/edit fields.
	•	Save changes.

rm-role NAME
	•	Confirm and remove role from spec.
	•	Save spec.

SP6.3 — Runtime Commands (runtime_cmd.py)
Commands:
	•	llmhub generate
	•	llmhub runtime show
	•	llmhub diff

generate
	•	Resolve context.
	•	Load spec.
	•	Call generator_hook.generate_runtime(spec, options).
	•	Save runtime to llmhub.yaml.
	•	Optionally update .env.example again (if providers changed).
	•	Flags:
	•	--dry-run → print proposed runtime (human-readable or YAML) without writing.
	•	--no-llm → passes option down to generator to use heuristic-only mode.
	•	--force → overwrite existing runtime without confirm.

runtime show
	•	Resolve context.
	•	Load runtime.
	•	Pretty-print providers and roles via ux.

diff
	•	Resolve context.
	•	Load spec and runtime (if exists).
	•	Compare:
	•	roles in spec but not in runtime.
	•	roles in runtime but not in spec.
	•	Print a small diff view.

SP6.4 — Env Commands (env_cmd.py)
Commands:
	•	llmhub env sync
	•	llmhub env check

env sync
	•	Resolve context.
	•	Load spec.
	•	Call generate_env_example.
	•	Optionally accept --dry-run to print what would be written.

env check
	•	Resolve context.
	•	Load spec.
	•	Optionally load .env from project root.
	•	Call check_env.
	•	Print missing keys via ux.print_env_check_results.
	•	Exit with non-zero code if any missing keys (good for CI).

SP6.5 — Test & Doctor (test_cmd.py)
Commands:
	•	llmhub test
	•	llmhub doctor

test
	•	Flags:
	•	--role ROLE (optional).
	•	--prompt PROMPT (optional).
	•	--env-file PATH (optional).
	•	--json (optional).
	•	Flow:
	•	Resolve context.
	•	Load runtime.
	•	Determine role:
	•	if --role given, use that.
	•	else, show list of roles, let user select.
	•	Determine prompt:
	•	if --prompt given, use that.
	•	else, ask interactively.
	•	Optional: load .env before calling.
	•	Instantiate LLMHub(config_path=runtime_path).
	•	Call hub.completion(...) or appropriate method based on role mode.
	•	Print:
	•	selected provider/model.
	•	response content (trimmed).
	•	duration.
	•	If --json, print raw response JSON.

doctor
	•	Composite health check:
	•	spec validate.
	•	env check.
	•	Attempt a minimal test call (if at least one chat role exists):
	•	choose the first chat role in runtime or one flagged as “testable” in a later version.
	•	Summarize status:
	•	[OK] All checks passed.
	•	or list which checks failed.
	•	Flags:
	•	--no-network — run only local validations, skip test call.

⸻

SP7 — Generator Integration Hook (generator_hook.py)

Goal: Provide a stable interface between CLI and the spec → runtime generator engine, without specifying its internal logic here.

Inputs
	•	SpecConfig object.
	•	Optional options:
	•	no_llm: bool (force heuristic-only mode).
	•	explain: bool (return reasons for choices).

Outputs
	•	RuntimeConfig object (same schema as llmhub_runtime.models.RuntimeConfig).
	•	Optional selection metadata for explain (e.g., reason strings per role).

Description
	•	The CLI will treat generator as a pure function from spec to runtime.
	•	Internally, it may use:
	•	any-llm to fetch model catalogs.
	•	LLMs to refine ranking.
	•	Static metadata about models.
	•	All that logic is out of scope here.

Interfaces

from typing import Optional
from llmhub_runtime.models import RuntimeConfig
from .spec_models import SpecConfig

class GeneratorOptions(BaseModel):
    no_llm: bool = False
    explain: bool = False

class GenerationResult(BaseModel):
    runtime: RuntimeConfig
    explanations: dict[str, str] = Field(default_factory=dict)  # role -> reason

def generate_runtime(spec: SpecConfig, options: Optional[GeneratorOptions] = None) -> GenerationResult:
    ...

For v0 implementation (just to wire CLI), this function can:
	•	Map roles to hardcoded dummy models (e.g. always use openai:gpt-4o-mini) so CLI features can be tested.
	•	Later replaced with production generator.

⸻

6. CLI Entry (cli.py)

Goal: Wire all commands with Typer and provide a good top-level UX.

Skeleton:

import typer
from .commands import setup_cmd, spec_cmd, runtime_cmd, env_cmd, test_cmd

app = typer.Typer(help="LLMHub CLI — manage LLM specs and runtime configs")

# Grouped commands
app.command()(setup_cmd.setup)
app.command()(setup_cmd.init)
app.command()(setup_cmd.status)
app.command()(setup_cmd.path)

spec_app = typer.Typer(help="Spec management commands")
spec_app.command(name="show")(spec_cmd.spec_show)
spec_app.command(name="validate")(spec_cmd.spec_validate)
spec_app.command(name="roles")(spec_cmd.roles)
spec_app.command(name="add-role")(spec_cmd.add_role)
spec_app.command(name="edit-role")(spec_cmd.edit_role)
spec_app.command(name="rm-role")(spec_cmd.rm_role)
app.add_typer(spec_app, name="spec")

runtime_app = typer.Typer(help="Runtime management commands")
runtime_app.command(name="generate")(runtime_cmd.generate)
runtime_app.command(name="show")(runtime_cmd.runtime_show)
runtime_app.command(name="diff")(runtime_cmd.diff)
app.add_typer(runtime_app, name="runtime")

env_app = typer.Typer(help="Env management commands")
env_app.command(name="sync")(env_cmd.env_sync)
env_app.command(name="check")(env_cmd.env_check)
app.add_typer(env_app, name="env")

test_app = typer.Typer(help="Testing & diagnostics")
test_app.command(name="test")(test_cmd.test)
test_app.command(name="doctor")(test_cmd.doctor)
app.add_typer(test_app, name="check")

# Default behaviour: no command
@app.callback(invoke_without_command=True)
def main(ctx: typer.Context):
    if ctx.invoked_subcommand is None:
        # print summary status via setup_cmd.status-like helper
        setup_cmd.print_status_summary()
        typer.echo("\nCommon next commands:")
        typer.echo("  llmhub setup       # first-time setup")
        typer.echo("  llmhub spec show   # view current spec")
        typer.echo("  llmhub generate    # generate llmhub.yaml")
        typer.echo("  llmhub check test  # test a role")


⸻

7. Implementation Order

Recommended order for Antigravity / IDE execution:
	1.	SP1 — context.py with tests.
	2.	SP2 — spec_models.py + load/save helpers with tests.
	3.	SP4 — env_manager.py + tests.
	4.	SP5 — ux.py basic helpers.
	5.	SP3 — runtime_io.py (simple I/O) with tests.
	6.	SP7 — generator_hook.py with stub implementation (dummy mappings).
	7.	SP6 — Commands modules in this order:
	•	setup_cmd.py (setup, init, status, path),
	•	spec_cmd.py (spec show/validate, roles, add/edit/rm),
	•	env_cmd.py (env sync/check),
	•	runtime_cmd.py (generate, runtime show, diff),
	•	test_cmd.py (test, doctor).
	8.	CLI wiring — cli.py with Typer.
	9.	Top-level tests — test_cli_smoke.py:
	•	python -m llmhub runs and prints a helpful summary.
	•	llmhub init, llmhub generate, llmhub env sync etc. are smoke-tested.

⸻

8. README Outline for the CLI Package

The packages/llmhub/README.md should include:
	•	What LLMHub CLI is.
	•	Relationship to llmhub_runtime.
	•	Quickstart:

pip install llmhub llmhub-runtime any-llm
cd my-project
llmhub setup       # or: llmhub init
llmhub generate
llmhub check test --role llm.inference --prompt "Hello"


	•	Explanation of llmhub.spec.yaml vs llmhub.yaml vs .env.example.
	•	Role-first philosophy.
	•	Short architecture overview:
	•	Context, Spec, Runtime, Env, Generator Hook.

This README is separate from this plan, but should reflect the same structure.

⸻

This plan defines the entire CLI core architecture and behaviour, with the generator logic abstracted behind generator_hook.generate_runtime. All components are decoupled and can be implemented and tested independently without conflict.

