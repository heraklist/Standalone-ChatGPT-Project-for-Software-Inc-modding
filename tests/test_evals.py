import json, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from tools.validate_evals import validate_dir

def load(name): return json.loads((ROOT/'production/evals'/name).read_text(encoding='utf-8'))

def test_core_ids_are_exactly_e01_e74():
    data=load('core.json')
    assert [r['id'] for r in data]==[f'E{i:02d}' for i in range(1,75)]
    assert len({r['id'] for r in data})==74

def test_core_records_have_nonempty_required_and_forbidden_assertions():
    for r in load('core.json'):
        assert r['severity'] in {'P0','P1','P2','P3'}
        assert r['required_assertions']
        assert r['forbidden_assertions']
        assert r['prompt'].strip()

def test_combined_canonical_severities_are_fail_safe_p0():
    by_id={r['id']:r for r in load('core.json')}
    for eid in ('E16','E64'):
        assert by_id[eid]['severity']=='P0'
        assert by_id[eid]['canonical_severity']=='P0/P1'

def test_final_reconciliation_cases_preserve_key_semantics():
    by_id={r['id']:r for r in load('core.json')}
    assert 'expression-bodied' in ' '.join(by_id['E65']['forbidden_assertions'])
    assert 'partial override' in ' '.join(by_id['E66']['required_assertions'])
    assert '~[...]' in ' '.join(by_id['E67']['forbidden_assertions'])
    assert 'Replace True' in by_id['E68']['prompt']
    assert 'Data/Features.tyd' in by_id['E69']['prompt']
    assert '/Mods/Buildings' in by_id['E70']['prompt']
    assert 'Software Inc_Data/Managed' in by_id['E71']['prompt']
    assert 'RELOAD_FURNITURE_MOD' in by_id['E72']['prompt']
    assert 'femalefirstnames.txt' in by_id['E73']['prompt']
    assert 'enum usage' in ' '.join(by_id['E74']['forbidden_assertions'])

def test_auxiliary_suites_present_and_nonempty():
    assert [r['id'] for r in load('retrieval.json')]==['RET-01','RET-02','RET-03']
    assert len(load('security.json'))>=4
    assert [r['id'] for r in load('multi_turn.json')]==['M01','M02','M03']
    assert len(load('migration.json'))>=4

def test_eval_validator_passes():
    assert validate_dir(ROOT/'production/evals')==[]
