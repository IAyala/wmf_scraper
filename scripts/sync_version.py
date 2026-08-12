#!/usr/bin/env python3
"""Copy the project version from pyproject.toml into frontend/package.json.

pyproject.toml is the single source of truth for the version. `uv version`
maintains it; this script keeps the frontend package manifest in step so the
two never disagree. Run via `make bump-patch` and friends.
"""

import json
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PYPROJECT = ROOT / "pyproject.toml"
PACKAGE_JSON = ROOT / "frontend" / "package.json"
PACKAGE_LOCK = ROOT / "frontend" / "package-lock.json"


def project_version() -> str:
    with PYPROJECT.open("rb") as handle:
        return tomllib.load(handle)["project"]["version"]


def write_json_version(path: Path, version: str, *, top_level_only: bool = False) -> bool:
    if not path.is_file():
        return False
    data = json.loads(path.read_text())
    changed = data.get("version") != version
    data["version"] = version
    # package-lock.json repeats the version for the root package.
    if not top_level_only:
        root_package = data.get("packages", {}).get("")
        if isinstance(root_package, dict):
            changed = changed or root_package.get("version") != version
            root_package["version"] = version
    if changed:
        path.write_text(json.dumps(data, indent=2) + "\n")
    return changed


def main() -> int:
    version = project_version()
    touched = [
        path.relative_to(ROOT)
        for path, top_level_only in ((PACKAGE_JSON, True), (PACKAGE_LOCK, False))
        if write_json_version(path, version, top_level_only=top_level_only)
    ]
    if touched:
        print(f"Version {version} written to {', '.join(str(p) for p in touched)}")
    else:
        print(f"Version {version} already in sync")
    return 0


if __name__ == "__main__":
    sys.exit(main())
