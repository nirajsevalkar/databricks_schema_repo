from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

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

    source = load_snapshot(args.source)
    target = load_snapshot(args.target)
    drift = compare_snapshots(source, target)
    write_json(args.output, {"drift_count": len(drift), "results": [item.to_dict() for item in drift]})

    print(f"Drift results written to {args.output}")
    print(f"Drift count: {len(drift)}")
    if drift and args.fail_on_drift:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

