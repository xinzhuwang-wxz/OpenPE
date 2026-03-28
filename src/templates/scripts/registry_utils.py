# Copyright 2026 OpenPE Contributors — Licensed under GPL-3.0
# Modified by Maxen Wong, 2026

"""Data registry utilities for OpenPE data provenance tracking."""
import hashlib
import yaml
from pathlib import Path
from datetime import datetime


def compute_hash(filepath: Path) -> str:
    """Compute SHA-256 hash of a file."""
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def register_dataset(
    registry_path: Path,
    source_id: str,
    name: str,
    url: str,
    filepath: Path,
    query_params: dict | None = None,
    notes: str = "",
) -> dict:
    """Register a downloaded dataset in registry.yaml."""
    entry = {
        "source_id": source_id,
        "name": name,
        "url": url,
        "retrieved": datetime.now().isoformat(),
        "file": str(filepath),
        "sha256": compute_hash(filepath),
        "query_params": query_params or {},
        "notes": notes,
    }
    if registry_path.exists():
        with open(registry_path) as f:
            registry = yaml.safe_load(f) or {"datasets": []}
    else:
        registry = {"datasets": []}
    registry["datasets"].append(entry)
    with open(registry_path, "w") as f:
        yaml.dump(registry, f, default_flow_style=False, sort_keys=False)
    return entry
