"""JSON and filesystem helpers."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def read_json(path: str | Path) -> Any:
    with Path(path).open("r", encoding="utf-8") as handle:
        return json.load(handle)


def write_json(path: str | Path, data: Any) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("w", encoding="utf-8") as handle:
        json.dump(data, handle, indent=2, sort_keys=True)
        handle.write("\n")


def safe_object_path(root: str | Path, catalog: str, schema: str, object_name: str) -> Path:
    filename = f"{object_name}.sql".replace("/", "_").replace("\\", "_")
    return Path(root) / catalog / schema / filename

