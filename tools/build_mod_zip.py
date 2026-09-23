from __future__ import annotations

import hashlib
import stat
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

from tools.safe_artifacts import (
    assert_regular_file_within,
    safe_source_files,
    validate_archive_names,
)

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

    output_path = Path(output_zip)
    if output_path.exists() or output_path.is_symlink():
        metadata = output_path.lstat()
        reparse_flag = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0)
        attributes = getattr(metadata, "st_file_attributes", 0)
        if (
            stat.S_ISLNK(metadata.st_mode)
            or bool(reparse_flag and attributes & reparse_flag)
            or not stat.S_ISREG(metadata.st_mode)
        ):
            raise ValueError("output path must be a regular file, not a symlink or special file")
    output = output_path.resolve()
    try:
        output.relative_to(source_resolved)
    except ValueError:
        pass
    else:
        raise ValueError("output ZIP must not be inside source tree")

    source_files = safe_source_files(source)
    files = validate_archive_names(
        [path.relative_to(source).as_posix() for path in source_files],
        windows_casefold=True,
    )

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
