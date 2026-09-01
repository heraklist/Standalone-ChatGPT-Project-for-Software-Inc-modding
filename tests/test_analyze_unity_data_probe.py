from pathlib import Path
import hashlib
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools.analyze_unity_data_probe import classify_payload, extract_top_level_identifiers, analyze_records


def test_classifies_supported_data_families():
    fixtures = {
        'SOFTWARE_TYPE': b'SoftwareType\n{\n Name "Operating System"\n Categories [ ]\n}',
        'COMPANY_TYPE': b'CompanyType\n{\n Specialization "Antivirus"\n}',
        'PERSONALITIES': b'PersonalityGraph\n{\n Personalities [ { Name Generous } ]\n}',
        'HARDWARE_DESIGN': b'Design\n{\n ID CellPhone\n Name Cellphone\n BaseMesh Base\n Objects [ ]\n}',
        'NAME_GENERATOR': b'-start(base)\n-base(stop)\nFoo\n',
    }
    for expected, payload in fixtures.items():
        assert classify_payload(payload) == expected


def test_rejects_false_positive_text_that_mentions_family_names():
    assert classify_payload(b'Patch note: fixed SoftwareType UI and HardwareDesign button') == 'OTHER'
    assert classify_payload(b'UI label Personalities') == 'OTHER'


def test_extracts_top_level_identifiers_by_family():
    assert extract_top_level_identifiers('SOFTWARE_TYPE', '01 Operating System', b'SoftwareType\n{\n Name "Operating System"\n Categories [ ]\n}') == ['Operating System']
    assert extract_top_level_identifiers('COMPANY_TYPE', 'Antivirus', b'CompanyType\n{\n Specialization "Antivirus"\n}') == ['Antivirus']
    assert extract_top_level_identifiers('NAME_GENERATOR', 'OS', b'-start(base)\n-base(stop)\nDoor\n') == ['OS']
    assert extract_top_level_identifiers('HARDWARE_DESIGN', 'CellPhone', b'Design {\n ID CellPhone\n Name Cellphone\n BaseMesh Base\n Objects [ ]\n}') == ['CellPhone']


def test_personality_identifier_extraction_gets_personality_names_not_graph_label():
    payload = b'''PersonalityGraph
    {
    Personalities
        [
            { Name Generous Traits [ Humble ] }
            { Name Optimistic Traits [ Active ] }
        ]
    Incompatibilities [ ]
    }'''
    assert extract_top_level_identifiers('PERSONALITIES', 'Personalities', payload) == ['Generous', 'Optimistic']


def test_analyze_records_requires_private_payload_for_every_manifest_record():
    records = [
        {'path_id': 1, 'object_name': 'OS', 'payload_sha256': 'x', 'payload_size': 1, 'private_path': 'PRIVATE/1.bin'}
    ]
    result = analyze_records(records, {})
    assert result['complete'] is False
    assert result['missing_payload_path_ids'] == [1]


def test_analyze_records_builds_nonempty_collision_namespaces():
    payloads = {
        'PRIVATE/1.bin': b'SoftwareType { Name "Operating System" Categories [ ] }',
        'PRIVATE/2.bin': b'CompanyType { Specialization "Antivirus" }',
        'PRIVATE/3.bin': b'-start(stop)\n',
        'PRIVATE/4.bin': b'PersonalityGraph { Personalities [ { Name Generous } ] }',
        'PRIVATE/5.bin': b'Design { ID CellPhone Name Cellphone BaseMesh Base Objects [ ] }',
    }
    records = []
    names = ['01 Operating System', 'Antivirus', 'None', 'Personalities', 'CellPhone']
    for i, (path, payload) in enumerate(payloads.items(), start=1):
        records.append({'path_id': i, 'object_name': names[i-1], 'payload_sha256': hashlib.sha256(payload).hexdigest(), 'payload_size': len(payload), 'private_path': path})
    result = analyze_records(records, payloads)
    assert result['complete'] is True
    assert result['family_counts'] == {
        'SOFTWARE_TYPE': 1, 'COMPANY_TYPE': 1, 'NAME_GENERATOR': 1, 'PERSONALITIES': 1, 'HARDWARE_DESIGN': 1, 'OTHER': 0
    }
    assert set(result['collision_index']['namespaces']) >= {'software_type', 'company_type', 'name_generator', 'personality', 'hardware_design'}


def test_write_and_bundle_outputs_are_metadata_only(tmp_path):
    from tools.analyze_unity_data_probe import write_sanitized_outputs, create_sanitized_bundle
    result = {
        'complete': True,
        'probe_zip_sha256': 'a' * 64,
        'family_counts': {'SOFTWARE_TYPE':1,'COMPANY_TYPE':1,'NAME_GENERATOR':1,'PERSONALITIES':1,'HARDWARE_DESIGN':0,'OTHER':0},
        'data_entries': [{'family':'SOFTWARE_TYPE','canonical_path':'SoftwareTypes/Test.tyd','source_asset':'resources.assets','path_id':1,'object_name':'Test','payload_size':1,'payload_sha256':'b'*64,'identifiers':['Test']}],
        'collision_index': {'namespaces': {'software_type': {'identifier_count':1,'identifiers':[{'identifier':'Test','occurrences':[]}]}}, 'collisions': [], 'total_identifier_count':1},
        'missing_payload_path_ids': [],
        'hash_or_size_mismatch_path_ids': [],
    }
    out = tmp_path / 'analysis'
    write_sanitized_outputs(result, out)
    bundle = create_sanitized_bundle(out, tmp_path / 'Beta1842-sanitized-analysis.zip')
    import zipfile
    with zipfile.ZipFile(bundle) as zf:
        assert set(zf.namelist()) == {'resolved-vanilla-data-manifest.json','identifiers-collision-index.json','analysis-summary.json'}
        assert not any(name.startswith('PRIVATE-EVIDENCE') for name in zf.namelist())
