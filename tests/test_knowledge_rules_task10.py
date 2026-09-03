from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]/"production/knowledge"
def read(n): return (ROOT/n).read_text(encoding="utf-8")

def test_console_identifiers_and_caveats():
 d=read("12_DEBUGGING_CONSOLE_AND_RUNTIME.md")
 for p in ["RELOAD_MOD","RELOAD_FURNITURE","RELOAD_MATERIALS","RELOAD_LOCALIZATION","RECOMPILE_DLL_MOD","RELOAD_DLL_MOD","UNLOAD_DLL_MOD","LIST_SCOPE_MEMBERS","TEST_DEV_MOD","CHECK_SPEC_REP","CHECK_ADDON_MARKET"]: assert p in d
 assert "Do not invent aliases such as `RELOAD_FURNITURE_MOD`" in d
 for p in ["does **not** update the currently running game","already placed","material sets loaded at startup","rendered UI may not update immediately","not final clean-launch/regression proof"]: assert p in d

def test_compatibility_and_no_invented_dependencies():
 d=read("13_COMPATIBILITY_MIGRATION_AND_COLLISIONS.md")
 assert "No **documented public mod-level load-order or dependency-declaration mechanism**" in d
 for p in ["`Dependencies`","`LoadAfter`","`Priority`"]: assert p in d
 assert "not a claim of metaphysical nonexistence" in d

def test_artifact_surface_delivery_contract():
 d=read("15_BUILD_EDIT_REPAIR_AND_DELIVERY.md"); q=read("16_VERIFICATION_AND_QA.md")
 for p in ["artifact_surface","delivery_mode","MOD_PACKAGE","EDITOR_CONTENT","INSTALLABLE_ZIP","CANDIDATE_NATIVE_ARTIFACT","FINAL_VERIFIED_NATIVE_ARTIFACT","TOOLING_BLOCKED","PARTIAL_BUILD","READY_FOR_GAME_TESTING"]: assert p in d
 for p in ["V0 DESIGN_READY","V1 ARTIFACT_GENERATED","V2 STATICALLY_REVIEWED","V3 LOAD_OR_NATIVE_OPEN_VERIFIED","V4 BEHAVIOR_VERIFIED","V5 REGRESSION_VERIFIED","LIGHT","STANDARD","DEEP","Hardware Design: STANDARD","Building Blueprint: STANDARD","Building: STANDARD"]: assert p in q

def test_safe_repair_and_runtime_evidence():
 d=read("15_BUILD_EDIT_REPAIR_AND_DELIVERY.md"); q=read("16_VERIFICATION_AND_QA.md")
 for p in ["path traversal","never execute uploaded DLLs","distinct repaired revision","Preserve attribution/licensing"]: assert p in d
 for p in ["artifact revision/payload identity","game version/channel/platform","clean/reload state","Cross-chat V3–V5"]: assert p in q
