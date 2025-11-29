"""
LMArena source: load and normalize arena-catalog leaderboard data.

This module provides quality scores (Elo ratings) from the LMArena leaderboard.
Integrates with the vendored update_leaderboard_data.py script with 24h TTL caching.
"""
import json
import os
import sys
import subprocess
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional
from .schema import ArenaModel


def _get_arena_cache_path() -> Path:
    """
    Resolve the path to the arena leaderboard JSON.
    Uses env var LLMHUB_ARENA_CACHE_DIR if set, otherwise:
        ~/.config/llmhub/arena/leaderboard-text.json
    Ensures the parent directory exists.
    """
    cache_dir_env = os.environ.get("LLMHUB_ARENA_CACHE_DIR")
    
    if cache_dir_env:
        cache_dir = Path(cache_dir_env)
    else:
        # Use OS-appropriate config directory
        cache_dir = Path.home() / ".config" / "llmhub" / "arena"
    
    # Ensure directory exists
    cache_dir.mkdir(parents=True, exist_ok=True)
    
    return cache_dir / "leaderboard-text.json"


def _is_fresh(path: Path, ttl_hours: int = 24) -> bool:
    """
    Return True if file exists and its mtime is within ttl_hours.
    
    Args:
        path: Path to check
        ttl_hours: Time-to-live in hours
        
    Returns:
        True if file is fresh, False otherwise
    """
    if not path.exists():
        return False
    
    try:
        mtime = datetime.fromtimestamp(path.stat().st_mtime)
        age = datetime.now() - mtime
        return age <= timedelta(hours=ttl_hours)
    except OSError:
        return False


def _run_arena_update_script(cache_dir: Path) -> bool:
    """
    Run the vendor script update_leaderboard_data.py to populate
    the arena leaderboard JSON files under cache_dir.

    Returns True if it appears to succeed (expected JSON file exists),
    False otherwise.
    
    Args:
        cache_dir: Directory where the script should write output
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Get path to vendor script
        vendor_script = Path(__file__).parent / "vendor" / "arena" / "update_leaderboard_data.py"
        
        if not vendor_script.exists():
            print(f"Warning: Arena update script not found at {vendor_script}")
            return False
        
        # Create a data subdirectory in cache_dir for the script's output
        data_dir = cache_dir / "data"
        data_dir.mkdir(parents=True, exist_ok=True)
        
        # Run the script using subprocess
        # The script writes to 'data/leaderboard-*.json' relative to its working directory
        result = subprocess.run(
            [sys.executable, str(vendor_script)],
            cwd=str(cache_dir),
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )
        
        # Check if the expected output file was created
        expected_output = data_dir / "leaderboard-text.json"
        
        if expected_output.exists():
            # Move the file to the parent cache_dir for consistency
            target_path = cache_dir / "leaderboard-text.json"
            expected_output.replace(target_path)
            return True
        
        # Script ran but didn't produce expected output
        if result.returncode != 0:
            print(f"Warning: Arena update script failed with code {result.returncode}")
            if result.stderr:
                print(f"Error output: {result.stderr[:500]}")
        
        return False
        
    except subprocess.TimeoutExpired:
        print("Warning: Arena update script timed out after 5 minutes")
        return False
    except Exception as e:
        print(f"Warning: Failed to run arena update script: {e}")
        return False


def _ensure_arena_json(ttl_hours: int = 24) -> Optional[Path]:
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
             
    Args:
        ttl_hours: Time-to-live in hours
        
    Returns:
        Path to arena JSON if available, None otherwise
    """
    cache_path = _get_arena_cache_path()
    cache_dir = cache_path.parent
    
    # Check if we have fresh data
    if _is_fresh(cache_path, ttl_hours):
        return cache_path
    
    # Need to refresh - run the update script
    print("Arena data is stale or missing, attempting to refresh...")
    success = _run_arena_update_script(cache_dir)
    
    if success and cache_path.exists():
        print("✓ Arena data refreshed successfully")
        return cache_path
    
    # Script failed - check if we have stale data to fall back on
    if cache_path.exists():
        print(f"Warning: Arena update script failed, using stale data from {cache_path}")
        return cache_path
    
    # No data available at all
    print("Error: Arena update script failed and no cached data available")
    return None


def load_arena_models(path: Optional[Path] = None) -> dict[str, ArenaModel]:
    """
    Ensure LMArena leaderboard JSON exists and is fresh enough (24h TTL),
    then load it and normalize into dict[str, ArenaModel].
    
    Args:
        path: Optional explicit path to arena catalog JSON. If provided,
              reads directly without TTL check or script execution.
              If None, uses TTL-based cache with automatic refresh.
        
    Returns:
        Dict mapping arena_id (model name) to ArenaModel with ratings.
        Returns empty dict if no data is available.
    """
    # If explicit path provided, use it directly (no TTL/script logic)
    if path is not None:
        if not path.exists():
            print(f"Warning: Provided arena path does not exist: {path}")
            return {}
        data_path = path
    else:
        # Use TTL-based cache with automatic refresh
        data_path = _ensure_arena_json(ttl_hours=24)
        if data_path is None:
            return {}
    
    # Parse the JSON file
    arena_map: dict[str, ArenaModel] = {}
    
    try:
        with open(data_path, 'r') as f:
            data = json.load(f)
        
        # Arena data structure: { category: { model_name: { rating, rating_q975, rating_q025 } } }
        # Prefer "overall_text" category if available
        for category, models in data.items():
            for model_name, scores in models.items():
                if not isinstance(scores, dict):
                    continue
                
                rating = scores.get("rating")
                if rating is None:
                    continue
                
                # Use model_name as arena_id
                arena_id = model_name
                
                # Only keep if we don't already have this model or if this is "overall_text"
                if arena_id not in arena_map or category == "overall_text":
                    arena_map[arena_id] = ArenaModel(
                        arena_id=arena_id,
                        rating=float(rating),
                        rating_q025=float(scores["rating_q025"]) if scores.get("rating_q025") is not None else None,
                        rating_q975=float(scores["rating_q975"]) if scores.get("rating_q975") is not None else None,
                        category=category
                    )
        
        return arena_map
        
    except (json.JSONDecodeError, IOError, ValueError) as e:
        print(f"Warning: Failed to parse arena JSON from {data_path}: {e}")
        return {}
