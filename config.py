import sys
import json
from pathlib import Path
from typing import Any, Dict, Optional

_CFG_CACHE: Optional[Dict[str, Any]] = None


def _base_dir() -> Path:
    """Exe folder when frozen (PyInstaller), otherwise this file's folder."""
    return Path(sys.executable).parent if getattr(sys, 'frozen', False) else Path(__file__).resolve().parent


def _load_config_json(base_dir: Path) -> Dict[str, Any]:
    cfg_path = base_dir / 'config.json'
    if not cfg_path.exists():
        raise FileNotFoundError(f'config.json not found at: {cfg_path}')
    # utf-8-sig: tolerate BOM written by some Windows editors
    return json.loads(cfg_path.read_text(encoding='utf-8-sig')) or {}


def load_settings(dot_key: Optional[str] = None, default: Any = None, reload: bool = False) -> Any:
    """Get a value from config.json.

    dot_key: e.g. 'database.server', 'table.p6', 'd2_drop_idx.0'
            None returns the whole config.
    default: returned when the key is missing.
    reload:  re-read config.json from disk.
    """
    global _CFG_CACHE
    if _CFG_CACHE is None or reload:
        _CFG_CACHE = _load_config_json(_base_dir())

    if dot_key is None:
        return _CFG_CACHE

    cur: Any = _CFG_CACHE
    for k in dot_key.split('.'):
        if isinstance(cur, dict) and k in cur:
            cur = cur[k]
        elif isinstance(cur, list) and k.lstrip('-').isdigit() and -len(cur) <= int(k) < len(cur):
            cur = cur[int(k)]  # list index access
        else:
            return default
    return cur
