"""Measure the unchanged CDnow source file for a reproducible manifest."""

import argparse
import hashlib
import json
from pathlib import Path

SOURCE_RELATIVE_PATH = Path("CDNOW_data/CDNOW_master.txt")
MANIFEST_RELATIVE_PATH = Path("docs/source_manifest.json")
REPOSITORY_ROOT = Path(__file__).resolve().parent.parent


def measure_source(path: Path) -> dict[str, int | str]:
    """Return byte size, physical line count, and SHA-256 of a file."""
    digest = hashlib.sha256()
    byte_size = 0
    line_count = 0
    with path.open("rb") as source:
        for line in source:
            digest.update(line)
            byte_size += len(line)
            line_count += 1
    return {
        "path": SOURCE_RELATIVE_PATH.as_posix(),
        "size_bytes": byte_size,
        "line_count": line_count,
        "sha256": digest.hexdigest(),
    }


def main() -> None:
    """Print current measurements or check them against the saved manifest."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check", action="store_true", help="compare with the saved manifest"
    )
    args = parser.parse_args()

    current = measure_source(REPOSITORY_ROOT / SOURCE_RELATIVE_PATH)
    if args.check:
        saved_path = REPOSITORY_ROOT / MANIFEST_RELATIVE_PATH
        saved = json.loads(saved_path.read_text(encoding="utf-8"))
        if current != saved:
            raise SystemExit("Source file does not match docs/source_manifest.json")
        print("Source file matches docs/source_manifest.json")
    else:
        print(json.dumps(current, indent=2))


if __name__ == "__main__":
    main()
