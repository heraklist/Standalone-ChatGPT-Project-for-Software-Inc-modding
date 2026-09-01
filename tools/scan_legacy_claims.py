from __future__ import annotations
import argparse, json, re
from pathlib import Path

PATTERNS = {
    "MODSPEC": r"\bModSpec\b",
    "SUPPORT_MATRIX": r"\bsupport_matrix\b",
    "MODFORGE_ENGINE_TRUTH": r"ModForge.{0,80}(validator|writer|support).{0,80}(engine|parser|Software Inc)",
    "GREEK_SEMICOLON": r"(Greek semicolon|ελληνικ[όο]\s+ερωτηματικ|Greek question mark)",
    "LOWERCASE_BOOLEAN": r"(lowercase[- ]only.{0,40}boolean|boolean.{0,40}lowercase[- ]only)",
    "UNIVERSAL_FIELD_ORDER": r"(mandatory universal TyD field order|field order.{0,60}(always|universal|mandatory))",
    "INVENTED_DATA_FEATURES": r"Data/Features\.tyd",
    "INVENTED_DATA_ADDONS": r"Data/AddOns\.tyd",
    "INVENTED_DATA_MANUFACTURING": r"Data/Manufacturing\.tyd",
    "INVENTED_BUILDINGS": r"Mods/Buildings",
    "INVENTED_BLUEPRINTS": r"Mods/Blueprints",
    "TYD_SIPL_ARRAY_CONFUSION": r"(TyD.{0,120}~\[|~\[.{0,120}TyD)",
    "C3_FORBIDS_VAR": r"C#\s*3.{0,80}forbids?\s+var",
    "C3_FORBIDS_LINQ": r"C#\s*3.{0,80}forbids?\s+LINQ",
    "ENUM_CAVEAT_NARROWED": r"(custom[- ]enum[- ]only|only custom enums).{0,100}(straight|game[- ]compiled|\.cs)",
}
TEXT_EXTS={".md",".txt",".json",".tyd",".cs",".csv"}

def scan_text(text: str):
    hits=[]
    for code,pattern in PATTERNS.items():
        if re.search(pattern,text,re.I|re.S):
            hits.append(code)
    return hits

def scan_tree(root: Path):
    findings=[]
    for path in sorted(root.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in TEXT_EXTS:
            continue
        try: text=path.read_text(encoding="utf-8",errors="replace")
        except OSError: continue
        hits=scan_text(text)
        if hits:
            findings.append({"path":str(path.relative_to(root)),"hits":hits})
    return findings

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("root",type=Path)
    ap.add_argument("--json",action="store_true")
    ns=ap.parse_args()
    findings=scan_tree(ns.root)
    if ns.json: print(json.dumps(findings,indent=2))
    else:
        for item in findings: print(f"{item['path']}: {','.join(item['hits'])}")
    return 1 if findings else 0

if __name__=="__main__":
    raise SystemExit(main())
