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
    parser.add_argument("--input-dir", default=None, help="Directory containing CSV files.")
    parser.add_argument("--catalog", default=None)
    parser.add_argument("--schema", default=None)
    parser.add_argument("--mode", default="overwrite", choices=["overwrite", "append"])
    args, _unknown = parser.parse_known_args()

    if "spark" not in globals():
        raise RuntimeError("load_master_data.py must run in Databricks or another Spark environment.")

    run_config = _resolve_runtime_args(args)
    spark.sql(f"USE CATALOG `{run_config['catalog']}`")

    for csv_path in _resolve_path(run_config["input_dir"]).glob("*.csv"):
        table_name = csv_path.stem
        target = f"`{run_config['schema']}`.`{table_name}`"
        (
            spark.read.option("header", "true")
            .option("inferSchema", "true")
            .csv(str(csv_path))
            .write.mode(run_config["mode"])
            .format("delta")
            .saveAsTable(target)
        )
        print(f"Loaded {csv_path} into {target}")
    return 0


def _resolve_runtime_args(args: argparse.Namespace) -> dict[str, str]:
    input_dir = args.input_dir or _get_widget_value("input_dir")
    catalog = args.catalog or _get_widget_value("catalog")
    schema = args.schema or _get_widget_value("schema")
    mode = args.mode or _get_widget_value("mode") or "overwrite"

    missing = []
    if not input_dir:
        missing.append("input_dir")
    if not catalog:
        missing.append("catalog")
    if not schema:
        missing.append("schema")
    if missing:
        names = ", ".join(missing)
        raise ValueError(f"Missing {names}. Pass CLI args or create matching Databricks widgets.")

    if mode not in {"overwrite", "append"}:
        raise ValueError("mode must be overwrite or append.")

    return {
        "input_dir": input_dir,
        "catalog": catalog,
        "schema": schema,
        "mode": mode,
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
