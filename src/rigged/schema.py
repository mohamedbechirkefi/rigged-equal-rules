# SPDX-License-Identifier: LicenseRef-RIGGED-NC-Research-1.0
"""Versioned JSON schemas; validation at export and import (fail closed)."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

import jsonschema

_DIR = Path(__file__).parent / "schemas"
SCHEMAS = {"rigged.result_bundle": "result_bundle-1.0.0.json", "rigged.run_manifest": "run_manifest-1.0.0.json"}


class SchemaError(ValueError):
    """Raised when a document fails validation."""


@lru_cache(maxsize=None)
def load_schema(name: str) -> dict:
    if name not in SCHEMAS:
        raise SchemaError(f"unknown schema {name!r}")
    return json.loads((_DIR / SCHEMAS[name]).read_text(encoding="utf-8"))


def validate(doc: dict, name: str) -> None:
    schema = load_schema(name)
    validator = jsonschema.Draft202012Validator(schema)
    errors = sorted(validator.iter_errors(doc), key=lambda e: list(e.absolute_path))
    if errors:
        e = errors[0]
        loc = "/".join(str(p) for p in e.absolute_path)
        raise SchemaError(f"{name}: {len(errors)} validation error(s); first at '{loc}': {e.message}")


def dump(doc: dict, name: str, path: Path) -> str:
    """Validate, then write canonical JSON; returns the SHA-256 hex digest of the bytes written."""
    import hashlib

    validate(doc, name)
    text = json.dumps(doc, indent=1, sort_keys=True, allow_nan=False) + "\n"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def load(path: Path, name: str) -> dict:
    """Read and validate; raises SchemaError on malformed or invalid input."""
    try:
        doc = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SchemaError(f"cannot read {path}: {exc}") from exc
    validate(doc, name)
    return doc
