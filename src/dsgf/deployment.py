"""Deployment package generation."""

from __future__ import annotations

from collections.abc import Iterable
from datetime import datetime, timezone
from pathlib import Path

from dsgf.compare import compare_snapshots, snapshot_index
from dsgf.io import write_json
from dsgf.models import DriftResult, SchemaObject


def generate_package(
    *,
    source_objects: Iterable[SchemaObject],
    target_objects: Iterable[SchemaObject],
    release_id: str,
    output_dir: str | Path,
) -> Path:
    source_list = list(source_objects)
    target_list = list(target_objects)
    drift = compare_snapshots(source_list, target_list)
    source = snapshot_index(source_list)
    package_dir = Path(output_dir) / release_id
    package_dir.mkdir(parents=True, exist_ok=True)

    _write_deployment_sql(package_dir / "deployment.sql", drift, source)
    _write_rollback_sql(package_dir / "rollback.sql", drift)
    _write_release_notes(package_dir / "release_notes.html", release_id, drift)
    write_json(
        package_dir / "schema_changes.json",
        {
            "release_id": release_id,
            "generated_on": datetime.now(timezone.utc).isoformat(),
            "changes": [item.to_dict() for item in drift],
        },
    )
    return package_dir


def _write_deployment_sql(
    path: Path,
    drift: Iterable[DriftResult],
    source: dict[str, SchemaObject],
) -> None:
    lines = [
        "-- Generated deployment script",
        "-- Review before executing in UAT or PROD.",
        "",
    ]
    for item in drift:
        lines.append(f"-- {item.status}: {item.qualified_name}")
        if item.status in {"MISSING_IN_TARGET", "HASH_MISMATCH"}:
            lines.append(source[item.qualified_name].ddl_definition.rstrip(";") + ";")
        elif item.status == "EXTRA_IN_TARGET":
            lines.append(f"-- Manual review required: target has extra object {item.qualified_name}.")
        lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def _write_rollback_sql(path: Path, drift: Iterable[DriftResult]) -> None:
    lines = [
        "-- Generated rollback placeholder",
        "-- Fill with approved reverse operations before production deployment.",
        "",
    ]
    for item in drift:
        lines.append(f"-- Rollback required for {item.status}: {item.qualified_name}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_release_notes(path: Path, release_id: str, drift: Iterable[DriftResult]) -> None:
    rows = "\n".join(
        f"<tr><td>{item.qualified_name}</td><td>{item.status}</td>"
        f"<td>{item.source_version or ''}</td><td>{item.target_version or ''}</td></tr>"
        for item in drift
    )
    html = f"""<!doctype html>
<html>
<head><meta charset="utf-8"><title>{release_id}</title></head>
<body>
<h1>{release_id}</h1>
<table border="1" cellspacing="0" cellpadding="6">
<thead><tr><th>Object</th><th>Status</th><th>Source Version</th><th>Target Version</th></tr></thead>
<tbody>
{rows}
</tbody>
</table>
</body>
</html>
"""
    path.write_text(html, encoding="utf-8")

