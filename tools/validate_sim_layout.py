from __future__ import annotations

import json
from pathlib import Path


LIFECYCLE_MODULES = {
    "research-evidence",
    "brainstorm-design",
    "implementation",
    "systematic-debugging",
    "verification-delivery",
}

REQUIRED_DOMAIN_MODULES = {
    "code-modding",
    "compatibility-packaging",
    "data-tyd",
    "editor-native",
    "furniture",
    "localization",
    "materials",
    "sipl",
}

REQUIRED_PATHS = (
    "schemas/sim-session.schema.json",
    "schemas/sim-plan.schema.json",
    "schemas/sim-specialist-request.schema.json",
    "schemas/sim-specialist-result.schema.json",
    "schemas/sim-reference-map.schema.json",
    "schemas/sim-release-manifest.schema.json",
    "schemas/sim-eval.schema.json",
    "production/sim/SKILL.md",
    "production/sim/manifests/sim-manifest.json",
    "production/sim/manifests/reference-source-map.json",
    "production/sim/manifests/compatibility-matrix.json",
    *(f"production/sim/lifecycle/{name}/SKILL.md" for name in sorted(LIFECYCLE_MODULES)),
    *(f"production/sim/domains/{name}/SKILL.md" for name in sorted(REQUIRED_DOMAIN_MODULES)),
)

MANIFEST_IDENTITY = {
    "product": "SIM",
    "display_name": "Software Inc Modding",
    "version": "0.2.0-preview",
    "channel": "PREVIEW",
    "canonical_game_target": "Beta 1.8.42",
    "evidence_grade": "GENERATION_GRADE",
}


def _skill_frontmatter_name(text: str) -> str | None:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None
    for line in lines[1:]:
        stripped = line.strip()
        if stripped == "---":
            return None
        if stripped.startswith("name:"):
            return stripped.partition(":")[2].strip()
    return None


def verify_sim_layout(root: Path) -> list[str]:
    errors = [
        f"missing SIM required path: {path}"
        for path in REQUIRED_PATHS
        if not (root / path).is_file()
    ]

    lifecycle_root = root / "production/sim/lifecycle"
    if lifecycle_root.is_dir():
        actual_modules = {path.name for path in lifecycle_root.iterdir() if path.is_dir()}
        for name in sorted(actual_modules - LIFECYCLE_MODULES):
            errors.append(f"unexpected SIM lifecycle module: {name}")

    domain_root = root / "production/sim/domains"
    if domain_root.is_dir():
        actual_domains = {path.name for path in domain_root.iterdir() if path.is_dir()}
        for name in sorted(actual_domains - REQUIRED_DOMAIN_MODULES):
            errors.append(f"unexpected SIM domain module: {name}")

    manifest_path = root / "production/sim/manifests/sim-manifest.json"
    if not manifest_path.is_file():
        return errors

    try:
        manifest_text = manifest_path.read_text(encoding="utf-8")
    except UnicodeError:
        return [*errors, "SIM manifest is not valid UTF-8"]
    except OSError:
        return [*errors, "SIM manifest could not be read"]

    try:
        manifest = json.loads(manifest_text)
    except json.JSONDecodeError:
        return [*errors, "SIM manifest is not valid JSON"]
    if not isinstance(manifest, dict):
        return [*errors, "SIM manifest must be a JSON object"]

    for key, expected in MANIFEST_IDENTITY.items():
        if manifest.get(key) != expected:
            errors.append(f"SIM manifest identity mismatch: {key}")

    skill_path = root / "production/sim/SKILL.md"
    if skill_path.is_file():
        try:
            skill_text = skill_path.read_text(encoding="utf-8")
        except UnicodeError:
            errors.append("SIM skill is not valid UTF-8")
        except OSError:
            errors.append("SIM skill could not be read")
        else:
            if _skill_frontmatter_name(skill_text) != "sim":
                errors.append("SIM skill frontmatter name must be sim")

    return errors
