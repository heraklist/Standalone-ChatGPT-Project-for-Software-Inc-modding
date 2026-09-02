from __future__ import annotations

import json
from pathlib import Path


REQUIRED_PATHS = (
    "schemas/sim-session.schema.json",
    "schemas/sim-plan.schema.json",
    "schemas/sim-specialist-request.schema.json",
    "schemas/sim-specialist-result.schema.json",
    "schemas/sim-reference-map.schema.json",
    "schemas/sim-release-manifest.schema.json",
    "schemas/sim-eval.schema.json",
    "production/sim/manifests/sim-manifest.json",
    "production/sim/manifests/reference-source-map.json",
    "production/sim/manifests/compatibility-matrix.json",
)

MANIFEST_IDENTITY = {
    "product": "SIM",
    "display_name": "Software Inc Modding",
    "version": "0.2.0-preview",
    "channel": "PREVIEW",
    "canonical_game_target": "Beta 1.8.42",
    "evidence_grade": "GENERATION_GRADE",
}


def verify_sim_layout(root: Path) -> list[str]:
    errors = [
        f"missing SIM required path: {path}"
        for path in REQUIRED_PATHS
        if not (root / path).is_file()
    ]

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
    return errors
