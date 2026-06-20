"""Shared dataclasses for schema governance operations."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True)
class SchemaObject:
    object_name: str
    object_type: str
    catalog_name: str
    schema_name: str
    schema_hash: str
    schema_version: str
    ddl_definition: str
    environment: str

    @property
    def qualified_name(self) -> str:
        return f"{self.catalog_name}.{self.schema_name}.{self.object_name}"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class DriftResult:
    qualified_name: str
    status: str
    source_hash: str | None
    target_hash: str | None
    source_version: str | None
    target_version: str | None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

