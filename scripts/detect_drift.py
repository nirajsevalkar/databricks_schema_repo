from __future__ import annotations

import argparse
from pathlib import Path

try:
    from scripts.bootstrap import add_src_to_path
except ModuleNotFoundError:
    from bootstrap import add_src_to_path


ROOT = add_src_to_path()

from dsgf.compare import compare_snapshots
from dsgf.io import write_json
from dsgf.snapshot import load_snapshot


def main() -> int:
    parser = argparse.ArgumentParser(description="Detect schema drift between two snapshots.")
    parser.add_argument("--source", default=None, help="Source snapshot JSON, usually DEV or Git-approved.")
    parser.add_argument("--target", default=None, help="Target snapshot JSON, usually UAT or PROD.")
    parser.add_argument("--output", default="drift_report.json", help="Output drift report JSON.")
    parser.add_argument("--fail-on-drift", action="store_true", help="Exit with code 2 when drift exists.")
    args, _unknown = parser.parse_known_args()

    run_config = _resolve_runtime_args(args)
    source = load_snapshot(_resolve_path(run_config["source"]))
    target = load_snapshot(_resolve_path(run_config["target"]))
    drift = compare_snapshots(source, target)
    write_json(_resolve_path(run_config["output"]), {"drift_count": len(drift), "results": [item.to_dict() for item in drift]})

    print(f"Drift results written to {run_config['output']}")
    print(f"Drift count: {len(drift)}")
    if drift and run_config["fail_on_drift"]:
        return 2
    return 0


def _resolve_runtime_args(args: argparse.Namespace) -> dict[str, str | bool]:
    source = args.source or _get_widget_value("source")
    target = args.target or _get_widget_value("target")
    output = args.output or _get_widget_value("output") or "drift_report.json"
    fail_on_drift = args.fail_on_drift or _get_bool_widget_value("fail_on_drift")

    missing = []
    if not source:
        missing.append("source")
    if not target:
        missing.append("target")
    if missing:
        names = ", ".join(missing)
        raise ValueError(f"Missing {names}. Pass CLI args or create Databricks widgets named source and target.")

    return {
        "source": source,
        "target": target,
        "output": output,
        "fail_on_drift": fail_on_drift,
    }


def _get_widget_value(name: str) -> str | None:
    if "dbutils" not in globals():
        return None
    try:
        value = dbutils.widgets.get(name)
    except Exception:
        return None
    return value or None


def _get_bool_widget_value(name: str) -> bool:
    value = _get_widget_value(name)
    return str(value).strip().lower() in {"1", "true", "yes", "y"}


def _resolve_path(path: str):
    candidate = Path(path)
    return candidate if candidate.is_absolute() else ROOT / candidate


if __name__ == "__main__":
    raise SystemExit(main())
