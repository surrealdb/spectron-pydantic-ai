"""Helpers for turning Spectron results into text for a model to read.

Spectron returns structured results. The exact shape depends on the operation
and the SDK version, so these helpers accept a range of shapes (a string, a
list of records, or a mapping with a ``results``/``memories`` key) and produce a
compact, readable block.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

_RESULT_KEYS = ("results", "memories", "facts", "items", "data")
_TEXT_KEYS = ("content", "text", "memory", "value", "summary")


def _record_to_text(record: Any) -> str:
    """Render a single record as a one-line string."""
    if isinstance(record, str):
        return record.strip()
    if isinstance(record, Mapping):
        for key in _TEXT_KEYS:
            value = record.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()
        return ", ".join(f"{k}: {v}" for k, v in record.items())
    return str(record)


def _iter_records(results: Any) -> list[Any]:
    """Extract an iterable of records from a variety of result shapes."""
    if results is None:
        return []
    if isinstance(results, str):
        return [results] if results.strip() else []
    if isinstance(results, Mapping):
        for key in _RESULT_KEYS:
            if key in results:
                return _iter_records(results[key])
        return [results]
    if isinstance(results, Sequence):
        return list(results)
    return [results]


def format_results(results: Any) -> str:
    """Format Spectron results as a newline-separated list of bullet points.

    Returns an empty string when there is nothing to show.
    """
    records = _iter_records(results)
    lines = [text for record in records if (text := _record_to_text(record))]
    return "\n".join(f"- {line}" for line in lines)


__all__ = ["format_results"]
