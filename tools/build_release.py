from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

from tools.validate_exact_target import generation_grade_errors
from tools.verify_repo import KNOWLEDGE_FILES, verify


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def build_release(root: Path, *, generation_grade: bool = False, out_dir: Path | None = None) -> tuple[Path, dict, dict]:
    errors = verify(root)
    if errors:
        raise RuntimeError("repository verification failed: " + "; ".join(errors))

    template_path = root / "work/corpus/beta-1.8.42/capture-manifest.template.json"
    exact_manifest = json.loads(template_path.read_text(encoding="utf-8"))
    gate_errors = generation_grade_errors(exact_manifest)
    if generation_grade and gate_errors:
        raise RuntimeError("generation-grade release blocked: " + "; ".join(gate_errors))

    kp_template = json.loads((root / "production/manifests/knowledge-pack-manifest.json").read_text(encoding="utf-8"))
    release_template = json.loads((root / "production/manifests/release-manifest.json").read_text(encoding="utf-8"))

    required = set(kp_template["mandatory_knowledge_files"])
    if required != KNOWLEDGE_FILES or len(required) != 18:
        raise RuntimeError("knowledge manifest must enumerate the exact 18-file canonical pack")

    payload: dict[str, bytes] = {}
    instructions = root / "production/project-instructions/PROJECT_INSTRUCTIONS.md"
    payload["project-instructions/PROJECT_INSTRUCTIONS.md"] = instructions.read_bytes()
    for name in sorted(required):
        payload[f"knowledge/{name}"] = (root / "production/knowledge" / name).read_bytes()

    file_hashes = {path: sha256_bytes(data) for path, data in sorted(payload.items())}
    kp = dict(kp_template)
    kp["project_instructions_sha256"] = file_hashes["project-instructions/PROJECT_INSTRUCTIONS.md"]
    kp["registry_sha256"] = file_hashes["knowledge/17_EVIDENCE_REGISTRY.json"]
    kp["file_sha256"] = file_hashes
    kp["exact_target_generation_grade"] = bool(generation_grade and not gate_errors)

    release = dict(release_template)
    release["release_status"] = "GENERATION_GRADE" if generation_grade else "STRUCTURAL_PREVIEW"
    release["generation_grade"] = bool(generation_grade)
    release["generated_at"] = datetime.now(timezone.utc).isoformat()
    release["exact_target_gate_errors"] = gate_errors

    kp_bytes = (json.dumps(kp, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    payload["manifests/knowledge-pack-manifest.json"] = kp_bytes

    # The release manifest records hashes for all non-self files. The ZIP digest is written to the returned report
    # after the archive is closed, avoiding a recursive self-hash dependency inside the ZIP payload.
    release["files"] = {path: sha256_bytes(data) for path, data in sorted(payload.items())}
    release["bundle_sha256"] = None
    release_bytes = (json.dumps(release, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    payload["manifests/release-manifest.json"] = release_bytes

    output = out_dir or (root / "dist")
    output.mkdir(parents=True, exist_ok=True)
    version = kp["pack_version"]
    zip_path = output / f"software-inc-mod-studio-project-{version}.zip"
    with ZipFile(zip_path, "w", compression=ZIP_DEFLATED) as archive:
        for path, data in sorted(payload.items()):
            archive.writestr(path, data)

    release["bundle_sha256"] = sha256_bytes(zip_path.read_bytes())
    report_path = output / f"software-inc-mod-studio-project-{version}.release-report.json"
    report_path.write_text(json.dumps(release, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return zip_path, kp, release


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--generation-grade", action="store_true")
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args(argv)
    try:
        zip_path, _, release = build_release(args.root, generation_grade=args.generation_grade)
    except RuntimeError as exc:
        print(exc)
        return 1
    print(zip_path)
    print(release["release_status"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
