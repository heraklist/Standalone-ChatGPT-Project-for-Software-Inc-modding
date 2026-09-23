from __future__ import annotations

import subprocess
from pathlib import Path, PurePosixPath


def _safe_repo_path(path: str) -> str:
    if not isinstance(path, str) or not path or "\x00" in path:
        raise ValueError("source path must be a non-empty repository-relative path")
    if "\\" in path:
        raise ValueError(f"source path uses ambiguous backslashes: {path!r}")
    if path.startswith("/") or (
        len(path) >= 2 and path[0].isalpha() and path[1] == ":"
    ):
        raise ValueError(f"source path must be repository-relative: {path!r}")
    parts = path.split("/")
    if any(part in {"", ".", ".."} for part in parts):
        raise ValueError(f"unsafe source path: {path!r}")
    normalized = PurePosixPath(path).as_posix()
    if normalized in {"", "."}:
        raise ValueError("source path must not be empty")
    return normalized


class GitSource:
    def __init__(self, repo_root: Path, source_sha: str):
        self.repo_root = Path(repo_root).resolve()
        if not isinstance(source_sha, str) or not source_sha or source_sha.startswith("-"):
            raise ValueError("source commit reference is invalid")
        self.source_sha = source_sha
        try:
            top = self._run_text("rev-parse", "--show-toplevel")
        except ValueError as exc:
            raise ValueError("source repository is not a valid Git repository") from exc
        if Path(top).resolve() != self.repo_root:
            raise ValueError("source repository root does not match Git toplevel")
        try:
            self._run_bytes("cat-file", "-e", f"{source_sha}^{{commit}}")
            full = self._run_text("rev-parse", "--verify", f"{source_sha}^{{commit}}")
        except ValueError as exc:
            raise ValueError(f"source reference does not resolve to a commit: {source_sha}") from exc
        if len(full) != 40 or any(ch not in "0123456789abcdefABCDEF" for ch in full):
            raise ValueError("resolved source commit is not a full SHA-1 commit id")
        self._full_commit = full.lower()

    def _run_bytes(self, *args: str) -> bytes:
        result = subprocess.run(
            ["git", "-C", str(self.repo_root), *args],
            capture_output=True,
            check=False,
        )
        if result.returncode != 0:
            detail = result.stderr.decode("utf-8", errors="replace").strip()
            raise ValueError(detail or f"git command failed: {' '.join(args)}")
        return result.stdout

    def _run_text(self, *args: str) -> str:
        return self._run_bytes(*args).decode("utf-8").strip()

    def full_commit(self) -> str:
        return self._full_commit

    def read_bytes(self, path: str) -> bytes:
        source_path = _safe_repo_path(path)
        try:
            return self._run_bytes("show", f"{self._full_commit}:{source_path}")
        except ValueError as exc:
            raise ValueError(f"source path is not readable at commit: {source_path}") from exc

    def list_files(self, prefix: str) -> tuple[str, ...]:
        safe_prefix = _safe_repo_path(prefix)
        try:
            output = self._run_text(
                "ls-tree",
                "-r",
                "--name-only",
                self._full_commit,
                "--",
                safe_prefix,
            )
        except ValueError as exc:
            raise ValueError(f"source prefix is not readable at commit: {safe_prefix}") from exc
        if not output:
            return ()
        files = []
        for line in output.splitlines():
            normalized = _safe_repo_path(line)
            if normalized == safe_prefix or normalized.startswith(safe_prefix + "/"):
                files.append(normalized)
        return tuple(sorted(files))
