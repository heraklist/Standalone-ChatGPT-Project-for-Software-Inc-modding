from __future__ import annotations

import argparse
import hashlib
import json
import os
import stat
import sys
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.safe_artifacts import normalize_archive_member
from tools.sim_candidate_identity import aggregate_file_hashes, hash_tree
from tools.sim_git_source import GitSource

POLICY_PATH = "docs/architecture/plugin/SIM-PLUGIN-PROJECTION-POLICY.json"
RUNTIME_PATH = "production/sim/RUNTIME.json"
SIM_MANIFEST_PATH = "production/sim/manifests/sim-manifest.json"


@dataclass(frozen=True)
class BuildResult:
    candidate_root: Path
    source_commit: str
    semantic_aggregate_sha256: str
    candidate_tree_sha256: str


def _json_bytes(value: object) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _load_object(source: GitSource, path: str) -> tuple[dict, bytes]:
    raw = source.read_bytes(path)
    try:
        value = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"invalid JSON source at {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"JSON source must be an object: {path}")
    return value, raw


def _prepare_output(path: Path) -> Path:
    output = Path(path)
    if output.is_symlink():
        raise ValueError("candidate output must not be a symlink")
    if output.exists():
        metadata = output.lstat()
        reparse_flag = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0)
        attributes = getattr(metadata, "st_file_attributes", 0)
        if bool(reparse_flag and attributes & reparse_flag):
            raise ValueError("candidate output must not be a reparse point")
        if not stat.S_ISDIR(metadata.st_mode):
            raise ValueError("candidate output must be a directory")
        if any(output.iterdir()):
            raise ValueError("candidate output directory must be empty")
    else:
        output.mkdir(parents=True)
    return output.resolve()


def _write_file(root: Path, relative: str, data: bytes) -> None:
    safe = normalize_archive_member(relative)
    target = root / safe
    resolved_parent = target.parent.resolve()
    try:
        resolved_parent.relative_to(root)
    except ValueError as exc:
        raise ValueError(f"candidate path escapes output root: {relative}") from exc
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists() or target.is_symlink():
        raise ValueError(f"candidate path collision: {safe}")
    target.write_bytes(data)


def _projected_destination(
    *,
    sim_relative: str,
    runtime: dict,
    policy: dict,
) -> tuple[str, str]:
    if sim_relative == "SKILL.md":
        return (
            f"{policy['projection_target_path']}/SKILL.md",
            "EXACT_BYTE_COPY",
        )

    parts = sim_relative.split("/")
    if len(parts) == 3 and parts[2] == "SKILL.md" and parts[0] in {
        "domains",
        "lifecycle",
    }:
        group = parts[0]
        module_id = parts[1]
        ids_key = "domain_ids" if group == "domains" else "lifecycle_ids"
        if module_id not in runtime.get(ids_key, []):
            raise ValueError(
                f"nested SIM skill is not registered in RUNTIME.json: {sim_relative}"
            )
        template = policy["internal_skill_targets"][group]
        mapped = template.format(id=module_id)
        return (
            f"{policy['projection_target_path']}/{mapped}",
            "REMAP_EXACT_BYTE_COPY",
        )

    if sim_relative.endswith("/SKILL.md"):
        raise ValueError(f"unexpected public/nested SIM skill source: {sim_relative}")

    return (
        f"{policy['projection_target_path']}/{sim_relative}",
        "EXACT_BYTE_COPY",
    )


def _validate_runtime_policy(runtime: dict, policy: dict, sim_manifest: dict) -> None:
    if runtime.get("plugin_identity") != "sim":
        raise ValueError("runtime plugin identity must be sim")
    if runtime.get("public_entrypoint") != "@sim":
        raise ValueError("runtime public entrypoint must be @sim")
    if runtime.get("runtime_skill") != "sim":
        raise ValueError("runtime skill must be sim")
    if runtime.get("public_skill_count") != 1:
        raise ValueError("runtime must expose exactly one public skill")
    if policy.get("plugin_identity") != runtime.get("plugin_identity"):
        raise ValueError("projection policy identity differs from runtime")
    if policy.get("public_skill_count") != 1:
        raise ValueError("projection policy must expose exactly one public skill")
    if policy.get("root_skill_relation") != "EXACT_BYTE_COPY":
        raise ValueError("root skill projection must be exact-byte copy")
    if policy.get("internal_skill_relation") != "REMAP_EXACT_BYTE_COPY":
        raise ValueError("internal skill projection must be exact-byte remap")
    if (
        runtime.get("canonical_game_target")
        != sim_manifest.get("canonical_game_target")
    ):
        raise ValueError("runtime target differs from SIM manifest")
    domains = runtime.get("domain_ids")
    lifecycle = runtime.get("lifecycle_ids")
    if (
        not isinstance(domains, list)
        or runtime.get("domain_count") != len(domains)
        or len(domains) != len(set(domains))
    ):
        raise ValueError("runtime domain topology is invalid")
    if (
        not isinstance(lifecycle, list)
        or runtime.get("lifecycle_count") != len(lifecycle)
        or len(lifecycle) != len(set(lifecycle))
    ):
        raise ValueError("runtime lifecycle topology is invalid")


def _generated_manifests(
    runtime: dict,
    sim_manifest: dict,
    plugin_interface: dict,
) -> tuple[dict, dict]:
    target = runtime["canonical_game_target"]
    description = f"SIM — Software Inc modding workflows for {target}."
    interface = {
        key: value
        for key, value in plugin_interface.items()
        if key != "schema_version"
    }
    portable = {
        "$schema": "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json",
        "name": runtime["plugin_identity"],
        "version": sim_manifest["version"],
        "description": description,
        "extensions": {
            "com.openai": {
                "interface": interface,
            }
        },
    }
    compatibility = {
        "name": runtime["plugin_identity"],
        "version": sim_manifest["version"],
        "description": description,
        "skills": "./skills/",
        "interface": interface,
    }
    return portable, compatibility


def build_candidate(
    repo_root: Path,
    source_sha: str,
    output_root: Path,
) -> BuildResult:
    repo = Path(repo_root).resolve()
    source = GitSource(repo, source_sha)
    full_source = source.full_commit()

    policy, policy_raw = _load_object(source, POLICY_PATH)
    runtime, runtime_raw = _load_object(source, RUNTIME_PATH)
    sim_manifest, _ = _load_object(source, SIM_MANIFEST_PATH)
    plugin_interface_path = str(policy.get("plugin_interface_source", ""))
    if plugin_interface_path != "production/sim/manifests/plugin-interface.json":
        raise ValueError("unexpected SIM plugin interface source")
    plugin_interface, _ = _load_object(source, plugin_interface_path)
    _validate_runtime_policy(runtime, policy, sim_manifest)

    output = _prepare_output(output_root)
    projected: dict[str, bytes] = {}
    provenance_entries: list[dict[str, str]] = []

    source_prefix = str(policy.get("runtime_source_path", ""))
    if source_prefix != "production/sim":
        raise ValueError("unexpected SIM runtime source path in projection policy")
    projection_root = str(policy.get("projection_target_path", ""))
    if projection_root != "skills/sim":
        raise ValueError("unexpected SIM projection target path")

    sim_files = source.list_files(source_prefix)
    forbidden = set(policy.get("forbidden_source_paths", []))
    expected_nested = {
        f"production/sim/domains/{module_id}/SKILL.md"
        for module_id in runtime["domain_ids"]
    } | {
        f"production/sim/lifecycle/{module_id}/SKILL.md"
        for module_id in runtime["lifecycle_ids"]
    }
    missing_nested = expected_nested - set(sim_files)
    if missing_nested:
        raise ValueError(
            "runtime topology source files are missing: "
            + ", ".join(sorted(missing_nested))
        )

    def add_projection(
        source_path: str,
        package_path: str,
        relation: str,
        data: bytes,
    ) -> None:
        safe_package = normalize_archive_member(package_path)
        if safe_package in projected:
            raise ValueError(f"candidate projection path collision: {safe_package}")
        projected[safe_package] = data
        provenance_entries.append(
            {
                "source_path": source_path,
                "package_path": safe_package,
                "relation": relation,
                "source_sha256": _sha256(data),
                "package_sha256": _sha256(data),
            }
        )

    for source_path in sim_files:
        sim_relative = source_path[len(source_prefix) + 1 :]
        if sim_relative in forbidden:
            raise ValueError(
                f"forbidden generated/provenance source committed in runtime: {sim_relative}"
            )
        package_path, relation = _projected_destination(
            sim_relative=sim_relative,
            runtime=runtime,
            policy=policy,
        )
        data = source.read_bytes(source_path)
        add_projection(source_path, package_path, relation, data)

    capabilities_path = str(policy.get("tool_capabilities_source", ""))
    capabilities, _ = _load_object(source, capabilities_path)
    tools = capabilities.get("tools", {})
    if not isinstance(tools, dict):
        raise ValueError("SIM tool capabilities must be an object")

    for tool_name, tool in sorted(tools.items()):
        if not isinstance(tool, dict):
            raise ValueError(f"invalid tool capability: {tool_name}")
        surfaces = tool.get("surfaces", {})
        if not isinstance(surfaces, dict):
            raise ValueError(f"invalid tool surfaces: {tool_name}")
        bundled = any(
            isinstance(surface, dict) and surface.get("bundled") is True
            for surface_name, surface in surfaces.items()
            if surface_name in {"ChatGPT", "Codex"}
        )
        if not bundled:
            continue
        repository_source = tool.get("repository_source")
        package_path = tool.get("package_path")
        if not isinstance(repository_source, str) or not isinstance(
            package_path, str
        ):
            raise ValueError(f"invalid bundled tool paths: {tool_name}")
        safe_tool_path = normalize_archive_member(package_path)
        destination = f"{projection_root}/{safe_tool_path}"
        data = source.read_bytes(repository_source)
        add_projection(
            repository_source,
            destination,
            str(policy.get("tool_projection_relation", "EXACT_BYTE_COPY")),
            data,
        )

    portable, compatibility = _generated_manifests(
        runtime, sim_manifest, plugin_interface
    )
    portable_path = normalize_archive_member(policy["portable_manifest_path"])
    compatibility_path = normalize_archive_member(
        policy["compatibility_manifest_path"]
    )
    if portable_path in projected or compatibility_path in projected:
        raise ValueError("generated metadata path collides with projected source")
    projected[portable_path] = _json_bytes(portable)
    projected[compatibility_path] = _json_bytes(compatibility)

    for relative, data in sorted(projected.items()):
        _write_file(output, relative, data)

    runtime_provenance_path = normalize_archive_member(
        policy["runtime_provenance_path"]
    )
    path_inventory_path = normalize_archive_member(policy["path_inventory_path"])
    file_hash_manifest_path = normalize_archive_member(
        policy["file_hash_manifest_path"]
    )
    plugin_provenance_path = normalize_archive_member(
        policy["plugin_provenance_path"]
    )
    provenance_paths = {
        runtime_provenance_path,
        path_inventory_path,
        file_hash_manifest_path,
        plugin_provenance_path,
    }
    if provenance_paths & set(projected):
        raise ValueError("generated provenance path collides with candidate source")

    runtime_provenance = {
        "schema_version": 1,
        "source_commit": full_source,
        "entries": sorted(
            provenance_entries,
            key=lambda entry: (
                entry["package_path"],
                entry["source_path"],
            ),
        ),
    }
    _write_file(
        output,
        runtime_provenance_path,
        _json_bytes(runtime_provenance),
    )

    final_paths = sorted(
        set(projected)
        | {
            runtime_provenance_path,
            path_inventory_path,
            file_hash_manifest_path,
            plugin_provenance_path,
        }
    )
    path_inventory = {
        "schema_version": 1,
        "paths": final_paths,
    }
    _write_file(output, path_inventory_path, _json_bytes(path_inventory))

    exclusions = {
        normalize_archive_member(path)
        for path in policy.get("semantic_aggregate_exclusions", [])
    }
    identity_files = {
        path: data
        for path, data in projected.items()
        if path not in exclusions
    }
    identity_hashes = {
        path: _sha256(data)
        for path, data in sorted(identity_files.items())
    }
    semantic_aggregate = aggregate_file_hashes(identity_hashes)
    file_hash_manifest = {
        "schema_version": 1,
        "files": identity_hashes,
    }
    _write_file(
        output,
        file_hash_manifest_path,
        _json_bytes(file_hash_manifest),
    )

    plugin_provenance = {
        "schema_version": 1,
        "plugin_identity": runtime["plugin_identity"],
        "plugin_version": sim_manifest["version"],
        "source_commit": full_source,
        "semantic_aggregate_sha256": semantic_aggregate,
        "projection_policy_sha256": _sha256(policy_raw),
        "runtime_manifest_sha256": _sha256(runtime_raw),
        "candidate_tree_sha256_external": True,
    }
    _write_file(
        output,
        plugin_provenance_path,
        _json_bytes(plugin_provenance),
    )

    actual_paths = sorted(
        path.relative_to(output).as_posix()
        for path in output.rglob("*")
        if path.is_file()
    )
    if actual_paths != final_paths:
        raise ValueError("candidate path inventory does not match final tree")

    tree_sha = hash_tree(output)
    return BuildResult(
        candidate_root=output,
        source_commit=full_source,
        semantic_aggregate_sha256=semantic_aggregate,
        candidate_tree_sha256=tree_sha,
    )


def _display_candidate_path(repo_root: Path, candidate_root: Path) -> str:
    try:
        return candidate_root.relative_to(repo_root.resolve()).as_posix()
    except ValueError:
        return candidate_root.as_posix()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)
    build = subparsers.add_parser("build")
    build.add_argument("--repo-root", type=Path, default=Path("."))
    build.add_argument("--source-sha", required=True)
    build.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)

    if args.command != "build":
        parser.error("unsupported command")

    try:
        result = build_candidate(
            args.repo_root,
            args.source_sha,
            args.output,
        )
    except (ValueError, OSError) as exc:
        print(str(exc), file=sys.stderr)
        return 1

    payload = {
        "candidate_root": _display_candidate_path(
            Path(args.repo_root), result.candidate_root
        ),
        "source_commit": result.source_commit,
        "semantic_aggregate_sha256": result.semantic_aggregate_sha256,
        "candidate_tree_sha256": result.candidate_tree_sha256,
    }
    print(json.dumps(payload, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
