import csv, json, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from tools.scan_legacy_claims import PATTERNS, scan_text

VALID_ACTIONS={"KEEP","REWRITE","MERGE","DROP","ARCHIVE_ONLY","SUPERSEDED"}

def test_every_legacy_source_file_is_mapped():
    with (ROOT/"work/migration/legacy-file-map.csv").open(encoding="utf-8",newline="") as f:
        rows=list(csv.DictReader(f))
    assert len(rows)==77
    assert len({r["source_path"] for r in rows})==77
    assert all(r["action"] in VALID_ACTIONS for r in rows)
    assert all(r["review_status"]=="REVIEWED" for r in rows)

def test_critical_claims_have_no_unmapped_items():
    data=json.loads((ROOT/"work/migration/critical-claim-map.json").read_text(encoding="utf-8"))
    assert data["source_archive"]["entry_count"]==91
    assert data["source_archive"]["file_count"]==77
    assert len(data["claims"])>=15
    assert all(c["new_owner"] and c["evidence_status"] and c["action"] for c in data["claims"])
    assert all(c["action"]!="UNMAPPED" for c in data["claims"])

def test_scanner_covers_required_conflict_classes():
    required={
        "MODSPEC","SUPPORT_MATRIX","MODFORGE_ENGINE_TRUTH","GREEK_SEMICOLON",
        "LOWERCASE_BOOLEAN","UNIVERSAL_FIELD_ORDER","INVENTED_DATA_FEATURES",
        "INVENTED_DATA_ADDONS","INVENTED_DATA_MANUFACTURING","INVENTED_BUILDINGS",
        "INVENTED_BLUEPRINTS","TYD_SIPL_ARRAY_CONFUSION","C3_FORBIDS_VAR",
        "C3_FORBIDS_LINQ","ENUM_CAVEAT_NARROWED",
    }
    assert required <= set(PATTERNS)
    sample="""ModSpec support_matrix Greek semicolon lowercase-only boolean parser rule
    mandatory universal TyD field order Data/Features.tyd Data/AddOns.tyd Data/Manufacturing.tyd
    Mods/Buildings Mods/Blueprints TyD uses ~[a,b]
    C#3 forbids var; C#3 forbids LINQ; custom-enum-only straight .cs caveat.
    ModForge validator support is Software Inc engine truth."""
    assert required <= set(scan_text(sample))
