from __future__ import annotations

import sys
from pathlib import Path


def add_src_to_path() -> Path:
    """Add repository src directory to sys.path for local and Databricks runs."""
    if "__file__" in globals():
        root = Path(__file__).resolve().parents[1]
    else:
        root = Path.cwd()

    src_path = root / "src"
    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))
    return root

