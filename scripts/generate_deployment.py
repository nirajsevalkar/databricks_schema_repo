from __future__ import annotations

import argparse
from pathlib import Path

try:
    from scripts.bootstrap import add_src_to_path
except ModuleNotFoundError:
    from bootstrap import add_src_to_path


ROOT = add_src_to_path()

from dsgf.deployment import generate_package
from dsgf.snapshot import load_snapshot


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate a schema deployment package.")
    parser.add_argument("--source", default=None, help="Source snapshot JSON.")
    parser.add_argument("--target", default=None, help="Target snapshot JSON.")
    parser.add_argument("--release-id", default=None, help="Release folder name.")
    parser.add_argument("--output-dir", default="deployments", help="Deployment output directory.")
    args, _unknown = parser.parse_known_args()

    run_config = _resolve_runtime_args(args)
    package_dir = generate_package(
        source_objects=load_snapshot(_resolve_path(run_config["source"])),
        target_objects=load_snapshot(_resolve_path(run_config["target"])),
        release_id=run_config["release_id"],
        output_dir=_resolve_path(run_config["output_dir"]),
    )
    print(f"Deployment package generated: {package_dir}")
    return 0


def _resolve_runtime_args(args: argparse.Namespace) -> dict[str, str]:
    source = args.source or _get_widget_value("source")
    target = args.target or _get_widget_value("target")
    release_id = args.release_id or _get_widget_value("release_id")
    output_dir = args.output_dir or _get_widget_value("output_dir") or "deployments"

    missing = []
    if not source:
        missing.append("source")
    if not target:
        missing.append("target")
    if not release_id:
        missing.append("release_id")
    if missing:
        names = ", ".join(missing)
        raise ValueError(f"Missing {names}. Pass CLI args or create matching Databricks widgets.")

    return {
        "source": source,
        "target": target,
        "release_id": release_id,
        "output_dir": output_dir,
    }


def _get_widget_value(name: str) -> str | None:
    if "dbutils" not in globals():
        return None
    try:
        value = dbutils.widgets.get(name)
    except Exception:
        return None
    return value or None


def _resolve_path(path: str):
    candidate = Path(path)
    return candidate if candidate.is_absolute() else ROOT / candidate


if __name__ == "__main__":
    raise SystemExit(main())
