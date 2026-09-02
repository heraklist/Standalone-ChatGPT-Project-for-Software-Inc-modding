from __future__ import annotations

import hashlib
from pathlib import Path
import zipfile


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def build_mod_zip(source_dir: Path, output_zip: Path) -> dict:
    source = source_dir.resolve()
    output = output_zip.resolve()
    try:
        output.relative_to(source)
    except ValueError:
        pass
    else:
        raise ValueError("output ZIP must not be inside source tree")

    files = sorted(
        path.relative_to(source).as_posix()
        for path in source.rglob("*")
        if path.is_file()
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for relative in files:
            archive.write(source / relative, arcname=relative)

    return {"files": files, "sha256": _sha256(output)}
