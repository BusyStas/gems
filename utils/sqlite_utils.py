"""Helpers for working with sqlite3.Row objects.

Provides a safe conversion to plain dict so callers can use dict.get()
without worrying about sqlite3.Row differences between Python versions.
"""
from typing import Any, Dict


def row_to_dict(row: Any) -> Dict[str, Any]:
    """Convert a sqlite3.Row (or mapping) to a plain dict safely.

    Returns empty dict when row is None or conversion fails.
    """
    if row is None:
        return {}
    try:
        # sqlite3.Row supports the mapping protocol; dict(row) works in CPython
        return dict(row)
    except Exception:
        # Fallback: attempt to iterate keys()
        try:
            return {k: row[k] for k in getattr(row, 'keys', lambda: [])()}
        except Exception:
            return {}
