"""Simple database error logger used across the app.

Writes timestamped entries to logs/db_errors.log with a short context message
and the exception traceback. This is intentionally minimal to avoid adding
external dependencies.
"""
import os
import traceback
from datetime import datetime


def _ensure_logs_dir():
    logs_dir = os.path.join(os.getcwd(), 'logs')
    try:
        os.makedirs(logs_dir, exist_ok=True)
    except Exception:
        # Best-effort: if we cannot create logs dir, give up silently
        return None
    return logs_dir


def log_db_exception(exc: Exception, context: str = ''):
    """Append a timestamped DB error entry to logs/db_errors.log.

    Args:
        exc: Exception instance
        context: short descriptive string where the error happened
    """
    try:
        logs_dir = _ensure_logs_dir()
        if not logs_dir:
            return
        path = os.path.join(logs_dir, 'db_errors.log')
        ts = datetime.utcnow().isoformat() + 'Z'
        header = f"[{ts}] DB ERROR"
        if context:
            header += f" - {context}"
        with open(path, 'a', encoding='utf-8') as f:
            f.write(header + '\n')
            f.write('Exception: ' + repr(exc) + '\n')
            f.write('Traceback:\n')
            f.write(traceback.format_exc())
            f.write('\n' + ('-' * 80) + '\n')
    except Exception:
        # Intentionally swallow any logging errors to avoid cascading failures
        return
