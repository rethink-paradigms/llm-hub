# PLAN-catalog-v1-arena-integration.md

## 0. Context and Intent

This is an **incremental update** to `PLAN-catalog-v1.md`, focused only on **how we obtain and refresh LMArena data** for the Catalog.

Previously:
- `arena_source.py` used **mock data** or placeholder logic.
- `Catalog` pipeline assumed a function `load_arena_models(...) -> dict[str, ArenaModel]` that returns real leaderboard data.

Now:
- We have the official `update_leaderboard_data.py` script from the `lmarena/arena-catalog` project in our repo.
- That script already knows how to fetch, assemble, and output the leaderboard JSON for various model categories.

**Goal of this plan**  
Replace mock arena data with a robust integration that:
- Uses `update_leaderboard_data.py` to produce the JSON we need.
- Caches that JSON locally with a **TTL of 24 hours**.
- Keeps the rest of the Catalog design intact (no rewrites of schema/builder/generator).

---

## 1. High-level Design

We keep the original responsibilities from `PLAN-catalog-v1`:

- `arena_source.py` should:
  - Ensure up-to-date LMArena JSON is available locally.
  - Parse that JSON into our `ArenaModel` records.
  - Return a mapping of `arena_id -> ArenaModel`.

**New behavior**:

1. **Arena data cache**  
   - We will cache the raw leaderboard JSON from `update_leaderboard_data.py` under a config directory, e.g.:

     ```text
     ~/.config/llmhub/arena/leaderboard-text.json
     ```

   - Cache will be refreshed if:
     - No file exists, or
     - File is older than **24 hours**.

2. **Script-driven refresh**  
   - When refresh is needed, `arena_source.py` will **call** `update_leaderboard_data.py` to regenerate JSON files.
   - We will **not** reimplement the fetching or aggregation logic; we just run the upstream script.

3. **Decoupled failure behavior**  
   - If the script fails but a *stale* JSON file exists:
     - We log/print a warning and **fall back** to the stale file (even if >24h), so Catalog can still build.
   - If no JSON exists and script fails:
     - `load_arena_models()` returns an empty dict, and the Catalog pipeline will treat `arena` as missing (graceful degradation).

Everything else in `PLAN-catalog-v1` (schema, mapping, builder, cache) remains as is.

---

## 2. Repository Layout for Arena Integration

Assume we place the vendor script under:

```text
llmhub/catalog/vendor/arena/update_leaderboard_data.py

We do not modify the internals of this script unless strictly necessary. It is treated as an upstream dependency.

Arena-related files:

llmhub/catalog/
  arena_source.py
  ...
  vendor/
    arena/
      update_leaderboard_data.py

Cache location (runtime):

~/.config/llmhub/arena/leaderboard-text.json

Optionally, we can also support an environment variable override:
	•	LLMHUB_ARENA_CACHE_DIR (default to ~/.config/llmhub/arena).

⸻

3. arena_source.py Spec Update

3.1 Responsibilities

arena_source.py now has two clear responsibilities:
	1.	Ensure arena JSON is present and up to date (run upstream script if needed).
	2.	Parse arena JSON into our internal ArenaModel objects.

3.2 Public Interface

We keep the same public interface expected by the rest of Catalog:

def load_arena_models(path: Path | None = None) -> dict[str, ArenaModel]:
    """
    Ensure LMArena leaderboard JSON exists and is fresh enough (24h TTL),
    then load it and normalize into dict[str, ArenaModel].
    """

If path is provided:
	•	Use it directly as the JSON path (no TTL check or script run).
	•	This is mainly for testing or special cases.

If path is None:
	•	Use default cache path (see below) and apply full TTL + script logic.

⸻

4. Detailed Flow: Refresh and Load

4.1 Utility: resolve cache path

Add helper:

def _get_arena_cache_path() -> Path:
    """
    Resolve the path to the arena leaderboard JSON.
    Uses env var LLMHUB_ARENA_CACHE_DIR if set, otherwise:
        ~/.config/llmhub/arena/leaderboard-text.json
    Ensures the parent directory exists.
    """

4.2 Utility: check TTL and freshness

def _is_fresh(path: Path, ttl_hours: int = 24) -> bool:
    """
    Return True if file exists and its mtime is within ttl_hours.
    """

4.3 Utility: run the upstream script

We want arena_source to be robust regardless of how update_leaderboard_data.py is structured internally. So:

def _run_arena_update_script(cache_dir: Path) -> bool:
    """
    Run the vendor script update_leaderboard_data.py to populate
    the arena leaderboard JSON files under cache_dir.

    Returns True if it appears to succeed (expected JSON file exists),
    False otherwise.
    """

Implementation-level expectations:
	•	The IDE should inspect update_leaderboard_data.py to see:
	•	Does it accept CLI arguments for output directory?
	•	Does it have a callable main()?
	•	Prefer import and call if feasible, e.g.:

from llmhub.catalog.vendor.arena import update_leaderboard_data

update_leaderboard_data.main(output_dir=cache_dir)


	•	If that’s not possible due to script design:
	•	Use subprocess.run(["python", path_to_script, "--output", str(cache_dir)], ...)
	•	The IDE should match whatever invocation is expected by the upstream script.

The critical point:
After running this function, we expect the script to have created or updated leaderboard-text.json (or whatever canonical filename we decide on) in cache_dir.

4.4 Arena data refresh logic

Add:

def _ensure_arena_json(ttl_hours: int = 24) -> Path | None:
    """
    Ensure we have a leaderboard JSON file.

    Steps:
      1) Determine cache_path via _get_arena_cache_path().
      2) If cache_path exists and _is_fresh(cache_path, ttl_hours): return cache_path.
      3) Else, attempt to run _run_arena_update_script(cache_dir).
         - If success and cache_path exists: return cache_path.
         - If failure:
             - If a stale cache_path exists: log warning and return cache_path.
             - Else: log error and return None.
    """

This gives us a single entry point to manage TTL and script calls.

⸻

5. Parsing Arena JSON into ArenaModel

Once _ensure_arena_json() returns a Path, the rest of load_arena_models() is straightforward:

def load_arena_models(path: Path | None = None) -> dict[str, ArenaModel]:
    if path is None:
        path = _ensure_arena_json(ttl_hours=24)
        if path is None:
            # No usable data; return empty map
            return {}

    # 1) Read the JSON file.
    # 2) Pick the correct leaderboard structure (e.g., "overall text" category).
    # 3) For each entry, extract:
    #       - arena_id (model name as used by LMArena)
    #       - rating
    #       - rating_q025
    #       - rating_q975
    # 4) Build ArenaModel instances and return dict[arena_id, ArenaModel].

The IDE should inspect the actual JSON structure produced by update_leaderboard_data.py to define:
	•	Where the “overall text” leaderboard lives in the JSON.
	•	What the exact key names are (rating, rating_q025, etc.).

Mapping rules from JSON to ArenaModel must reflect the real structure.

⸻

6. Interaction with Existing Catalog Pipeline

No changes are needed to:
	•	schema.py
	•	mapper.py
	•	builder.py
	•	cache.py
	•	Generator logic

From builder.py perspective:
	•	It still calls:

from llmhub.catalog.arena_source import load_arena_models

arena_map = load_arena_models()


	•	And gets back:

dict[str, ArenaModel]



The only change is that ArenaModel instances are now populated from real LMArena JSON instead of mocks.

When Catalog builds:
	1.	anyllm_source → available models.
	2.	modelsdev_source → models.dev metadata.
	3.	arena_source.load_arena_models() → real LMArena quality scores.
	4.	mapper.fuse_sources(...) → fuse all three.
	5.	builder._derive_canonical(...) → compute tiers.
	6.	cache.save_catalog(...) → final catalog JSON.

⸻

7. Edge Cases and Behavior Expectations
	1.	No network / LMArena temporarily down
	•	If we already have a JSON file (even stale):
	•	_ensure_arena_json returns that path with a warning.
	•	If we have no JSON at all:
	•	load_arena_models() returns {}.
	•	Catalog still builds, but all arena data is missing, and tiers fall back to provider/family heuristics.
	2.	Script changes upstream
	•	If update_leaderboard_data.py changes its output schema or filenames:
	•	Parsing may break; we log/raise a clear error on parsing.
	•	This is an integration maintenance task, but our design isolates it to arena_source.py.
	3.	User custom path for arena JSON
	•	If user passes path explicitly to load_arena_models(path=...):
	•	TTL + script logic is bypassed.
	•	This is mainly for tests/experiments.

⸻

8. Implementation Checklist

To implement this improvement, the IDE (e.g. Antigravity) must:
	1.	Place update_leaderboard_data.py under llmhub/catalog/vendor/arena/ (or use the path where it already exists).
	2.	Implement the following helpers in arena_source.py:
	•	_get_arena_cache_path()
	•	_is_fresh(path, ttl_hours)
	•	_run_arena_update_script(cache_dir)
	•	_ensure_arena_json(ttl_hours)
	3.	Update load_arena_models() to:
	•	Use _ensure_arena_json() when path is None.
	•	Parse the generated JSON into ArenaModel instances.
	4.	Remove or replace any mock/stub data previously used in arena_source.py.
	5.	Ensure build_catalog() in builder.py still works without changes to its external contract.
	6.	Add or update tests to cover:
	•	Fresh data path (no cache → script run → new JSON).
	•	Cache hit path (fresh JSON, no script).
	•	Script failure with stale cache.
	•	Script failure with no cache (empty arena map).

