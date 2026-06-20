from __future__ import annotations

import argparse
import re
from datetime import datetime, timezone
from pathlib import Path

try:
    from scripts.bootstrap import add_src_to_path
except ModuleNotFoundError:
    from bootstrap import add_src_to_path


ROOT = add_src_to_path()

from dsgf.hashing import ddl_hash
from dsgf.io import read_json, safe_object_path, write_json
from dsgf.models import SchemaObject
from dsgf.snapshot import write_snapshot
from dsgf.versioning import bump_minor, initial_version


def main() -> int:
    parser = argparse.ArgumentParser(description="Export Databricks schemas into registry and Git files.")
    parser.add_argument("--environment", default=None, help="Environment name, such as DEV, UAT, or PROD.")
    parser.add_argument("--config", default="config/environments.example.json", help="Environment config JSON.")
    parser.add_argument("--snapshot-output", default=None, help="Optional local snapshot JSON output.")
    args, _unknown = parser.parse_known_args()

    if "spark" not in globals():
        raise RuntimeError("schema_export.py must run in Databricks or another Spark environment.")

    run_config = _resolve_runtime_args(args)
    config = read_json(run_config["config"])
    objects = export_environment(spark, config, run_config["environment"])
    write_registry(spark, config, objects)
    export_git_files(config["git_export_root"], objects)

    if run_config["snapshot_output"]:
        write_snapshot(run_config["snapshot_output"], objects, run_config["environment"])

    print(f"Exported {len(objects)} objects for {run_config['environment']}")
    return 0


def _resolve_runtime_args(args: argparse.Namespace) -> dict[str, str | None]:
    environment = args.environment or _get_widget_value("environment")
    config = args.config or _get_widget_value("config") or _get_widget_value("config_path")
    snapshot_output = args.snapshot_output or _get_widget_value("snapshot_output")

    if not environment:
        raise ValueError(
            "Missing environment. Pass --environment DEV or create a Databricks widget named environment."
        )

    return {
        "environment": environment,
        "config": config or "config/environments.example.json",
        "snapshot_output": snapshot_output,
    }


def _get_widget_value(name: str) -> str | None:
    if "dbutils" not in globals():
        return None
    try:
        value = dbutils.widgets.get(name)
    except Exception:
        return None
    return value or None


def export_environment(spark_session, config: dict, environment: str) -> list[SchemaObject]:
    env_config = config["environments"][environment]
    exclude_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in config.get("exclude_object_patterns", [])]
    objects: list[SchemaObject] = []

    for catalog in env_config["catalogs"]:
        for schema in env_config["schemas"]:
            tables = [
                (row["tableName"], "TABLE")
                for row in spark_session.sql(f"SHOW TABLES IN `{catalog}`.`{schema}`").collect()
                if not bool(row["isTemporary"])
            ]
            views = [
                (row["viewName"], "VIEW")
                for row in spark_session.sql(f"SHOW VIEWS IN `{catalog}`.`{schema}`").collect()
                if not bool(row["isTemporary"])
            ]
            for object_name, object_type in tables + views:
                if any(pattern.search(object_name) for pattern in exclude_patterns):
                    continue
                objects.append(
                    _build_schema_object(
                        spark_session,
                        config,
                        environment,
                        catalog,
                        schema,
                        object_name,
                        object_type,
                    )
                )
    return objects


def _build_schema_object(
    spark_session,
    config: dict,
    environment: str,
    catalog: str,
    schema: str,
    object_name: str,
    object_type: str,
) -> SchemaObject:
    ddl = _show_create(spark_session, catalog, schema, object_name)
    previous_version = _latest_version(spark_session, config, environment, catalog, schema, object_name)
    schema_hash = ddl_hash(ddl)
    schema_version = previous_version or initial_version()
    if previous_version and _latest_hash(spark_session, config, environment, catalog, schema, object_name) != schema_hash:
        schema_version = bump_minor(previous_version)
    return SchemaObject(
        object_name=object_name,
        object_type=object_type,
        catalog_name=catalog,
        schema_name=schema,
        schema_hash=schema_hash,
        schema_version=schema_version,
        ddl_definition=ddl,
        environment=environment,
    )


def write_registry(spark_session, config: dict, objects: list[SchemaObject]) -> None:
    if not objects:
        return
    table_name = _registry_table(config)
    rows = [
        {
            **obj.to_dict(),
            "extracted_on": datetime.now(timezone.utc),
        }
        for obj in objects
    ]
    spark_session.createDataFrame(rows).write.mode("append").format("delta").saveAsTable(table_name)


def export_git_files(root: str, objects: list[SchemaObject]) -> None:
    manifest = []
    for obj in objects:
        path = safe_object_path(root, obj.catalog_name, obj.schema_name, obj.object_name)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(obj.ddl_definition.rstrip() + "\n", encoding="utf-8")
        manifest.append(obj.to_dict())
    write_json(Path(root) / "schema_manifest.json", {"objects": manifest})


def _show_create(spark_session, catalog: str, schema: str, object_name: str) -> str:
    qualified = f"`{catalog}`.`{schema}`.`{object_name}`"
    rows = spark_session.sql(f"SHOW CREATE TABLE {qualified}").collect()
    return rows[0][0]


def _registry_table(config: dict) -> str:
    catalog = config.get("metadata_catalog", "platform_metadata")
    schema = config.get("metadata_schema", "default")
    return f"`{catalog}`.`{schema}`.`schema_registry`"


def _latest_version(spark_session, config: dict, environment: str, catalog: str, schema: str, object_name: str) -> str | None:
    row = _latest_registry_row(spark_session, config, environment, catalog, schema, object_name)
    return None if row is None else row["schema_version"]


def _latest_hash(spark_session, config: dict, environment: str, catalog: str, schema: str, object_name: str) -> str | None:
    row = _latest_registry_row(spark_session, config, environment, catalog, schema, object_name)
    return None if row is None else row["schema_hash"]


def _latest_registry_row(spark_session, config: dict, environment: str, catalog: str, schema: str, object_name: str):
    table_name = _registry_table(config)
    query = f"""
      SELECT schema_hash, schema_version
      FROM {table_name}
      WHERE environment = '{environment}'
        AND catalog_name = '{catalog}'
        AND schema_name = '{schema}'
        AND object_name = '{object_name}'
      ORDER BY extracted_on DESC
      LIMIT 1
    """
    rows = spark_session.sql(query).collect()
    return rows[0] if rows else None


if __name__ == "__main__":
    raise SystemExit(main())
