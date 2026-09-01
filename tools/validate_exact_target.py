from __future__ import annotations
import argparse, json
from pathlib import Path

UNKNOWN={None,"","UNKNOWN"}

def generation_grade_errors(manifest: dict[str, object]) -> list[str]:
    errors=[]
    def miss(label, value):
        if value in UNKNOWN: errors.append(label)
    if manifest.get("game_version")!="Beta 1.8.42": errors.append("game_version must equal Beta 1.8.42")
    for key,label in [
        ("release_channel","missing release_channel"),
        ("platform","missing platform"),
        ("distribution","missing distribution"),
        ("capture_timestamp","missing capture_timestamp"),
        ("capture_method","missing capture_method"),
        ("vanilla_data_manifest_sha256","missing vanilla Data manifest hash"),
        ("localization_manifest_sha256","missing Localization manifest hash"),
        ("loader_root_snapshot_sha256","missing loader-root snapshot hash"),
        ("identifiers_collision_index_sha256","missing identifiers/collision index hash"),
    ]: miss(label, manifest.get(key))
    miss("missing executable SHA-256", manifest.get("executable_sha256"))
    assemblies=manifest.get("managed_assemblies")
    if not isinstance(assemblies,list) or not assemblies:
        errors.append("missing managed assembly hashes/versions/MVIDs")
    else:
        for item in assemblies:
            if not isinstance(item,dict) or any(item.get(k) in UNKNOWN for k in ("name","sha256","assembly_version","mvid")):
                errors.append("incomplete managed assembly evidence"); break
    code=manifest.get("code_api_surface")
    if not isinstance(code,dict) or not code.get("captured") or code.get("manifest_sha256") in UNKNOWN or not code.get("includes_persistence") or not code.get("includes_security"):
        errors.append("missing current Code persistence/security API surface")
    hw=manifest.get("hardware_design_observations")
    if not isinstance(hw,dict) or not hw.get("captured") or hw.get("manifest_sha256") in UNKNOWN:
        errors.append("missing current Hardware Design observations")
    return errors

def main(argv=None):
    ap=argparse.ArgumentParser()
    ap.add_argument("manifest", nargs="?", default="work/corpus/beta-1.8.42/capture-manifest.template.json")
    ap.add_argument("--structural", action="store_true")
    ns=ap.parse_args(argv)
    path=Path(ns.manifest)
    data=json.loads(path.read_text(encoding="utf-8"))
    errors=generation_grade_errors(data)
    if ns.structural:
        if not errors:
            print("structural gate error: template unexpectedly qualifies as generation-grade")
            return 1
        print(f"STRUCTURAL_OK: exact-target generation-grade remains blocked by {len(errors)} evidence requirements")
        return 0
    for e in errors: print(e)
    return 1 if errors else 0

if __name__=="__main__": raise SystemExit(main())
