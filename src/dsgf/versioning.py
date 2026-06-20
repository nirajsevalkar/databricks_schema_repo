"""Schema object version helpers."""

from __future__ import annotations


def initial_version() -> str:
    return "1.0.0"


def bump_minor(version: str) -> str:
    major, minor, patch = _parse(version)
    return f"{major}.{minor + 1}.{patch}"


def bump_major(version: str) -> str:
    major, _minor, _patch = _parse(version)
    return f"{major + 1}.0.0"


def bump_patch(version: str) -> str:
    major, minor, patch = _parse(version)
    return f"{major}.{minor}.{patch + 1}"


def _parse(version: str) -> tuple[int, int, int]:
    parts = version.split(".")
    if len(parts) != 3:
        raise ValueError(f"Invalid semantic version: {version}")
    return int(parts[0]), int(parts[1]), int(parts[2])

