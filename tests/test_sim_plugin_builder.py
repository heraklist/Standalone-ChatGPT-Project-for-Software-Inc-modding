from __future__ import annotations

import subprocess
from pathlib import Path

import pytest


def _git(repo: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(repo), *args],
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def make_git_source_fixture(tmp_path: Path):
    from tools.sim_git_source import GitSource

    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init")
    _git(repo, "config", "user.email", "sim@example.invalid")
    _git(repo, "config", "user.name", "SIM Test")
    skill = repo / "production/sim/SKILL.md"
    skill.parent.mkdir(parents=True)
    skill.write_bytes(b"committed\n")
    _git(repo, "add", "production/sim/SKILL.md")
    _git(repo, "commit", "-m", "fixture")
    source = GitSource(repo, "HEAD")
    skill.write_bytes(b"dirty\n")
    return source


def test_git_source_reads_committed_bytes_not_dirty_worktree(tmp_path: Path) -> None:
    source = make_git_source_fixture(tmp_path)
    assert source.read_bytes("production/sim/SKILL.md") == b"committed\n"


def test_git_source_lists_committed_files_in_sorted_order(tmp_path: Path) -> None:
    from tools.sim_git_source import GitSource

    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init")
    _git(repo, "config", "user.email", "sim@example.invalid")
    _git(repo, "config", "user.name", "SIM Test")
    for relative, data in (
        ("production/sim/z.txt", b"z"),
        ("production/sim/a.txt", b"a"),
        ("outside.txt", b"x"),
    ):
        path = repo / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
    _git(repo, "add", ".")
    _git(repo, "commit", "-m", "fixture")

    source = GitSource(repo, "HEAD")
    assert source.list_files("production/sim") == (
        "production/sim/a.txt",
        "production/sim/z.txt",
    )


def test_git_source_rejects_invalid_source_sha(tmp_path: Path) -> None:
    from tools.sim_git_source import GitSource

    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init")
    with pytest.raises(ValueError, match="commit"):
        GitSource(repo, "definitely-not-a-commit")


@pytest.mark.parametrize(
    "path",
    ("/absolute.txt", "../secret.txt", "production/../secret.txt", r"production\sim\SKILL.md"),
)
def test_git_source_rejects_unsafe_repository_paths(tmp_path: Path, path: str) -> None:
    source = make_git_source_fixture(tmp_path)
    with pytest.raises(ValueError, match="path"):
        source.read_bytes(path)


ROOT = Path(__file__).resolve().parents[1]


def _current_head(repo: Path) -> str:
    return _git(repo, "rev-parse", "HEAD")


def _candidate_snapshot(root: Path) -> dict[str, bytes]:
    return {
        path.relative_to(root).as_posix(): path.read_bytes()
        for path in sorted(root.rglob("*"))
        if path.is_file()
    }


def test_build_candidate_projects_one_public_skill_and_internal_modules(
    tmp_path: Path,
) -> None:
    from tools.build_sim_plugin import build_candidate
    from tools.sim_git_source import GitSource

    source_sha = _current_head(ROOT)
    output = tmp_path / "candidate"
    result = build_candidate(ROOT, source_sha, output)

    assert (output / "plugin.json").is_file()
    assert (output / ".codex-plugin/plugin.json").is_file()
    assert [
        path.relative_to(output).as_posix()
        for path in output.rglob("SKILL.md")
    ] == ["skills/sim/SKILL.md"]

    runtime = __import__("json").loads(
        GitSource(ROOT, source_sha).read_bytes("production/sim/RUNTIME.json")
    )
    for domain_id in runtime["domain_ids"]:
        assert (
            output
            / f"skills/sim/references/internal/domains/{domain_id}.md"
        ).is_file()
    for lifecycle_id in runtime["lifecycle_ids"]:
        assert (
            output
            / f"skills/sim/references/internal/lifecycle/{lifecycle_id}.md"
        ).is_file()

    source = GitSource(ROOT, source_sha)
    assert (output / "skills/sim/SKILL.md").read_bytes() == source.read_bytes(
        "production/sim/SKILL.md"
    )
    assert (output / "skills/sim/tools/validate_code_profile.py").read_bytes() == (
        source.read_bytes("tools/validate_code_profile.py")
    )
    assert (output / "skills/sim/tools/inspect_archive.py").read_bytes() == (
        source.read_bytes("tools/inspect_archive.py")
    )
    assert len(result.semantic_aggregate_sha256) == 64
    assert len(result.candidate_tree_sha256) == 64


def test_build_candidate_is_byte_reproducible_and_tree_identity_matches(
    tmp_path: Path,
) -> None:
    from tools.build_sim_plugin import build_candidate
    from tools.sim_candidate_identity import hash_tree

    source_sha = _current_head(ROOT)
    first = tmp_path / "first"
    second = tmp_path / "second"
    first_result = build_candidate(ROOT, source_sha, first)
    second_result = build_candidate(ROOT, source_sha, second)

    assert _candidate_snapshot(first) == _candidate_snapshot(second)
    assert first_result.semantic_aggregate_sha256 == second_result.semantic_aggregate_sha256
    assert first_result.candidate_tree_sha256 == second_result.candidate_tree_sha256
    assert first_result.candidate_tree_sha256 == hash_tree(first)
    assert second_result.candidate_tree_sha256 == hash_tree(second)


def _make_minimal_projection_repo(tmp_path: Path) -> tuple[Path, str]:
    import json
    import shutil

    repo = tmp_path / "projection-repo"
    repo.mkdir()
    _git(repo, "init")
    _git(repo, "config", "user.email", "sim@example.invalid")
    _git(repo, "config", "user.name", "SIM Test")

    policy_source = (
        ROOT / "docs/architecture/plugin/SIM-PLUGIN-PROJECTION-POLICY.json"
    )
    policy_target = (
        repo / "docs/architecture/plugin/SIM-PLUGIN-PROJECTION-POLICY.json"
    )
    policy_target.parent.mkdir(parents=True)
    shutil.copy2(policy_source, policy_target)

    runtime = {
        "schema_version": 1,
        "plugin_identity": "sim",
        "public_entrypoint": "@sim",
        "display_invocation": "@Sim",
        "runtime_skill": "sim",
        "public_skill_count": 1,
        "canonical_game_target": "Beta 1.8.42",
        "domain_count": 1,
        "domain_ids": ["d1"],
        "lifecycle_count": 1,
        "lifecycle_ids": ["l1"],
    }
    files = {
        "production/sim/RUNTIME.json": json.dumps(runtime).encode(),
        "production/sim/SKILL.md": b"committed skill\n",
        "production/sim/domains/d1/SKILL.md": b"domain\n",
        "production/sim/lifecycle/l1/SKILL.md": b"lifecycle\n",
        "production/sim/manifests/sim-manifest.json": json.dumps(
            {
                "product": "SIM",
                "display_name": "Software Inc Modding",
                "version": "0.2.3-preview.1",
                "channel": "PREVIEW",
                "canonical_game_target": "Beta 1.8.42",
                "evidence_grade": "GENERATION_GRADE",
            }
        ).encode(),
        "production/sim/manifests/tool-capabilities.json": json.dumps(
            {"schema_version": 1, "tools": {}}
        ).encode(),
        "production/sim/manifests/plugin-interface.json": json.dumps(
            {
                "schema_version": 1,
                "displayName": "SIM",
                "shortDescription": "Software Inc modding for Beta 1.8.42.",
                "longDescription": "Create and verify Software Inc mods.",
                "developerName": "Heraklis",
                "category": "Developer Tools",
                "capabilities": ["Create Software Inc mods"],
                "defaultPrompt": ["Create a Software Inc mod for Beta 1.8.42."]
            }
        ).encode(),
        "production/sim/references/example.md": b"reference\n",
    }
    for relative, data in files.items():
        target = repo / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
    _git(repo, "add", ".")
    _git(repo, "commit", "-m", "projection fixture")
    return repo, _current_head(repo)


def test_build_candidate_uses_source_commit_not_dirty_worktree(tmp_path: Path) -> None:
    from tools.build_sim_plugin import build_candidate

    repo, source_sha = _make_minimal_projection_repo(tmp_path)
    (repo / "production/sim/SKILL.md").write_bytes(b"dirty skill\n")

    output = tmp_path / "candidate"
    build_candidate(repo, source_sha, output)
    assert (output / "skills/sim/SKILL.md").read_bytes() == b"committed skill\n"


def test_build_candidate_rejects_nonempty_output(tmp_path: Path) -> None:
    from tools.build_sim_plugin import build_candidate

    source_sha = _current_head(ROOT)
    output = tmp_path / "candidate"
    output.mkdir()
    (output / "rogue.txt").write_text("occupied", encoding="utf-8")
    with pytest.raises(ValueError, match="output"):
        build_candidate(ROOT, source_sha, output)


def test_build_candidate_emits_portable_agent_plugins_and_codex_manifests(
    tmp_path: Path,
) -> None:
    import json

    from tools.build_sim_plugin import build_candidate

    source_sha = _current_head(ROOT)
    output = tmp_path / "candidate"
    build_candidate(ROOT, source_sha, output)

    portable = json.loads((output / "plugin.json").read_text(encoding="utf-8"))
    compatibility = json.loads(
        (output / ".codex-plugin/plugin.json").read_text(encoding="utf-8")
    )

    assert portable["$schema"] == "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json"
    assert portable["name"] == "sim"
    assert portable["version"] == "0.2.3-preview.1"
    assert isinstance(portable["description"], str) and portable["description"]
    assert "schema_version" not in portable
    assert "display_name" not in portable
    assert "entrypoint" not in portable
    assert "runtime_skill" not in portable
    assert "public_skill_count" not in portable
    assert "canonical_game_target" not in portable

    assert compatibility["name"] == "sim"
    assert compatibility["version"] == "0.2.3-preview.1"
    assert isinstance(compatibility["description"], str) and compatibility["description"]
    assert compatibility["skills"] == "./skills/"
    assert compatibility["interface"]["displayName"] == "SIM"
    assert "schema_version" not in compatibility
    assert "displayName" not in compatibility
    assert "entrypoint" not in compatibility
    assert "skill" not in compatibility
    assert "publicSkillCount" not in compatibility


def test_build_candidate_emits_canonical_openai_interface_metadata(
    tmp_path: Path,
) -> None:
    import json

    from tools.build_sim_plugin import build_candidate

    source_sha = _current_head(ROOT)
    output = tmp_path / "candidate"
    build_candidate(ROOT, source_sha, output)

    portable = json.loads((output / "plugin.json").read_text(encoding="utf-8"))
    compatibility = json.loads(
        (output / ".codex-plugin/plugin.json").read_text(encoding="utf-8")
    )

    assert "extensions" in portable
    assert "com.openai" in portable["extensions"]
    interface = portable["extensions"]["com.openai"]["interface"]

    assert interface["displayName"] == "SIM"
    assert interface["developerName"] == "Heraklis"
    assert interface["category"] == "Developer Tools"
    assert len(interface["defaultPrompt"]) == 3
    assert all(
        isinstance(prompt, str)
        and prompt
        and "\n" not in prompt
        and len(prompt) <= 128
        for prompt in interface["defaultPrompt"]
    )
    assert compatibility["interface"] == interface
