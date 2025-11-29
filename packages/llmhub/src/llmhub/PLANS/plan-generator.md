# PLAN-generator-v1.md

Generator = bridge from **human spec** → **canonical role needs** → **model selection** → **machine config** for LLM Hub Runtime.

The generator lives in its own top-level module, with tight subproblem boundaries and a spec sheet in every folder.

---

## 1. Responsibilities (end-to-end)

Given a project:

1. Read a **human spec YAML** (written by user/agent).
2. Parse/validate it into a **canonical spec model** (no LLM yet).
3. Use an **interpreter LLM** (via LLM Hub Runtime) with structured JSON output to turn canonical spec → list of **RoleNeed** objects.
4. Load the **catalog snapshot** (built elsewhere) as a list of **CanonicalModel** objects.
5. For each role:
   - Filter candidates (hard constraints).
   - Score & rank models using catalog metrics and role preferences.
   - Apply controlled relaxation if no candidates match.
   - Emit primary model + optional backups + rationale.
6. Assemble everything into a **MachineConfig** (the machine-readable `llm-hub.yaml` format).
7. Expose a library API used by CLI (and later UI) to run this whole pipeline.

No network calls or scraping live data inside the generator. All external calls go through LLM Hub Runtime and Catalog.

---

## 2. Project Structure (generator module)

All generator-specific logic is under `src/generator/`. Tests live under `tests/generator/`.

Top-level:

- `src/generator/__init__.py`
- `src/generator/spec.md`  
  High-level spec for the whole generator (inputs, outputs, flow, non-goals).
- `src/generator/README.md`  
  Human-readable overview and quickstart for using the generator module.

Subfolders (each with its own `spec.md`):

- `src/generator/sp1_spec_schema/`
- `src/generator/sp2_needs_interpreter/`
- `src/generator/sp3_needs_schema/`
- `src/generator/sp4_catalog_view/`
- `src/generator/sp5_filter_candidates/`
- `src/generator/sp6_weights/`
- `src/generator/sp7_scoring_engine/`
- `src/generator/sp8_relaxation_engine/`
- `src/generator/sp9_selector_orchestrator/`
- `src/generator/sp10_machine_config_emitter/`

Tests:

- `tests/generator/test_sp1_spec_schema.py`
- `tests/generator/test_sp2_needs_interpreter.py`
- …
- `tests/generator/test_sp10_machine_config_emitter.py`
- `tests/generator/test_generate_e2e.py` (full pipeline)

---

## 3. Spec Sheet Template (per folder)

Every `src/generator/spX_*/spec.md` must follow this minimal template:

- Name: `SPX – <short title>`
- Purpose: 2–3 lines; what this subproblem is responsible for.
- Inputs:
  - Types and shape (Pydantic models / dataclasses / plain dicts).
- Outputs:
  - Types and shape.
- Public Interfaces:
  - Function signatures (Python-style) this folder exposes.
- Invariants / Constraints:
  - Things that must always hold (e.g. “no network calls”, “pure function”).
- Non-goals:
  - What this subproblem deliberately does not do.

This keeps the generator architecture explicit and easy to evolve.

---

## 4. Subproblems (SP1–SP10)

### SP1 – Spec Schema (human spec → typed model)

Folder: `src/generator/sp1_spec_schema/`

- Purpose: Define and validate the **human spec YAML** structure.
- Inputs:
  - Raw YAML/dict loaded from user’s spec file.
- Outputs:
  - `ProjectSpec` model (Pydantic), including:
    - project metadata (name, env, etc.).
    - list of roles with natural-language descriptions and preferences.
- Public Interfaces:
  - `parse_project_spec(raw: dict) -> ProjectSpec`
- Rules:
  - No LLM usage.
  - Provide defaults where possible; fail with clear errors on invalid shape.

---

### SP2 – Needs Interpreter (ProjectSpec → RoleNeed[] via LLM)

Folder: `src/generator/sp2_needs_interpreter/`

- Purpose: Convert **ProjectSpec** into canonical **RoleNeed** objects using an LLM with structured output.
- Inputs:
  - `ProjectSpec` from SP1.
  - A `Hub` instance (LLM Hub Runtime) or injectable `llm_call` function.
- Outputs:
  - `List[RoleNeed]` (raw JSON from LLM parsed into typed models).
- Public Interfaces:
  - `interpret_needs(spec: ProjectSpec, hub: Hub, model_role: str) -> list[RoleNeed]`
- Rules:
  - Exactly one LLM call per project (or per environment) with structured JSON output.
  - The JSON schema returned must match the `RoleNeed` model defined in SP3.
  - No catalog access here; only interpretation of human spec.

---

### SP3 – Needs Schema (RoleNeed model)

Folder: `src/generator/sp3_needs_schema/`

- Purpose: Define canonical **RoleNeed** model used by selector.
- Inputs:
  - Raw dicts from SP2 (LLM output).
- Outputs:
  - `List[RoleNeed]` Pydantic models.
- Public Interfaces:
  - `parse_role_needs(raw: list[dict]) -> list[RoleNeed]`
  - `RoleNeed` class with fields:
    - id, task_kind, importance, quality_bias, cost_bias,
      latency_sensitivity, reasoning_required, tools_required,
      structured_output_required, context_min, modalities_in/out,
      provider_allowlist/blocklist, model_denylist,
      reasoning_tier_pref, creative_tier_pref, notes.
- Rules:
  - Must be forward-compatible: adding new fields in future must not break existing code.

---

### SP4 – Catalog View (catalog snapshot → CanonicalModel list)

Folder: `src/generator/sp4_catalog_view/`

- Purpose: Adapt the catalog module’s snapshot into **CanonicalModel** objects for the selector.
- Inputs:
  - Catalog API: e.g. `llmhub.catalog.load_snapshot()` or equivalent.
- Outputs:
  - `List[CanonicalModel]` Pydantic models.
- Public Interfaces:
  - `load_catalog_view() -> list[CanonicalModel]`
  - `CanonicalModel` class with fields:
    - model_id, provider, family,
      quality_tier, reasoning_tier, creative_tier,
      cost_per_million, cost_tier,
      context_tokens,
      supports_reasoning, supports_tool_call, supports_structured_output,
      modalities_in/out,
      open_weights,
      knowledge_cutoff, release_date, last_updated,
      arena_score.
- Rules:
  - No HTTP calls; only uses existing catalog module.
  - Any missing fields must be defaulted safely.

---

### SP5 – Filter Candidates (hard constraints)

Folder: `src/generator/sp5_filter_candidates/`

- Purpose: Apply hard constraints from a `RoleNeed` to the catalog.
- Inputs:
  - `RoleNeed`, `List[CanonicalModel]`.
- Outputs:
  - Filtered `List[CanonicalModel]` (candidates).
- Public Interfaces:
  - `filter_candidates(role: RoleNeed, models: list[CanonicalModel]) -> list[CanonicalModel]`
- Rules:
  - Apply:
    - provider allowlist/blocklist,
    - model denylist,
    - modalities,
    - reasoning/tools/structured_output flags,
    - context_min.
  - No scoring or relaxation here; pure filter.

---

### SP6 – Weights (derive scoring weights from RoleNeed)

Folder: `src/generator/sp6_weights/`

- Purpose: Turn role preferences into numeric weights for scoring.
- Inputs:
  - `RoleNeed`.
- Outputs:
  - `Weights` model: w_quality, w_cost, w_reasoning, w_creative, w_context, w_freshness.
- Public Interfaces:
  - `derive_weights(role: RoleNeed) -> Weights`
- Rules:
  - Weights in [0,1], sum to 1.
  - Must consider:
    - task_kind, quality_bias, cost_bias,
      latency_sensitivity, importance,
      reasoning_required, reasoning_tier_pref, creative_tier_pref.

---

### SP7 – Scoring Engine (candidates → ranked list)

Folder: `src/generator/sp7_scoring_engine/`

- Purpose: Compute a final score per candidate and sort them.
- Inputs:
  - `RoleNeed`, `Weights`, `List[CanonicalModel]`.
- Outputs:
  - List of `(CanonicalModel, float score)` sorted desc.
- Public Interfaces:
  - `score_candidates(role: RoleNeed, weights: Weights, models: list[CanonicalModel]) -> list[tuple[CanonicalModel, float]]`
- Rules:
  - Normalize:
    - quality_score: mix of quality_tier + arena_score.
    - reasoning_score: based on reasoning_tier.
    - creative_score: based on creative_tier.
    - cost_score: inverse of cost_per_million / cost_tier.
    - context_score: context_tokens vs role.context_min.
    - freshness_score: last_updated / release_date.
  - Final score:
    - score = w_quality*quality_score + w_reasoning*reasoning_score +
      w_creative*creative_score + w_context*context_score +
      w_freshness*freshness_score + w_cost*cost_score.
  - Tie-break:
    - provider in allowlist,
    - higher arena_score,
    - higher context_tokens,
    - lexicographic model_id.

---

### SP8 – Relaxation Engine (when filter returns zero)

Folder: `src/generator/sp8_relaxation_engine/`

- Purpose: Systematically relax constraints when no candidates pass filters.
- Inputs:
  - `RoleNeed`, `List[CanonicalModel]`, references to SP5 and SP7.
- Outputs:
  - `(ranked_candidates: list[(CanonicalModel, float)], relaxations: list[str])`
- Public Interfaces:
  - `relax_and_select(role: RoleNeed, models: list[CanonicalModel], weights: Weights) -> tuple[list[tuple[CanonicalModel, float]], list[str]]`
- Rules:
  - Relaxation steps in order (configurable but deterministic):
    - remove provider_allowlist (keep blocklist),
    - lower context_min,
    - turn structured_output_required into preference,
    - turn reasoning_required into preference.
  - At each step:
    - re-run filter + scoring.
    - record a human-readable string in `relaxations`.
  - If still none:
    - return empty candidates + full list of attempted relaxations.

---

### SP9 – Selector Orchestrator (per-role selection)

Folder: `src/generator/sp9_selector_orchestrator/`

- Purpose: Single entrypoint to select model(s) for a RoleNeed.
- Inputs:
  - `RoleNeed`, `List[CanonicalModel]`, selector options.
- Outputs:
  - `SelectionResult` (primary, backups, rationale, relaxations).
- Public Interfaces:
  - `select_for_role(role: RoleNeed, models: list[CanonicalModel], options: SelectorOptions) -> SelectionResult`
- Rules:
  - Path:
    - run SP5 (filter); if non-empty:
      - SP6 (weights) → SP7 (scoring).
    - if empty:
      - SP6 (weights) → SP8 (relaxation engine).
  - Always return a `SelectionResult` with:
    - role_id,
    - primary (may be None),
    - backups (0..N),
    - rationale: e.g. top factors, score range,
    - relaxation_applied: list of strings.

---

### SP10 – Machine Config Emitter (multi-role → llm-hub.yaml)

Folder: `src/generator/sp10_machine_config_emitter/`

- Purpose: Assemble all selections into a machine config file for LLM Hub Runtime.
- Inputs:
  - `ProjectSpec`, `List[SelectionResult]`.
- Outputs:
  - `MachineConfig` (in Python) and written YAML on disk.
- Public Interfaces:
  - `build_machine_config(spec: ProjectSpec, selections: list[SelectionResult]) -> MachineConfig`
  - `write_machine_config(path: str, config: MachineConfig) -> None`
- Rules:
  - Map `RoleNeed.id` / spec roles to `llm.<role_name>` entries.
  - Include:
    - provider, model,
    - backups,
    - optional `meta` section with rationale and relaxations.
  - YAML format must be compatible with LLM Hub Runtime resolver.

---

## 5. End-to-End Generator API

Library-level API inside `src/generator/__init__.py`:

- `generate_machine_config(spec_path: str, hub: Hub, catalog_override: list[CanonicalModel] | None = None) -> MachineConfig`

Steps:

1. Load YAML at `spec_path`.
2. SP1: `ProjectSpec = parse_project_spec(raw)`.
3. SP2: `raw_needs = interpret_needs(ProjectSpec, hub, model_role="llm.generator")`.
4. SP3: `needs = parse_role_needs(raw_needs)`.
5. SP4: `models = load_catalog_view()` (unless `catalog_override` is provided).
6. For each role in `needs`:
   - SP9: `SelectionResult`.
7. SP10: build and optionally write the machine config.

CLI will call this API; UI will later call the same entry.

---

## 6. Acceptance Criteria (for v1)

- Generator lives entirely under `src/generator/` with the structure above.
- Each SP folder has a `spec.md` that matches the template.
- `generate_machine_config(...)` works end-to-end with:
  - mocked Hub (no real API calls needed),
  - a small mock catalog.
- Output config is accepted by LLM Hub Runtime and used to resolve LLM roles.
- No network calls or scraping inside generator; only:
  - one structured-output LLM call in SP2 (using runtime),
  - catalog data from catalog module (already handled elsewhere).