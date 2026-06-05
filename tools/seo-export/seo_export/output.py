"""CSV/JSON writers for exported report rows.

All reports write to ``tools/seo-export/exports/YYYY-MM-DD/<report>.<ext>`` unless an
explicit output directory is given. CSV is the default format; ``--format json``
writes a JSON array with the same normalized keys.
"""

from __future__ import annotations

import csv
import json
from datetime import date
from pathlib import Path
from typing import Optional, Sequence

# tools/seo-export/exports/
DEFAULT_EXPORTS_ROOT = Path(__file__).resolve().parent.parent / "exports"


def dated_output_dir(root: Optional[Path] = None) -> Path:
    """Return (and create) the dated output directory for today's run."""
    out = (root or DEFAULT_EXPORTS_ROOT) / date.today().isoformat()
    out.mkdir(parents=True, exist_ok=True)
    return out


def write_rows(
    rows: list[dict],
    report_name: str,
    *,
    fmt: str = "csv",
    out_dir: Optional[Path] = None,
    columns: Optional[Sequence[str]] = None,
) -> Path:
    """Write report rows to a dated CSV or JSON file and return the path.

    Args:
        rows: Normalized report rows. May be empty (an empty file with headers is
            still written so downstream tooling sees a stable schema).
        report_name: Base filename without extension (e.g. "gsc-queries").
        fmt: "csv" (default) or "json".
        out_dir: Override output directory; defaults to exports/YYYY-MM-DD/.
        columns: Explicit column order for CSV; defaults to the first row's keys.
    """
    target_dir = out_dir or dated_output_dir()
    target_dir.mkdir(parents=True, exist_ok=True)

    if fmt == "json":
        path = target_dir / f"{report_name}.json"
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(rows, fh, indent=2, ensure_ascii=False)
            fh.write("\n")
        return path

    if fmt != "csv":
        raise ValueError(f"Unsupported format: {fmt!r} (expected 'csv' or 'json')")

    fieldnames = list(columns) if columns else (list(rows[0].keys()) if rows else [])
    path = target_dir / f"{report_name}.csv"
    with open(path, "w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames, extrasaction="ignore")
        if fieldnames:
            writer.writeheader()
        for row in rows:
            writer.writerow(row)
    return path
