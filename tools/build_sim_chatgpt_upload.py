from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

ROOT = Path(__file__).resolve().parents[1]
FIXED_ZIP_TIME = (1980, 1, 1, 0, 0, 0)


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _sha256_file(path: Path) -> str:
    return _sha256_bytes(path.read_bytes())


def _internal_reference_path(relative: Path) -> str:
    parts = relative.parts
    if len(parts) != 3 or parts[2] != "SKILL.md" or parts[0] not in {"domains", "lifecycle"}:
        raise RuntimeError(f"unexpected internal SIM skill path: {relative.as_posix()}")
    return f"references/internal/{parts[0]}/{parts[1]}.md"


def build_chatgpt_upload(root: Path, out_dir: Path | None = None) -> tuple[Path, dict]:
    sim_root = root / "production/sim"
    manifest = json.loads((sim_root / "manifests/sim-manifest.json").read_text(encoding="utf-8"))
    capabilities = json.loads(
        (sim_root / "manifests/tool-capabilities.json").read_text(encoding="utf-8")
    )
    version = manifest["version"]
    if version != "0.2.0-preview":
        raise RuntimeError("unexpected SIM Preview version")

    root_skill = (sim_root / "SKILL.md").read_text(encoding="utf-8")
    payload: dict[str, bytes] = {}
    internal_refs: list[str] = []

    for source in sorted(path for path in sim_root.rglob("*") if path.is_file()):
        relative = source.relative_to(sim_root)
        if relative.as_posix() == "SKILL.md":
            continue
        if relative.name == "SKILL.md" and relative.parts[0] in {"domains", "lifecycle"}:
            target = _internal_reference_path(relative)
            internal_refs.append(target)
            payload[target] = source.read_bytes()
            continue
        payload[relative.as_posix()] = source.read_bytes()

    chatgpt_tools: dict[str, dict] = {}
    for tool_name, tool in sorted(capabilities.get("tools", {}).items()):
        surface = tool.get("surfaces", {}).get("ChatGPT", {})
        if not surface.get("bundled", False):
            continue
        repository_source = root / tool["repository_source"]
        if not repository_source.is_file():
            raise RuntimeError(f"missing bundled SIM tool source: {tool['repository_source']}")
        package_path = tool["package_path"]
        if package_path.startswith("/") or ".." in Path(package_path).parts:
            raise RuntimeError(f"unsafe bundled SIM tool package path: {package_path}")
        payload[package_path] = repository_source.read_bytes()
        chatgpt_tools[tool_name] = {
            "bundled": True,
            "execution": surface["execution"],
            "package_path": package_path,
            "sha256": _sha256_file(repository_source),
        }

    appendix = [
        "",
        "## Bundled internal workflow references",
        "",
        "The following files are internal orchestration references, not public peer skills. Read only the relevant file when routing requires it; the root SIM orchestrator remains the sole public skill and session owner.",
        "",
    ]
    appendix.extend(f"- `{path}`" for path in sorted(internal_refs))
    payload["SKILL.md"] = (root_skill.rstrip() + "\n" + "\n".join(appendix) + "\n").encode("utf-8")

    nested_public = [name for name in payload if name.endswith("SKILL.md") and name != "SKILL.md"]
    if nested_public:
        raise RuntimeError("ChatGPT upload would expose nested public skills: " + ", ".join(nested_public))

    output = out_dir or (root / "dist")
    output.mkdir(parents=True, exist_ok=True)
    zip_path = output / f"sim-{version}-chatgpt-upload.zip"
    with ZipFile(zip_path, "w", compression=ZIP_DEFLATED) as archive:
        for name, data in sorted(payload.items()):
            info = ZipInfo(name, FIXED_ZIP_TIME)
            info.compress_type = ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, data)

    report = {
        "sim_version": version,
        "surface": "ChatGPT",
        "source_layout": "production/sim",
        "public_skill_entries": ["SKILL.md"],
        "internal_reference_entries": sorted(internal_refs),
        "tool_capabilities": chatgpt_tools,
        "bundle_sha256": _sha256_file(zip_path),
        "files": {name: _sha256_bytes(data) for name, data in sorted(payload.items())},
    }
    report_path = output / f"sim-{version}-chatgpt-upload.report.json"
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return zip_path, report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--out-dir", type=Path)
    args = parser.parse_args(argv)
    try:
        zip_path, report = build_chatgpt_upload(args.root, out_dir=args.out_dir)
    except RuntimeError as exc:
        print(exc)
        return 1
    print(zip_path)
    print(report["bundle_sha256"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
