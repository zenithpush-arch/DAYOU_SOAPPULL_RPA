import re
from typing import Dict, List, Optional, Tuple

from config import _base_dir, load_settings

QUERY_PATH = _base_dir() / 'query.sql'

_SECTION_RE = re.compile(r'^\s*--\s*\[(\w+)\]')
_QUERY_CACHE: Optional[Dict[str, str]] = None


def load_queries(reload: bool = False) -> Dict[str, str]:
    """Parse query.sql into {section_name: sql}. Comment lines are skipped."""
    global _QUERY_CACHE
    if _QUERY_CACHE is not None and not reload:
        return _QUERY_CACHE

    queries: Dict[str, List[str]] = {}
    name = None
    for line in QUERY_PATH.read_text(encoding='utf-8-sig').splitlines():
        m = _SECTION_RE.match(line)
        if m:
            name = m.group(1)
            queries[name] = []
        elif name and not line.strip().startswith('--'):
            queries[name].append(line)

    _QUERY_CACHE = {k: '\n'.join(v).strip().rstrip(';') for k, v in queries.items()}
    return _QUERY_CACHE


def get_insert_query(file_type: str) -> Tuple[str, int]:
    """Build full INSERT for a file type (P6/P7/D1/D2).

    Returns (sql, param_count). VALUES gets one "?" per column in the column list.
    """
    key = f'insert{file_type.upper()}'
    queries = load_queries()
    if key not in queries:
        raise KeyError(f'query [{key}] not found in {QUERY_PATH.name}')

    head = queries[key]
    table = load_settings(f'info.{file_type.lower()}.table')
    if not table:
        raise KeyError(f'config "info.{file_type.lower()}.table" is not set')
    head = head.replace('{table}', table)

    cols = parse_columns(head)

    # one "?" per column
    sql = f'{head}\nVALUES ({", ".join("?" * len(cols))})'
    return sql, len(cols)


def parse_columns(sql: str) -> List[str]:
    """Column names inside the first '( ... )' of an INSERT statement."""
    start, end = sql.find('('), sql.find(')')
    if start < 0 or end < start:
        raise ValueError('column list "( ... )" not found')
    return [c.strip() for c in sql[start + 1:end].split(',') if c.strip()]
