import sys
from pathlib import Path
from typing import Optional, Union

from loguru import logger

from config import _base_dir, load_settings

LOG_FORMAT = '{time:YYYY-MM-DD HH:mm:ss.SSS} [{level}] {name}:{line} - {message}'


def setup_logger(
    expire_days: Optional[int] = None,
    log_dir: Union[str, Path, None] = None,
    prefix: str = 'app',
    level: str = 'INFO',
    console: bool = True,
):
    """Configure loguru: one log file per day, delete files older than expire_days.

    expire_days: keep logs for this many days (default: config.json "expire", else 30)
    log_dir:     log folder (default: <base_dir>/logs)
    """
    if expire_days is None:
        expire_days = int(load_settings('expire', 30))
    log_dir = Path(log_dir) if log_dir else _base_dir() / 'logs'

    logger.remove()  # drop default stderr handler
    if console:
        logger.add(sys.stderr, level=level, format=LOG_FORMAT, diagnose=False)
    logger.add(
        log_dir / f'{prefix}_{{time:YYYY-MM-DD}}.log',
        rotation='00:00',                  # new file at midnight
        retention=f'{expire_days} days',   # delete older files on rotation
        encoding='utf-8',
        level=level,
        format=LOG_FORMAT,
        diagnose=False,                    # no variable values in tracebacks (may hold secrets)
        enqueue=True,                      # thread/process safe
    )
    return logger
