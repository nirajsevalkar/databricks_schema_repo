"""Stable DDL normalization and hashing."""

from __future__ import annotations

import hashlib
import re


_LINE_COMMENT = re.compile(r"--.*?$", re.MULTILINE)
_BLOCK_COMMENT = re.compile(r"/\*.*?\*/", re.DOTALL)
_WHITESPACE = re.compile(r"\s+")


def normalize_ddl(ddl: str) -> str:
    """Return a stable representation of DDL for comparisons."""
    without_comments = _BLOCK_COMMENT.sub(" ", ddl)
    without_comments = _LINE_COMMENT.sub(" ", without_comments)
    normalized = _WHITESPACE.sub(" ", without_comments).strip()
    return normalized.rstrip(";").lower()


def ddl_hash(ddl: str) -> str:
    """Return a SHA256 hash for normalized DDL."""
    return hashlib.sha256(normalize_ddl(ddl).encode("utf-8")).hexdigest()

