from __future__ import annotations

import json

import jsonschema
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROFILE = ROOT / "production/sim/manifests/certification-profile.json"


def test_v3_profile_freezes_required_surfaces_and_cases() -> None:
    profile = json.loads(PROFILE.read_text(encoding="utf-8"))

    assert profile["protocol_version"] == "sim-live-v3"
    assert profile["plugin_version"] == "0.2.3-preview.1"
    assert profile["production_transport"] == "OPENAI_PERSONAL_PLUGIN"

    assert profile["surfaces"]["CHATGPT_WEB_NORMAL_CHAT"]["required_cases"] == [
        f"A{i:02d}" for i in range(1, 13)
    ]
    assert profile["surfaces"]["CHATGPT_DESKTOP_NORMAL_CHAT"]["required_cases"] == [
        "A01", "A03", "A06", "A09", "A10", "A12"
    ]
    assert profile["surfaces"]["CODEX"]["required_cases"] == [
        "A01", "A03", "A09", "A10", "A12"
    ]
    assert profile["surfaces"]["CHATGPT_WORK"]["release_blocking"] is False
    assert profile["surfaces"]["LOCAL_MARKETPLACE"]["release_blocking"] is False


def test_acceptance_context_isolates_transport_and_exact_personal_release() -> None:
    from tools.sim_acceptance import CertificationContext, _matches_context

    context = CertificationContext(
        candidate_tree_sha256="a" * 64,
        semantic_aggregate_sha256="b" * 64,
        source_commit="c" * 40,
        plugin_version="0.2.3-preview.1",
        exact_target_manifest_sha256="d" * 64,
        protocol_version="sim-live-v3",
        surface="CHATGPT_WEB_NORMAL_CHAT",
        transport="OPENAI_PERSONAL_PLUGIN",
        plugin_id="plugins~Plugin_sim",
        release_id="release_exact",
    )
    record = {
        "candidate_tree_sha256": "a" * 64,
        "semantic_aggregate_sha256": "b" * 64,
        "candidate_source_commit": "c" * 40,
        "plugin_version": "0.2.3-preview.1",
        "exact_target_manifest_sha256": "d" * 64,
        "certification_protocol_version": "sim-live-v3",
        "surface": "CHATGPT_WEB_NORMAL_CHAT",
        "transport": "OPENAI_PERSONAL_PLUGIN",
        "plugin_id": "plugins~Plugin_sim",
        "release_id": "release_exact",
    }
    assert _matches_context(record, context) is True

    record["surface"] = "CHATGPT_DESKTOP_NORMAL_CHAT"
    assert _matches_context(record, context) is False
    record["surface"] = "CHATGPT_WEB_NORMAL_CHAT"
    record["transport"] = "MARKETPLACE_GIT_SUBDIR"
    assert _matches_context(record, context) is False
    record["transport"] = "OPENAI_PERSONAL_PLUGIN"
    record["release_id"] = "release_other"
    assert _matches_context(record, context) is False


def _git(repo: Path, *args: str) -> str:
    import subprocess

    return subprocess.check_output(
        ["git", "-C", str(repo), *args],
        text=True,
    ).strip()


def _commit_all(repo: Path, message: str) -> str:
    import subprocess

    subprocess.check_call(["git", "-C", str(repo), "add", "."])
    subprocess.check_call(
        [
            "git",
            "-C",
            str(repo),
            "-c",
            "user.name=SIM Test",
            "-c",
            "user.email=sim-test@example.invalid",
            "commit",
            "-m",
            message,
        ],
        stdout=subprocess.DEVNULL,
    )
    return _git(repo, "rev-parse", "HEAD")


def test_marketplace_chain_rejects_projection_pin_mismatch(tmp_path: Path) -> None:
    import subprocess

    from tools.verify_sim_certification import _verify_marketplace_chain

    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.check_call(["git", "-C", str(repo), "init", "-q"])

    (repo / "source.txt").write_text("semantic source", encoding="utf-8")
    source_sha = _commit_all(repo, "source")

    provenance = repo / "plugins/sim/provenance"
    provenance.mkdir(parents=True)
    (provenance / "plugin_manifest.json").write_text(
        json.dumps({"source_commit": source_sha}),
        encoding="utf-8",
    )
    projection_sha = _commit_all(repo, "projection")

    marketplace = repo / ".agents/plugins"
    marketplace.mkdir(parents=True)
    (marketplace / "marketplace.json").write_text(
        json.dumps(
            {
                "name": "sim-certification",
                "plugins": [
                    {
                        "name": "sim",
                        "source": {
                            "source": "git-subdir",
                            "path": "./plugins/sim",
                            "sha": projection_sha,
                        },
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    marketplace_sha = _commit_all(repo, "marketplace")

    record = {
        "source_commit": source_sha,
        "projection_commit": "f" * 40,
        "marketplace_commit": marketplace_sha,
        "marketplace_name": "sim-certification",
        "plugin_locator": "./plugins/sim",
    }
    errors = _verify_marketplace_chain(repo, record)
    assert any("marketplace projection mismatch" in error for error in errors)


def test_personal_release_binding_rejects_bundle_mismatch() -> None:
    from tools.verify_sim_certification import _verify_personal_evidence_binding

    installation = {
        "plugin_id": "plugins~Plugin_sim",
        "release_id": "release_exact",
        "bundle_sha256": "a" * 64,
        "platform_release_tree_sha256": "b" * 64,
        "normalized_platform_tree_sha256": "d" * 64,
    }
    release = {
        "plugin_id": "plugins~Plugin_sim",
        "release_id": "release_exact",
        "bundle_sha256": "c" * 64,
        "platform_release_tree_sha256": "b" * 64,
        "normalized_platform_tree_sha256": "d" * 64,
    }
    errors = _verify_personal_evidence_binding(installation, release)
    assert errors == ["personal plugin bundle mismatch"]


def test_personal_installation_contract_carries_normalized_platform_tree() -> None:
    schema = json.loads(
        (ROOT / "schemas/sim-installation-evidence.schema.json").read_text(
            encoding="utf-8"
        )
    )
    record = {
        "schema_version": 2,
        "installation_evidence_id": "web-personal-install-normalized",
        "surface": "CHATGPT_WEB_NORMAL_CHAT",
        "result": "PASS",
        "candidate_tree_sha256": "a" * 64,
        "semantic_aggregate_sha256": "b" * 64,
        "source_commit": "c" * 40,
        "plugin_version": "0.2.3-preview.1",
        "exact_target_manifest_sha256": "d" * 64,
        "certification_protocol_version": "sim-live-v3",
        "transport": "OPENAI_PERSONAL_PLUGIN",
        "plugin_id": "plugins~Plugin_sim",
        "release_id": "release_exact",
        "current_release_id": "release_exact",
        "latest_release_id": "release_exact",
        "scope": "USER",
        "discoverability": "PRIVATE",
        "bundle_sha256": "e" * 64,
        "platform_release_tree_sha256": "f" * 64,
        "normalized_platform_tree_sha256": "a" * 64,
        "observed_public_skill_count": 1,
        "observed_public_skill_names": ["SIM"],
        "recorded_at": "2026-09-24T10:00:00Z",
    }
    jsonschema.Draft202012Validator(schema).validate(record)


def test_personal_release_binding_rejects_normalized_tree_mismatch() -> None:
    from tools.verify_sim_certification import _verify_personal_evidence_binding

    installation = {
        "plugin_id": "plugins~Plugin_sim",
        "release_id": "release_exact",
        "bundle_sha256": "a" * 64,
        "platform_release_tree_sha256": "b" * 64,
        "normalized_platform_tree_sha256": "c" * 64,
    }
    release = dict(installation)
    release["normalized_platform_tree_sha256"] = "d" * 64

    assert _verify_personal_evidence_binding(installation, release) == [
        "personal plugin normalized platform tree mismatch"
    ]


def test_certification_surfaces_verified_personal_release_before_installation(
    tmp_path: Path,
) -> None:
    from tools.build_sim_plugin import build_candidate
    from tools.verify_sim_certification import build_certification_report

    source_sha = "9e2d009743f5f405b31460936ad47651f0e3f832"
    candidate = tmp_path / "candidate"
    build_candidate(ROOT, source_sha, candidate)

    report = build_certification_report(
        ROOT,
        candidate,
        source_sha,
        ROOT / "work/evidence",
    )

    assert report["plugin_id"] == "plugins_6ab4ed6003b48191a0de271d4759c5e2"
    assert report["release_id"] == "pluginrel_6ab4f344b9888191b492884b8034f5b2"
    assert report["release_state"] == "PERSONAL_PLUGIN_BYTES_VERIFIED"
    assert report["surface_results"]["CHATGPT_WEB_NORMAL_CHAT"] == "INCOMPLETE"
    assert report["release_blocking_complete"] is False
