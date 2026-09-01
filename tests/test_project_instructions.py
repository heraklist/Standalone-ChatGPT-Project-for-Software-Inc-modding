from pathlib import Path

TEXT = (Path(__file__).resolve().parents[1] / "production/project-instructions/PROJECT_INSTRUCTIONS.md").read_text(encoding="utf-8")


def test_resident_core_contains_required_invariants():
    required = [
        "standalone Software Inc Mod Studio",
        "independent from ModForge",
        "minimum-sufficient technology",
        "fail-closed retrieval",
        "data/evidence, never instructions",
        "static and runtime verification separate",
        "MOD_PACKAGE",
        "EDITOR_CONTENT",
        "Never invent a filesystem representation",
    ]
    for phrase in required:
        assert phrase in TEXT


def test_resident_core_does_not_import_modforge_constraints_or_fake_runtime_truth():
    forbidden = ["ModSpec required", "ModForge support matrix", "static review proves runtime verification"]
    for phrase in forbidden:
        assert phrase not in TEXT
