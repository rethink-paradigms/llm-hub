"""
Cache: disk caching for Catalog with TTL support.

Caches catalog.json to ~/.config/llmhub/ (or OS-appropriate config dir).
"""
import json
import os
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional
import platform
from .schema import Catalog


def _get_cache_dir() -> Path:
    """Get OS-appropriate config directory for llmhub."""
    system = platform.system()
    
    if system == "Darwin":  # macOS
        base = Path.home() / ".config" / "llmhub"
    elif system == "Windows":
        appdata = Path(os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming"))
        base = appdata / "llmhub"
    else:  # Linux and others
        base = Path.home() / ".config" / "llmhub"
    
    # Create directory if it doesn't exist
    base.mkdir(parents=True, exist_ok=True)
    return base


def _get_cache_path() -> Path:
    """Get full path to catalog.json cache file."""
    return _get_cache_dir() / "catalog.json"


def load_cached_catalog(ttl_hours: int = 24) -> Optional[Catalog]:
    """
    Load cached catalog if it exists and is fresh.
    
    Args:
        ttl_hours: Time-to-live in hours. Cache older than this is ignored.
        
    Returns:
        Catalog if cache is fresh, None otherwise.
    """
    cache_path = _get_cache_path()
    
    if not cache_path.exists():
        return None
    
    try:
        # Check modification time
        mtime = datetime.fromtimestamp(cache_path.stat().st_mtime)
        age = datetime.now() - mtime
        
        if age > timedelta(hours=ttl_hours):
            # Cache is stale
            return None
        
        # Load and parse
        with open(cache_path, 'r') as f:
            data = json.load(f)
        
        return Catalog(**data)
        
    except (json.JSONDecodeError, IOError, ValueError) as e:
        # Cache is corrupted or invalid
        return None


def save_catalog(catalog: Catalog) -> None:
    """
    Save catalog to disk cache.
    
    Args:
        catalog: Catalog instance to save.
    """
    cache_path = _get_cache_path()
    
    try:
        # Serialize to JSON
        data = catalog.model_dump()
        
        # Write to file
        with open(cache_path, 'w') as f:
            json.dump(data, f, indent=2)
            
    except (IOError, ValueError) as e:
        # Non-fatal - just log warning
        print(f"Warning: Failed to save catalog cache: {e}")


def clear_cache() -> bool:
    """
    Clear the catalog cache.
    
    Returns:
        True if cache was cleared, False if no cache existed.
    """
    cache_path = _get_cache_path()
    
    if cache_path.exists():
        try:
            cache_path.unlink()
            return True
        except IOError:
            return False
    
    return False
