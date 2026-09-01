from __future__ import annotations
from pathlib import Path

REQUIRED_DIRS=("archive","work","production","docs","schemas","tools","tests")
KNOWLEDGE_FILES={
"00_INDEX.md","01_EVIDENCE_VERSION_AND_TRUTH.md","02_MOD_ECOSYSTEM_AND_ROUTER.md","03_TYD_FOUNDATIONS.md","04_DATA_MODDING.md","05_SIPL.md","06_CODE_MODDING_CORE_AND_DISTRIBUTION.md","07_CODE_RUNTIME_UI_PERSISTENCE_SECURITY.md","08_FURNITURE.md","09_MATERIALS.md","10_LOCALIZATION.md","11_EDITOR_CONTENT_HARDWARE_BLUEPRINTS_BUILDINGS.md","12_DEBUGGING_CONSOLE_AND_RUNTIME.md","13_COMPATIBILITY_MIGRATION_AND_COLLISIONS.md","14_DISCOVERY_BRAINSTORM_AND_DESIGN.md","15_BUILD_EDIT_REPAIR_AND_DELIVERY.md","16_VERIFICATION_AND_QA.md","17_EVIDENCE_REGISTRY.json"}
META_KEYS=("document_id","title","knowledge_type","canonical_target_version","last_researched","last_runtime_verified","aliases","use_for","do_not_use_for","source_classes","currency_summary","known_version_gaps")

def verify(root:Path)->list[str]:
    errors=[]
    for name in REQUIRED_DIRS:
        if not (root/name).is_dir(): errors.append(f"missing repository root: {name}")
    ignore=root/'.gitignore'
    if not ignore.exists(): errors.append('missing .gitignore')
    else:
        text=ignore.read_text(encoding='utf-8')
        for required in ('.local-sources/','dist/'):
            if required not in text: errors.append(f'.gitignore missing {required}')
    kdir=root/'production/knowledge'
    if kdir.exists():
        actual={p.name for p in kdir.iterdir() if p.is_file()}
        if actual != KNOWLEDGE_FILES: errors.append(f'knowledge file set mismatch: {sorted(actual ^ KNOWLEDGE_FILES)}')
        for p in kdir.glob('*.md'):
            text=p.read_text(encoding='utf-8')
            if not text.startswith('---\n'): errors.append(f'{p.name}: missing metadata header'); continue
            head=text.split('---\n',2)[1]
            for key in META_KEYS:
                if f'{key}:' not in head: errors.append(f'{p.name}: metadata missing {key}')
    return errors

def main(root:Path|None=None)->int:
    repo=root or Path(__file__).resolve().parents[1]
    errors=verify(repo)
    for e in errors: print(e)
    return 1 if errors else 0
if __name__=='__main__': raise SystemExit(main())
