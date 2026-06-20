from __future__ import annotations

import argparse
from pathlib import Path

try:
    from scripts.bootstrap import add_src_to_path
except ModuleNotFoundError:
    from bootstrap import add_src_to_path


ROOT = add_src_to_path()


def main() -> int:
    parser = argparse.ArgumentParser(description="Load master data CSV files into Databricks Delta tables.")
    parser.add_argument("--input-dir", required=True, help="Directory containing CSV files.")
    parser.add_argument("--catalog", required=True)
    parser.add_argument("--schema", required=True)
    parser.add_argument("--mode", default="overwrite", choices=["overwrite", "append"])
    args = parser.parse_args()

    if "spark" not in globals():
        raise RuntimeError("load_master_data.py must run in Databricks or another Spark environment.")

    for csv_path in Path(args.input_dir).glob("*.csv"):
        table_name = csv_path.stem
        target = f"`{args.catalog}`.`{args.schema}`.`{table_name}`"
        (
            spark.read.option("header", "true")
            .option("inferSchema", "true")
            .csv(str(csv_path))
            .write.mode(args.mode)
            .format("delta")
            .saveAsTable(target)
        )
        print(f"Loaded {csv_path} into {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
