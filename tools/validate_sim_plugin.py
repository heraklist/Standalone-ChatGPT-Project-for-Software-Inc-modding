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
class PluginFinding:
    code: str
    path: str | None
    message: str


Finding = PluginFinding


def _finding(
    code: str,
    message: str,
    path: str | None = None,
) -> PluginFinding:
    return PluginFinding(code=code, path=path, message=message)


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


def _metadata(
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


def _destination(sim_relative: str, runtime: dict, policy: dict) -> tuple[str, str]:
    projection_root = policy["projection_target_path"]
    if sim_relative == "SKILL.md":
        return f"{projection_root}/SKILL.md", "EXACT_BYTE_COPY"

    parts = sim_relative.split("/")
    if len(parts) == 3 and parts[2] == "SKILL.md" and parts[0] in {
        "domains",
        "lifecycle",
    }:
        group = parts[0]
        module_id = parts[1]
        ids_key = "domain_ids" if group == "domains" else "lifecycle_ids"
        if module_id not in runtime.get(ids_key, []):
            raise ValueError(f"unregistered nested skill source: {sim_relative}")
        mapped = policy["internal_skill_targets"][group].format(id=module_id)
        return f"{projection_root}/{mapped}", "REMAP_EXACT_BYTE_COPY"

    if sim_relative.endswith("/SKILL.md"):
        raise ValueError(f"unexpected nested skill source: {sim_relative}")

    return f"{projection_root}/{sim_relative}", "EXACT_BYTE_COPY"


def _expected_candidate(
    source: GitSource,
) -> tuple[dict[str, bytes], dict, dict, dict[str, str]]:
    policy, policy_raw = _load_object(source, POLICY_PATH)
    runtime, runtime_raw = _load_object(source, RUNTIME_PATH)
    sim_manifest, _ = _load_object(source, SIM_MANIFEST_PATH)
    plugin_interface_path = policy.get("plugin_interface_source")
    if plugin_interface_path != "production/sim/manifests/plugin-interface.json":
        raise ValueError("plugin interface source is invalid")
    plugin_interface, _ = _load_object(source, plugin_interface_path)

    if runtime.get("plugin_identity") != "sim":
        raise ValueError("runtime plugin identity is not sim")
    if runtime.get("public_entrypoint") != "@sim":
        raise ValueError("runtime entrypoint is not @sim")
    if runtime.get("public_skill_count") != 1:
        raise ValueError("runtime public skill count is not one")
    if policy.get("plugin_identity") != "sim":
        raise ValueError("projection policy plugin identity is not sim")
    if policy.get("root_skill_relation") != "EXACT_BYTE_COPY":
        raise ValueError("root skill relation is not exact-byte copy")
    if policy.get("internal_skill_relation") != "REMAP_EXACT_BYTE_COPY":
        raise ValueError("internal skill relation is not remap exact-byte copy")

    source_prefix = policy.get("runtime_source_path")
    projection_root = policy.get("projection_target_path")
    if source_prefix != "production/sim" or projection_root != "skills/sim":
        raise ValueError("projection topology is invalid")

    projected: dict[str, bytes] = {}
    provenance_entries: list[dict[str, str]] = []

    def add(
        source_path: str,
        package_path: str,
        relation: str,
        data: bytes,
    ) -> None:
        safe = normalize_archive_member(package_path)
        if safe in projected:
            raise ValueError(f"duplicate expected package path: {safe}")
        projected[safe] = data
        provenance_entries.append(
            {
                "source_path": source_path,
                "package_path": safe,
                "relation": relation,
                "source_sha256": _sha256(data),
                "package_sha256": _sha256(data),
            }
        )

    sim_files = source.list_files(source_prefix)
    forbidden = set(policy.get("forbidden_source_paths", []))
    expected_nested = {
        f"{source_prefix}/domains/{module_id}/SKILL.md"
        for module_id in runtime.get("domain_ids", [])
    } | {
        f"{source_prefix}/lifecycle/{module_id}/SKILL.md"
        for module_id in runtime.get("lifecycle_ids", [])
    }
    if expected_nested - set(sim_files):
        raise ValueError("runtime topology sources are missing")

    for source_path in sim_files:
        relative = source_path[len(source_prefix) + 1 :]
        if relative in forbidden:
            raise ValueError(f"forbidden runtime source path: {relative}")
        package_path, relation = _destination(relative, runtime, policy)
        add(source_path, package_path, relation, source.read_bytes(source_path))

    capabilities_path = policy.get("tool_capabilities_source")
    if not isinstance(capabilities_path, str):
        raise ValueError("tool capabilities source is invalid")
    capabilities, _ = _load_object(source, capabilities_path)
    tools = capabilities.get("tools", {})
    if not isinstance(tools, dict):
        raise ValueError("tool capabilities must be an object")

    expected_tools: dict[str, str] = {}
    for tool_name, tool in sorted(tools.items()):
        if not isinstance(tool, dict):
            raise ValueError(f"tool capability is invalid: {tool_name}")
        surfaces = tool.get("surfaces", {})
        if not isinstance(surfaces, dict):
            raise ValueError(f"tool surfaces are invalid: {tool_name}")
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
            raise ValueError(f"bundled tool paths are invalid: {tool_name}")
        destination = f"{projection_root}/{normalize_archive_member(package_path)}"
        add(
            repository_source,
            destination,
            str(policy.get("tool_projection_relation", "EXACT_BYTE_COPY")),
            source.read_bytes(repository_source),
        )
        expected_tools[tool_name] = destination

    portable, compatibility = _metadata(runtime, sim_manifest, plugin_interface)
    portable_path = normalize_archive_member(policy["portable_manifest_path"])
    compatibility_path = normalize_archive_member(
        policy["compatibility_manifest_path"]
    )
    projected[portable_path] = _json_bytes(portable)
    projected[compatibility_path] = _json_bytes(compatibility)

    runtime_provenance_path = normalize_archive_member(
        policy["runtime_provenance_path"]
    )
    path_inventory_path = normalize_archive_member(policy["path_inventory_path"])
    file_hash_path = normalize_archive_member(policy["file_hash_manifest_path"])
    plugin_manifest_path = normalize_archive_member(policy["plugin_provenance_path"])

    expected = dict(projected)
    runtime_provenance = {
        "schema_version": 1,
        "source_commit": source.full_commit(),
        "entries": sorted(
            provenance_entries,
            key=lambda entry: (
                entry["package_path"],
                entry["source_path"],
            ),
        ),
    }
    expected[runtime_provenance_path] = _json_bytes(runtime_provenance)

    final_paths = sorted(
        set(projected)
        | {
            runtime_provenance_path,
            path_inventory_path,
            file_hash_path,
            plugin_manifest_path,
        }
    )
    expected[path_inventory_path] = _json_bytes(
        {"schema_version": 1, "paths": final_paths}
    )

    exclusions = {
        normalize_archive_member(path)
        for path in policy.get("semantic_aggregate_exclusions", [])
    }
    identity_hashes = {
        path: _sha256(data)
        for path, data in sorted(projected.items())
        if path not in exclusions
    }
    semantic = aggregate_file_hashes(identity_hashes)
    expected[file_hash_path] = _json_bytes(
        {"schema_version": 1, "files": identity_hashes}
    )
    expected[plugin_manifest_path] = _json_bytes(
        {
            "schema_version": 1,
            "plugin_identity": runtime["plugin_identity"],
            "plugin_version": sim_manifest["version"],
            "source_commit": source.full_commit(),
            "semantic_aggregate_sha256": semantic,
            "projection_policy_sha256": _sha256(policy_raw),
            "runtime_manifest_sha256": _sha256(runtime_raw),
            "candidate_tree_sha256_external": True,
        }
    )
    return expected, policy, runtime, expected_tools


def _actual_tree(candidate: Path) -> tuple[dict[str, bytes], list[Finding]]:
    findings: list[Finding] = []
    files: dict[str, bytes] = []
    actual: dict[str, bytes] = {}
    root = Path(candidate)
    if not root.is_dir() or root.is_symlink():
        return {}, [
            _finding(
                "SIM_PLUGIN_TOPOLOGY_DRIFT",
                "candidate root is not a real directory",
            )
        ]

    for current, dirnames, filenames in os.walk(root, followlinks=False):
        current_path = Path(current)
        kept_dirs: list[str] = []
        for dirname in sorted(dirnames):
            path = current_path / dirname
            metadata = path.lstat()
            if stat.S_ISLNK(metadata.st_mode):
                findings.append(
                    _finding(
                        "SIM_PLUGIN_UNEXPECTED_SYMLINK",
                        "candidate contains a symlink directory",
                        path.relative_to(root).as_posix(),
                    )
                )
                continue
            kept_dirs.append(dirname)
        dirnames[:] = kept_dirs

        for filename in sorted(filenames):
            path = current_path / filename
            relative = path.relative_to(root).as_posix()
            metadata = path.lstat()
            if stat.S_ISLNK(metadata.st_mode):
                findings.append(
                    _finding(
                        "SIM_PLUGIN_UNEXPECTED_SYMLINK",
                        "candidate contains a symlink",
                        relative,
                    )
                )
                continue
            if not stat.S_ISREG(metadata.st_mode):
                findings.append(
                    _finding(
                        "SIM_PLUGIN_UNSAFE_PATH",
                        "candidate contains a non-regular file",
                        relative,
                    )
                )
                continue
            try:
                safe = normalize_archive_member(relative)
            except ValueError:
                findings.append(
                    _finding(
                        "SIM_PLUGIN_UNSAFE_PATH",
                        "candidate path is unsafe or ambiguous",
                        relative,
                    )
                )
                continue
            if metadata.st_mode & 0o111:
                findings.append(
                    _finding(
                        "SIM_PLUGIN_UNEXPECTED_EXECUTABLE_HOOK",
                        "candidate contains an executable file",
                        safe,
                    )
                )
            actual[safe] = path.read_bytes()
    return actual, findings


def _parse_json_candidate(
    actual: dict[str, bytes],
    path: str,
) -> dict | None:
    data = actual.get(path)
    if data is None:
        return None
    try:
        value = json.loads(data.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return None
    return value if isinstance(value, dict) else None


def validate_candidate(
    repo_root: Path,
    candidate_root: Path,
    source_sha: str,
) -> list[Finding]:
    findings: list[Finding] = []
    try:
        source = GitSource(repo_root, source_sha)
    except ValueError as exc:
        text = str(exc)
        code = (
            "SIM_PLUGIN_SOURCE_REPOSITORY_INVALID"
            if "repository" in text
            else "SIM_PLUGIN_SOURCE_SHA_INVALID"
        )
        return [_finding(code, text)]

    try:
        expected, policy, runtime, expected_tools = _expected_candidate(source)
    except ValueError as exc:
        return [
            _finding(
                "SIM_PLUGIN_SOURCE_SHA_UNVERIFIABLE",
                str(exc),
            )
        ]

    actual, tree_findings = _actual_tree(Path(candidate_root))
    findings.extend(tree_findings)
    expected_paths = set(expected)
    actual_paths = set(actual)

    duplicate_runtime = sorted(
        path
        for path in actual_paths
        if path == "production/sim" or path.startswith("production/sim/")
    )
    for path in duplicate_runtime:
        findings.append(
            _finding(
                "SIM_PLUGIN_DUPLICATE_RUNTIME_SOURCE",
                "candidate contains a duplicate runtime authority tree",
                path,
            )
        )

    skill_paths = sorted(path for path in actual_paths if path.endswith("SKILL.md"))
    if skill_paths != ["skills/sim/SKILL.md"]:
        findings.append(
            _finding(
                "SIM_PLUGIN_PUBLIC_SKILL_COUNT_INVALID",
                "candidate must contain exactly one public SKILL.md at skills/sim/SKILL.md",
            )
        )

    for path in sorted(actual_paths - expected_paths):
        findings.append(
            _finding(
                "SIM_PLUGIN_UNDECLARED_FILE",
                "candidate contains a file outside the closed-world projection",
                path,
            )
        )
    missing = sorted(expected_paths - actual_paths)
    if missing:
        findings.append(
            _finding(
                "SIM_PLUGIN_TOPOLOGY_DRIFT",
                "candidate is missing declared paths: " + ", ".join(missing),
            )
        )

    source_projection_paths = {
        entry["package_path"]
        for entry in (
            _parse_json_candidate(expected, "provenance/runtime_provenance.json")
            or {}
        ).get("entries", [])
        if isinstance(entry, dict) and isinstance(entry.get("package_path"), str)
    }
    for path in sorted(source_projection_paths & actual_paths):
        if actual[path] != expected[path]:
            findings.append(
                _finding(
                    "SIM_PLUGIN_PROJECTION_BYTE_DRIFT",
                    "projected source bytes differ from exact source commit",
                    path,
                )
            )

    portable = _parse_json_candidate(actual, "plugin.json")
    expected_portable = _parse_json_candidate(expected, "plugin.json")
    portable_forbidden = {
        "schema_version",
        "display_name",
        "entrypoint",
        "runtime_skill",
        "public_skill_count",
        "canonical_game_target",
    }
    portable_valid = (
        isinstance(portable, dict)
        and portable.get("$schema")
        == "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json"
        and isinstance(portable.get("description"), str)
        and bool(portable["description"].strip())
        and not (portable_forbidden & set(portable))
    )
    if not portable_valid:
        findings.append(
            _finding(
                "SIM_PLUGIN_PORTABLE_MANIFEST_INVALID",
                "portable root plugin.json does not match the supported Agent Plugins manifest shape",
                "plugin.json",
            )
        )
    if (
        portable is None
        or expected_portable is None
        or portable.get("name") != expected_portable.get("name")
        or portable.get("version") != expected_portable.get("version")
    ):
        findings.append(
            _finding(
                "SIM_PLUGIN_IDENTITY_INVALID",
                "portable plugin identity/version differs from exact source projection",
                "plugin.json",
            )
        )

    compatibility_path = normalize_archive_member(
        policy["compatibility_manifest_path"]
    )
    compatibility = _parse_json_candidate(actual, compatibility_path)
    expected_compatibility = _parse_json_candidate(
        expected, compatibility_path
    )
    compatibility_forbidden = {
        "schema_version",
        "displayName",
        "entrypoint",
        "skill",
        "publicSkillCount",
    }
    interface = (
        compatibility.get("interface")
        if isinstance(compatibility, dict)
        else None
    )
    compatibility_valid = (
        isinstance(compatibility, dict)
        and isinstance(compatibility.get("description"), str)
        and bool(compatibility["description"].strip())
        and compatibility.get("skills") == "./skills/"
        and isinstance(interface, dict)
        and interface.get("displayName") == "SIM"
        and not (compatibility_forbidden & set(compatibility))
    )
    if not compatibility_valid:
        findings.append(
            _finding(
                "SIM_PLUGIN_COMPATIBILITY_MANIFEST_INVALID",
                "Codex compatibility manifest does not match the supported skills-plugin manifest shape",
                compatibility_path,
            )
        )
    if (
        compatibility is None
        or expected_compatibility is None
        or compatibility.get("name") != expected_compatibility.get("name")
        or compatibility.get("version")
        != expected_compatibility.get("version")
    ):
        findings.append(
            _finding(
                "SIM_PLUGIN_IDENTITY_INVALID",
                "compatibility plugin identity/version differs from exact source projection",
                compatibility_path,
            )
        )

    inventory_path = normalize_archive_member(policy["path_inventory_path"])
    inventory = _parse_json_candidate(actual, inventory_path)
    expected_inventory = _parse_json_candidate(expected, inventory_path)
    if inventory != expected_inventory or (
        inventory is not None and inventory.get("paths") != sorted(actual_paths)
    ):
        findings.append(
            _finding(
                "SIM_PLUGIN_PATH_INVENTORY_DRIFT",
                "candidate path inventory differs from the closed-world tree",
                inventory_path,
            )
        )

    file_hash_path = normalize_archive_member(policy["file_hash_manifest_path"])
    declared_hashes = _parse_json_candidate(actual, file_hash_path)
    expected_hashes = _parse_json_candidate(expected, file_hash_path)
    if declared_hashes != expected_hashes:
        findings.append(
            _finding(
                "SIM_PLUGIN_FILE_HASH_DRIFT",
                "candidate file hash manifest differs from expected identity files",
                file_hash_path,
            )
        )
    elif declared_hashes is not None:
        hashes = declared_hashes.get("files")
        if not isinstance(hashes, dict):
            findings.append(
                _finding(
                    "SIM_PLUGIN_FILE_HASH_DRIFT",
                    "candidate file hash manifest has invalid files object",
                    file_hash_path,
                )
            )
        else:
            for path, declared in hashes.items():
                if path not in actual or _sha256(actual[path]) != declared:
                    findings.append(
                        _finding(
                            "SIM_PLUGIN_FILE_HASH_DRIFT",
                            "candidate identity file bytes do not match declared SHA-256",
                            path,
                        )
                    )

    plugin_manifest_path = normalize_archive_member(
        policy["plugin_provenance_path"]
    )
    plugin_manifest = _parse_json_candidate(actual, plugin_manifest_path)
    expected_plugin_manifest = _parse_json_candidate(
        expected, plugin_manifest_path
    )
    if (
        plugin_manifest is None
        or expected_plugin_manifest is None
        or plugin_manifest.get("source_commit")
        != expected_plugin_manifest.get("source_commit")
    ):
        findings.append(
            _finding(
                "SIM_PLUGIN_SOURCE_SHA_INVALID",
                "plugin provenance source commit differs from exact validation source",
                plugin_manifest_path,
            )
        )
    if (
        plugin_manifest is None
        or expected_plugin_manifest is None
        or plugin_manifest.get("plugin_identity")
        != expected_plugin_manifest.get("plugin_identity")
        or plugin_manifest.get("plugin_version")
        != expected_plugin_manifest.get("plugin_version")
    ):
        findings.append(
            _finding(
                "SIM_PLUGIN_IDENTITY_INVALID",
                "plugin provenance identity/version differs from exact source projection",
                plugin_manifest_path,
            )
        )
    if (
        plugin_manifest is None
        or expected_plugin_manifest is None
        or plugin_manifest.get("semantic_aggregate_sha256")
        != expected_plugin_manifest.get("semantic_aggregate_sha256")
    ):
        findings.append(
            _finding(
                "SIM_PLUGIN_AGGREGATE_HASH_DRIFT",
                "semantic aggregate identity differs from exact source projection",
                plugin_manifest_path,
            )
        )
    provenance_fields = (
        "projection_policy_sha256",
        "runtime_manifest_sha256",
        "candidate_tree_sha256_external",
    )
    if (
        plugin_manifest is None
        or expected_plugin_manifest is None
        or any(
            plugin_manifest.get(field)
            != expected_plugin_manifest.get(field)
            for field in provenance_fields
        )
    ):
        findings.append(
            _finding(
                "SIM_PLUGIN_RUNTIME_PROVENANCE_DRIFT",
                "plugin provenance metadata differs from independently recomputed values",
                plugin_manifest_path,
            )
        )

    runtime_provenance_path = normalize_archive_member(
        policy["runtime_provenance_path"]
    )
    if actual.get(runtime_provenance_path) != expected.get(runtime_provenance_path):
        findings.append(
            _finding(
                "SIM_PLUGIN_RUNTIME_PROVENANCE_DRIFT",
                "runtime provenance differs from exact source mapping",
                runtime_provenance_path,
            )
        )

    for tool_name, package_path in sorted(expected_tools.items()):
        if actual.get(package_path) != expected.get(package_path):
            findings.append(
                _finding(
                    "SIM_PLUGIN_TOOL_CAPABILITY_DRIFT",
                    f"bundled tool capability differs from declared source: {tool_name}",
                    package_path,
                )
            )

    forbidden_tokens = (
        b"OPENAI_API_KEY",
        b"sk-proj-",
        b"mandatory paid service",
        b"requires OpenAI API billing",
        b"UNDECLARED_APP",
        b"undeclared app",
        b"undeclared MCP",
    )
    for path, data in sorted(actual.items()):
        lowered = data.lower()
        for token in forbidden_tokens:
            if token.lower() in lowered:
                findings.append(
                    _finding(
                        "SIM_PLUGIN_FORBIDDEN_REQUIREMENT",
                        "candidate contains a forbidden runtime requirement",
                        path,
                    )
                )
                break

    return findings


def validate_candidate_report(
    repo_root: Path,
    candidate_root: Path,
    source_sha: str,
) -> dict[str, object]:
    findings = validate_candidate(repo_root, candidate_root, source_sha)
    candidate_tree_sha256: str | None
    try:
        candidate_tree_sha256 = hash_tree(Path(candidate_root))
    except (OSError, ValueError):
        candidate_tree_sha256 = None
    return {
        "candidate_tree_sha256": candidate_tree_sha256,
        "findings": findings,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)
    check = subparsers.add_parser("check")
    check.add_argument("--repo-root", type=Path, default=Path("."))
    check.add_argument("--candidate", type=Path, required=True)
    check.add_argument("--source-sha", required=True)
    args = parser.parse_args(argv)

    report = validate_candidate_report(
        args.repo_root,
        args.candidate,
        args.source_sha,
    )
    findings = report["findings"]
    if not findings:
        print("PASS")
        return 0

    assert isinstance(findings, list)
    for finding in sorted(
        findings,
        key=lambda item: (
            item.code,
            item.path or "",
            item.message,
        ),
    ):
        if finding.path:
            print(f"{finding.code}: {finding.path}: {finding.message}")
        else:
            print(f"{finding.code}: {finding.message}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
