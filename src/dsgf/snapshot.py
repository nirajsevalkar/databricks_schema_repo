"""Load and save schema snapshots."""

from __future__ import annotations

from collections.abc import Iterable
from datetime import datetime, timezone
from pathlib import Path

from dsgf.hashing import ddl_hash
from dsgf.io import read_json, write_json
from dsgf.models import SchemaObject
from dsgf.versioning import initial_version


def load_snapshot(path: str | Path) -> list[SchemaObject]:
    data = read_json(path)
    return [SchemaObject(**item) for item in data["objects"]]


def write_snapshot(path: str | Path, objects: Iterable[SchemaObject], environment: str) -> None:
    write_json(
        path,
        {
            "environment": environment,
            "extracted_on": datetime.now(timezone.utc).isoformat(),
            "objects": [obj.to_dict() for obj in objects],
        },
    )


def object_from_ddl(
    *,
    object_name: str,
    object_type: str,
    catalog_name: str,
    schema_name: str,
    ddl_definition: str,
    environment: str,
    schema_version: str | None = None,
) -> SchemaObject:
    return SchemaObject(
        object_name=object_name,
        object_type=object_type,
        catalog_name=catalog_name,
        schema_name=schema_name,
        schema_hash=ddl_hash(ddl_definition),
        schema_version=schema_version or initial_version(),
        ddl_definition=ddl_definition,
        environment=environment,
    )

