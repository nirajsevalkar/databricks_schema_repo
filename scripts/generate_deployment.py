from __future__ import annotations

import argparse

try:
    from scripts.bootstrap import add_src_to_path
except ModuleNotFoundError:
    from bootstrap import add_src_to_path


ROOT = add_src_to_path()

from dsgf.deployment import generate_package
from dsgf.snapshot import load_snapshot


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate a schema deployment package.")
    parser.add_argument("--source", required=True, help="Source snapshot JSON.")
    parser.add_argument("--target", required=True, help="Target snapshot JSON.")
    parser.add_argument("--release-id", required=True, help="Release folder name.")
    parser.add_argument("--output-dir", default="deployments", help="Deployment output directory.")
    args = parser.parse_args()

    package_dir = generate_package(
        source_objects=load_snapshot(args.source),
        target_objects=load_snapshot(args.target),
        release_id=args.release_id,
        output_dir=args.output_dir,
    )
    print(f"Deployment package generated: {package_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
