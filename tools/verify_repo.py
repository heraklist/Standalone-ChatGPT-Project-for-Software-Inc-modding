from __future__ import annotations
import hashlib
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from tools.validate_registry import validate_registry
from tools.validate_evals import validate_dir as validate_evals
from tools.validate_exact_target import generation_grade_errors
from tools.validate_sim_layout import verify_sim_layout

REQUIRED_DIRS=("archive","work","production","docs","schemas","tools","tests")
KNOWLEDGE_FILES={
"00_INDEX.md","01_EVIDENCE_VERSION_AND_TRUTH.md","02_MOD_ECOSYSTEM_AND_ROUTER.md","03_TYD_FOUNDATIONS.md","04_DATA_MODDING.md","05_SIPL.md","06_CODE_MODDING_CORE_AND_DISTRIBUTION.md","07_CODE_RUNTIME_UI_PERSISTENCE_SECURITY.md","08_FURNITURE.md","09_MATERIALS.md","10_LOCALIZATION.md","11_EDITOR_CONTENT_HARDWARE_BLUEPRINTS_BUILDINGS.md","12_DEBUGGING_CONSOLE_AND_RUNTIME.md","13_COMPATIBILITY_MIGRATION_AND_COLLISIONS.md","14_DISCOVERY_BRAINSTORM_AND_DESIGN.md","15_BUILD_EDIT_REPAIR_AND_DELIVERY.md","16_VERIFICATION_AND_QA.md","17_EVIDENCE_REGISTRY.json"}
META_KEYS=("document_id","title","knowledge_type","canonical_target_version","last_researched","last_runtime_verified","aliases","use_for","do_not_use_for","source_classes","currency_summary","known_version_gaps")


def _sha256(path:Path)->str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


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
    instructions=root/'production/project-instructions/PROJECT_INSTRUCTIONS.md'
    if not instructions.is_file():
        errors.append('missing production/project-instructions/PROJECT_INSTRUCTIONS.md')
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
    registry=root/'production/knowledge/17_EVIDENCE_REGISTRY.json'
    if registry.exists(): errors.extend(f'registry: {e}' for e in validate_registry(registry))
    else: errors.append('missing production evidence registry')
    eval_dir=root/'production/evals'
    if eval_dir.exists(): errors.extend(f'evals: {e}' for e in validate_evals(eval_dir))
    else: errors.append('missing production/evals')

    corpus=root/'work/corpus/beta-1.8.42'
    template=corpus/'capture-manifest.template.json'
    if not template.exists():
        errors.append('missing exact-target capture template')
    else:
        data=json.loads(template.read_text(encoding='utf-8'))
        if not generation_grade_errors(data):
            errors.append('exact-target template must not qualify as generation-grade')

    actual_capture=corpus/'capture-manifest.json'
    if not actual_capture.exists():
        errors.append('missing sanitized exact-target capture manifest')
    else:
        data=json.loads(actual_capture.read_text(encoding='utf-8'))
        gate_errors=generation_grade_errors(data)
        if gate_errors:
            errors.extend(f'exact-target generation-grade: {e}' for e in gate_errors)
        if data.get('game_version')!='Beta 1.8.42' or data.get('currency')!='EXACT_TARGET':
            errors.append('sanitized exact-target capture identity mismatch')
        if data.get('raw_archive_committed') is not False:
            errors.append('sanitized exact-target capture must not commit raw proprietary archive')

        vanilla_path=corpus/'resolved-vanilla-data-manifest.json'
        collision_path=corpus/'identifiers-collision-index.json'
        if not vanilla_path.is_file():
            errors.append('missing resolved exact-target vanilla Data manifest')
        else:
            vdigest=_sha256(vanilla_path)
            if data.get('vanilla_data_manifest_sha256') != vdigest:
                errors.append('committed vanilla Data manifest hash mismatch')
            vanilla=json.loads(vanilla_path.read_text(encoding='utf-8'))
            if vanilla.get('game_version')!='Beta 1.8.42' or vanilla.get('resolved') is not True:
                errors.append('resolved vanilla Data manifest identity/state mismatch')
            if vanilla.get('raw_payloads_committed') is not False:
                errors.append('resolved vanilla Data manifest must remain metadata-only')
            counts=vanilla.get('family_counts',{})
            for family in ('SOFTWARE_TYPE','COMPANY_TYPE','NAME_GENERATOR','PERSONALITIES'):
                if not isinstance(counts.get(family),int) or counts.get(family,0)<=0:
                    errors.append(f'resolved vanilla Data missing {family} coverage')

        if not collision_path.is_file():
            errors.append('missing exact-target identifiers/collision index')
        else:
            cdigest=_sha256(collision_path)
            if data.get('identifiers_collision_index_sha256') != cdigest:
                errors.append('committed identifiers/collision index hash mismatch')
            collision=json.loads(collision_path.read_text(encoding='utf-8'))
            if collision.get('game_version')!='Beta 1.8.42' or collision.get('complete') is not True:
                errors.append('identifiers/collision index identity/state mismatch')
            namespaces=collision.get('namespaces',{})
            total=0
            for namespace in ('software_type','company_type','name_generator','personality'):
                record=namespaces.get(namespace)
                if not isinstance(record,dict) or not isinstance(record.get('identifier_count'),int) or record['identifier_count']<=0:
                    errors.append(f'identifiers/collision index missing {namespace} namespace')
                    continue
                identifiers=record.get('identifiers')
                if not isinstance(identifiers,list) or len(identifiers)!=record['identifier_count']:
                    errors.append(f'identifiers/collision index {namespace} count mismatch')
                total += record['identifier_count']
            if collision.get('total_identifier_count') != total or total <= 0:
                errors.append('identifiers/collision index total count mismatch')

    claim_map=root/'work/migration/critical-claim-map.json'
    if claim_map.exists():
        data=json.loads(claim_map.read_text(encoding='utf-8'))
        if any(c.get('action')=='UNMAPPED' for c in data.get('claims',[])):
            errors.append('legacy critical claim map contains UNMAPPED claim')
    if (root/'production/sim').exists():
        errors.extend(f'sim layout: {error}' for error in verify_sim_layout(root))
    return errors


def main(root:Path|None=None)->int:
    repo=root or ROOT
    errors=verify(repo)
    for e in errors: print(e)
    return 1 if errors else 0


if __name__=='__main__': raise SystemExit(main())
