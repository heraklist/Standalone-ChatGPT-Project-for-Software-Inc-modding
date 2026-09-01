from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
from zipfile import ZipFile


def _unsafe(name: str) -> bool:
    p = PurePosixPath(name.replace('\\', '/'))
    return p.is_absolute() or '..' in p.parts


def inspect_zip(path: Path) -> dict[str, object]:
    archive_bytes = path.read_bytes()
    files: list[dict[str, object]] = []
    unsafe_paths: list[str] = []
    compressed_total = 0
    uncompressed_total = 0

    with ZipFile(path) as zf:
        infos = sorted((i for i in zf.infolist() if not i.is_dir()), key=lambda i: i.filename.replace('\\', '/'))
        for info in infos:
            normalized = info.filename.replace('\\', '/')
            if _unsafe(normalized):
                unsafe_paths.append(normalized)
                continue
            data = zf.read(info)
            compressed_total += info.compress_size
            uncompressed_total += info.file_size
            files.append({
                'path': normalized,
                'compressed_bytes': info.compress_size,
                'uncompressed_bytes': info.file_size,
                'sha256': hashlib.sha256(data).hexdigest(),
            })

    return {
        'archive_sha256': hashlib.sha256(archive_bytes).hexdigest(),
        'file_count': len(files),
        'compressed_bytes': compressed_total,
        'uncompressed_bytes': uncompressed_total,
        'unsafe_paths': sorted(unsafe_paths),
        'files': files,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('zip_path', type=Path)
    parser.add_argument('--manifest', type=Path)
    args = parser.parse_args()
    result = inspect_zip(args.zip_path)
    text = json.dumps(result, indent=2, ensure_ascii=False, sort_keys=True) + '\n'
    if args.manifest:
        args.manifest.parent.mkdir(parents=True, exist_ok=True)
        args.manifest.write_text(text, encoding='utf-8')
    else:
        print(text, end='')
    return 1 if result['unsafe_paths'] else 0


if __name__ == '__main__':
    raise SystemExit(main())
