"""Utilities to purge old MSAL cache files and run a periodic scheduler.

Functions:
- purge_old_caches(...)
- start_cache_cleanup_scheduler(...)

This module is intentionally dependency-free (stdlib only) and uses a
background thread. For multi-process deployments consider an external
cron/leader election to avoid duplicate runners.
"""

from __future__ import annotations

import os
import time
import threading
import random
from pathlib import Path
from typing import List, Optional
import src.app_logging as al

# pylint: disable=W1203

_LOCK = threading.Lock()


def purge_old_caches(
    cache_dir: str | Path = "msal_cache",
    pattern: str = "msalcache_*.json",
    max_age_minutes: int = 60,
    secure_overwrite: bool = False,
) -> List[Path]:
    """Delete MSAL cache files older than `max_age_minutes`.

    Returns a list of deleted Path objects.
    """
    cache_path = Path(cache_dir)
    if not cache_path.exists():
        al.logger.info(
            f"Cache directory '{cache_path}' does not exist; nothing to purge."
        )
        return []

    now = time.time()
    max_age_seconds = max_age_minutes * 60
    deleted: List[Path] = []

    with _LOCK:
        for file_path in cache_path.glob(pattern):
            if not file_path.is_file():
                continue
            try:
                age = now - file_path.stat().st_mtime
                if age < max_age_seconds:
                    continue

                if secure_overwrite:
                    try:
                        size = max(1, file_path.stat().st_size)
                        with file_path.open("r+b") as fh:
                            fh.seek(0)
                            fh.write(os.urandom(size))
                            fh.flush()
                    except Exception as e:
                        al.logger.warning(
                            f"Secure overwrite failed for {file_path.name}: {e}"
                        )

                file_path.unlink(missing_ok=True)
                deleted.append(file_path)
            except Exception as e:
                al.logger.error(f"Failed deleting {file_path.name}: {e}")

    if deleted:
        al.logger.info(
            f"Purged {len(deleted)} old cache file(s): {[p.name for p in deleted]}"
        )
    else:
        al.logger.debug("No cache files met age threshold for purge.")
    return deleted


def start_cache_cleanup_scheduler(
    interval_minutes: Optional[int] = None,
    max_age_minutes: Optional[int] = None,
    cache_dir: str | Path = "msal_cache",
    pattern: str = "msalcache_*.json",
    secure_overwrite: Optional[bool] = None,
    daemon: bool = True,
) -> threading.Event:
    """Start a background thread that periodically purges old cache files.

    Returns a threading.Event that can be set to signal shutdown.
    """
    if interval_minutes is None:
        interval_minutes = int(os.environ.get("CACHE_PURGE_INTERVAL_MINUTES"))
    if max_age_minutes is None:
        max_age_minutes = int(os.environ.get("CACHE_MAX_AGE_MINUTES"))
    if secure_overwrite is None:
        secure_overwrite = os.environ.get(
            "CACHE_SECURE_OVERWRITE", "false"
        ).lower() in {"1", "true", "yes"}

    interval_seconds = max(1, int(interval_minutes)) * 60
    stop_event = threading.Event()

    def _loop():
        al.logger.info(
            f"Cache cleanup scheduler starting (every {interval_minutes}m, "
            f"delete older than {max_age_minutes}m)"
        )
        # jitter to reduce thundering herd
        time.sleep(random.uniform(0, min(10.0, interval_seconds / 4)))
        while not stop_event.is_set():
            try:
                purge_old_caches(
                    cache_dir=cache_dir,
                    pattern=pattern,
                    max_age_minutes=max_age_minutes,
                    secure_overwrite=secure_overwrite,
                )
            except Exception as e:
                al.logger.error(f"Unexpected error in cache purge loop: {e}")
            stop_event.wait(interval_seconds)
        al.logger.info("Cache cleanup scheduler stopped.")

    thread = threading.Thread(target=_loop, name="cache-cleanup", daemon=daemon)
    thread.start()
    return stop_event


__all__ = ["purge_old_caches", "start_cache_cleanup_scheduler"]
