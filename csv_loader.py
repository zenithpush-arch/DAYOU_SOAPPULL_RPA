from datetime import datetime
from pathlib import Path
from typing import Union

import pandas as pd
from loguru import logger

from config import load_settings


def col_to_idx(col: str) -> int:
    """Excel-style column letter to 0-based index (A=0, Z=25, AA=26)."""
    col = col.strip().upper()
    if not col.isalpha():
        raise ValueError(f'invalid column name: {col!r}')
    idx = 0
    for ch in col:
        idx = idx * 26 + (ord(ch) - ord('A') + 1)
    return idx - 1


def _clean(x):
    """Strip BOM / nbsp / padding spaces; empty string becomes None."""
    if isinstance(x, str):
        x = x.replace('﻿', '').replace(' ', ' ').strip()
        return x or None
    return x


def _read_csv(path: Path) -> pd.DataFrame:
    """Read every cell as raw text (no type inference). Tries utf-8 then cp949."""
    for enc in ('utf-8-sig', 'cp949'):
        try:
            return pd.read_csv(path, header=None, encoding=enc, dtype=str, keep_default_na=False)
        except UnicodeDecodeError:
            continue
    raise ValueError(f'cannot decode file: {path}')


def read_file(file_path: Union[str, Path]) -> pd.DataFrame:
    """Read csv, drop configured columns, prepend file mtime and plan_sq.

    File name format: <..>_<..>_<TYPE>_<DATE>_<PLAN_SQ>_<..>.csv
    """
    p = Path(file_path)
    parts = p.stem.split('_')
    file_type = parts[2].lower()  # e.g. 'd2'
    plan_sq = parts[4]
    mt = datetime.fromtimestamp(p.stat().st_mtime)

    try:
        df = _read_csv(p)
    except pd.errors.EmptyDataError:
        logger.warning(f'empty file: {p.name}')
        return pd.DataFrame()

    # strip padding; empty -> None (pandas may turn None back into NaN here, fixed below)
    df = df.astype(object).map(_clean)

    drop_cols = load_settings(f'info.{file_type}.drop_column', [])
    df = df.drop(columns=[col_to_idx(c) for c in drop_cols])

    df.insert(0, 'plan_sq', plan_sq)
    df.insert(0, 'plan_dt', mt)

    # pandas 3 str dtype stores missing as NaN; pyodbc cannot bind NaN (22003) -> use None
    df = df.astype(object)
    df = df.where(df.notna(), None)

    return df.reset_index(drop=True)
