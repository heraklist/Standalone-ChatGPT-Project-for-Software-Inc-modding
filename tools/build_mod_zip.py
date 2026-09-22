from __future__ import annotations

import hashlib
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

from tools.safe_artifacts import assert_regular_file_within, safe_source_files

FIXED_ZIP_TIME = (1980, 1, 1, 0, 0, 0)


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def build_mod_zip(source_dir: Path, output_zip: Path) -> dict:
    source = Path(source_dir)
    source_resolved = source.resolve(strict=True)
    output = Path(output_zip).resolve()
    try:
        output.relative_to(source_resolved)
    except ValueError:
        pass
    else:
        raise ValueError("output ZIP must not be inside source tree")

    source_files = safe_source_files(source)
    files = [path.relative_to(source).as_posix() for path in source_files]

    output.parent.mkdir(parents=True, exist_ok=True)
    with ZipFile(output, "w", compression=ZIP_DEFLATED) as archive:
        for path, relative in zip(source_files, files, strict=True):
            assert_regular_file_within(source, path)
            info = ZipInfo(relative, FIXED_ZIP_TIME)
            info.compress_type = ZIP_DEFLATED
            info.create_system = 3
            info.external_attr = 0o100644 << 16
            archive.writestr(info, path.read_bytes())

    return {"files": files, "sha256": _sha256(output)}
