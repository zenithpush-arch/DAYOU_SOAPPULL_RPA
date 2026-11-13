import shutil
import pyodbc
import time
from pathlib import Path
from typing import List, Optional

from config import load_settings
from csv_loader import read_file
from logger import setup_logger
from query_loader import get_insert_query

log = setup_logger()  # loguru logger (console + daily file)

TARGET_TYPES = ('P6', 'P7', 'D1', 'D2')


def get_target_files(folder_path: str, fmt: Optional[str] = None) -> List[Path]:
    """Files in folder (non-recursive) with given extension, oldest first."""
    folder = Path(folder_path)
    if not folder.is_dir():
        raise FileNotFoundError(f'target folder not found: {folder}')

    fmt = fmt.lower() if fmt else None
    files = [p for p in folder.iterdir() if p.is_file() and (fmt is None or p.suffix.lower() == fmt)]
    files.sort(key=lambda x: x.stat().st_mtime)
    return files


def move_file(folder_path, file_path) -> Path:
    """Move file to <folder>/<YYYY>_BACKUP/ (year from file name). Overwrites existing."""
    src = Path(file_path)
    if not src.exists():
        raise FileNotFoundError(src)

    parts = src.name.split('_')
    if len(parts) < 4:
        raise ValueError(f'Unexpected filename format: {src.name}')

    file_year = parts[3][:4]
    if not (file_year.isdigit() and len(file_year) == 4):
        raise ValueError(f'Invalid year extracted from filename: {src.name}')

    dst_dir = Path(folder_path) / f'{file_year}_BACKUP'
    dst_dir.mkdir(parents=True, exist_ok=True)

    dst = dst_dir / src.name
    if dst.exists():
        dst.unlink()  # overwrite

    shutil.move(str(src), str(dst))
    return dst


def _odbc_value(v: str) -> str:
    """Wrap value in {} so spaces / ';' in driver name or password are safe."""
    v = str(v)
    if v.startswith('{') and v.endswith('}'):
        return v
    return '{' + v.replace('}', '}}') + '}'


def make_connection() -> pyodbc.Connection:
    info = load_settings('database')
    conn = pyodbc.connect(
        f"DRIVER={_odbc_value(info['driver'])};"
        f"SERVER={info['server']};"
        f"DATABASE={info['database']};"
        f"UID={info['uid']};"
        f"PWD={_odbc_value(info['pwd'])};",
        autocommit=False,
    )
    log.info(f"DB connected: {info['server']}/{info['database']}")
    return conn


"""
File name samples
P6 : RKW7_KMC_P6_20260202_23_RKW7.csv
P7 : RKW7_KMC_P7_20260202_23_RKW7.csv
D1 : RKW7_HMC_D1_20260101_1_RKW7.csv
D2 : RKW7_HMC_D2_20260202_3_RKW7.csv
"""
def run():
    target = load_settings('target')
    root = target['root']
    fmt = target['fmt']

    files = get_target_files(root, fmt)
    log.info(f'Found {len(files)} file(s) in {root}')
    if not files:
        return

    try:
        conn = make_connection()
    except pyodbc.Error:
        log.exception('DB connection failed')
        return

    try:
        _process_files(conn, root, files)
    finally:
        conn.close()


def _process_files(conn: pyodbc.Connection, root: str, files: List[Path]) -> None:
    for f in files:
        file_name = f.name
        try:
            parts = file_name.split('_')
            file_type = parts[2].upper() if len(parts) > 2 else ''

            log.info(f'Check file: {file_name} (type={file_type or "?"})')
            if file_type not in TARGET_TYPES:
                dst = move_file(root, f)
                log.info(f'Not target, moved: {file_name} -> {dst.parent.name}')
                continue

            df = read_file(f)
            if df.empty:
                raise ValueError('df is empty')
            log.info(f'Read {file_name}: {len(df)} rows x {len(df.columns)} cols')

            sql, n_param = get_insert_query(file_type)
            if len(df.columns) != n_param:
                raise ValueError(f'column count mismatch: data {len(df.columns)} != query {n_param}')

            # positional rows for "INSERT ... VALUES (?, ?, ...)"
            rows = df.values.tolist()
            log.debug(f'{file_name}: {len(rows)} rows ready for insert{file_type}')

            table_name = load_settings(f'info.{file_type.lower()}.table')

            cur = conn.cursor()
            try:
                cur.fast_executemany = True
                cur.executemany(sql, rows)
                conn.commit()
            except Exception:
                conn.rollback()  # discard partial insert of this file
                raise
            finally:
                cur.close()
            log.info(f'Inserted {len(rows)} rows to [ {table_name} ]')

        except Exception:
            # one bad file must not stop the rest
            log.exception(f'Failed: {file_name}')
            continue

        # insert already committed: a move failure must not look like an insert failure
        try:
            dst = move_file(root, f)
            log.info(f'Moved: {file_name} -> {dst.parent.name}')
        except Exception:
            log.exception(f'Inserted but move failed (may be inserted again next run): {file_name}')


if __name__ == '__main__':
    interval = load_settings('interval')

    while True:
        run()
        time.sleep(interval)
