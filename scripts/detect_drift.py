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
    parser.add_argument("--source", required=True, help="Source snapshot JSON, usually DEV or Git-approved.")
    parser.add_argument("--target", required=True, help="Target snapshot JSON, usually UAT or PROD.")
    parser.add_argument("--output", default="drift_report.json", help="Output drift report JSON.")
    parser.add_argument("--fail-on-drift", action="store_true", help="Exit with code 2 when drift exists.")
    args = parser.parse_args()

    source = load_snapshot(_resolve_path(args.source))
    target = load_snapshot(_resolve_path(args.target))
    drift = compare_snapshots(source, target)
    write_json(_resolve_path(args.output), {"drift_count": len(drift), "results": [item.to_dict() for item in drift]})

    print(f"Drift results written to {args.output}")
    print(f"Drift count: {len(drift)}")
    if drift and args.fail_on_drift:
        return 2
    return 0


def _resolve_path(path: str):
    candidate = Path(path)
    return candidate if candidate.is_absolute() else ROOT / candidate


if __name__ == "__main__":
    raise SystemExit(main())
