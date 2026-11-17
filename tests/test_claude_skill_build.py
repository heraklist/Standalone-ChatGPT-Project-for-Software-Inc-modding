import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools.build_claude_skill import SKILL_NAME, build_skill
from tools.verify_repo import KNOWLEDGE_FILES


def test_skill_builds_with_valid_frontmatter_and_all_references(tmp_path):
    out, manifest = build_skill(ROOT, tmp_path / "claude")
    skill_md = (out / "skills" / SKILL_NAME / "SKILL.md").read_text(encoding="utf-8")

    assert skill_md.startswith(f"---\nname: {SKILL_NAME}\ndescription: ")
    # Claude skill descriptions are length-bounded; keep well under the limit.
    description_line = skill_md.splitlines()[2]
    assert len(description_line) < 1024

    refs = {p.name for p in (out / "skills" / SKILL_NAME / "references").iterdir()}
    assert refs == KNOWLEDGE_FILES
    assert manifest["reference_count"] == 18


def test_skill_body_is_the_single_source_instructions(tmp_path):
    out, _ = build_skill(ROOT, tmp_path / "claude")
    skill_md = (out / "skills" / SKILL_NAME / "SKILL.md").read_text(encoding="utf-8")
    instructions = (ROOT / "production/project-instructions/PROJECT_INSTRUCTIONS.md").read_text(encoding="utf-8")
    # The skill must not fork the content: the authored instructions appear verbatim.
    assert instructions.rstrip() in skill_md


def test_plugin_wrapper_version_tracks_pack_version(tmp_path):
    out, _ = build_skill(ROOT, tmp_path / "claude")
    plugin = json.loads((out / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"))
    pack = json.loads((ROOT / "production/manifests/knowledge-pack-manifest.json").read_text(encoding="utf-8"))
    assert plugin["version"] == pack["pack_version"]


def test_skill_build_is_deterministic(tmp_path):
    _, m1 = build_skill(ROOT, tmp_path / "a")
    _, m2 = build_skill(ROOT, tmp_path / "b")
    assert m1["file_sha256"] == m2["file_sha256"]
