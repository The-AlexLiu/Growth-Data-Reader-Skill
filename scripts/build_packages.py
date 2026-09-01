#!/usr/bin/env python3
import hashlib
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
VERSION = "1.0.0"


def add_tree(archive: zipfile.ZipFile, source: Path, prefix: str = "") -> None:
    for path in sorted(source.rglob("*")):
        if path.is_dir() or "__pycache__" in path.parts or path.suffix == ".pyc":
            continue
        archive.write(path, Path(prefix) / path.relative_to(source))


def build() -> list[Path]:
    DIST.mkdir(exist_ok=True)
    aily = DIST / f"growth-data-reader-aily-v{VERSION}.skill"
    workbuddy = DIST / f"growth-data-reader-workbuddy-v{VERSION}.zip"
    with zipfile.ZipFile(aily, "w", zipfile.ZIP_DEFLATED) as archive:
        add_tree(archive, ROOT / "skills/growth-data-reader-aily", "growth-data-reader-aily")
    with zipfile.ZipFile(workbuddy, "w", zipfile.ZIP_DEFLATED) as archive:
        add_tree(archive, ROOT / "skills/growth-data-reader-workbuddy")
    sums = DIST / "SHA256SUMS.txt"
    sums.write_text(
        "".join(
            f"{hashlib.sha256(path.read_bytes()).hexdigest()}  {path.name}\n"
            for path in (aily, workbuddy)
        ),
        encoding="ascii",
    )
    return [aily, workbuddy, sums]


if __name__ == "__main__":
    for artifact in build():
        print(artifact.relative_to(ROOT))
