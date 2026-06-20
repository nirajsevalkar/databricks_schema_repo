"""Compare schema snapshots across environments."""

from __future__ import annotations

from collections.abc import Iterable

from dsgf.models import DriftResult, SchemaObject


def snapshot_index(objects: Iterable[SchemaObject]) -> dict[str, SchemaObject]:
    return {obj.qualified_name: obj for obj in objects}


def compare_snapshots(
    source_objects: Iterable[SchemaObject],
    target_objects: Iterable[SchemaObject],
) -> list[DriftResult]:
    source = snapshot_index(source_objects)
    target = snapshot_index(target_objects)
    results: list[DriftResult] = []

    for name in sorted(source.keys() - target.keys()):
        src = source[name]
        results.append(
            DriftResult(name, "MISSING_IN_TARGET", src.schema_hash, None, src.schema_version, None)
        )

    for name in sorted(target.keys() - source.keys()):
        tgt = target[name]
        results.append(
            DriftResult(name, "EXTRA_IN_TARGET", None, tgt.schema_hash, None, tgt.schema_version)
        )

    for name in sorted(source.keys() & target.keys()):
        src = source[name]
        tgt = target[name]
        if src.schema_hash != tgt.schema_hash:
            results.append(
                DriftResult(
                    name,
                    "HASH_MISMATCH",
                    src.schema_hash,
                    tgt.schema_hash,
                    src.schema_version,
                    tgt.schema_version,
                )
            )

    return results


def has_drift(results: Iterable[DriftResult]) -> bool:
    return any(result.status != "MATCH" for result in results)

