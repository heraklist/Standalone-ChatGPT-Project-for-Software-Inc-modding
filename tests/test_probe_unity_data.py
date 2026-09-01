from pathlib import Path
import hashlib
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools.probe_unity_data import (
    TARGET_ASSETS,
    build_textasset_record,
    find_relevant_tokens,
    safe_component,
)


def test_target_assets_are_exact_three_observed_containers():
    assert set(TARGET_ASSETS) == {
        "Software Inc_Data/globalgamemanagers.assets",
        "Software Inc_Data/resources.assets",
        "Software Inc_Data/sharedassets2.assets",
    }
    assert all(len(digest) == 64 for digest in TARGET_ASSETS.values())


def test_find_relevant_tokens_is_case_insensitive_and_stable():
    payload = b"softwaretype foo HARDWAREDESIGN bar companytype"
    assert find_relevant_tokens(payload) == ["SoftwareType", "CompanyType", "HardwareDesign"]


def test_textasset_record_hashes_payload_without_embedding_raw_content():
    payload = b'SoftwareType "Example" { }'
    record = build_textasset_record(
        source_asset="Software Inc_Data/resources.assets",
        path_id=42,
        object_name="Software Types",
        payload=payload,
    )
    assert record["payload_sha256"] == hashlib.sha256(payload).hexdigest()
    assert record["payload_size"] == len(payload)
    assert record["tokens"] == ["SoftwareType"]
    assert "payload" not in record
    assert "raw" not in record


def test_safe_component_removes_path_and_windows_reserved_characters():
    assert safe_component('Hardware:Design/Primary*?') == 'Hardware_Design_Primary__'


def test_get_textasset_payload_roundtrips_surrogateescaped_binary():
    class Dummy:
        m_Script = b'\x8bABC\xd2'.decode('utf-8', 'surrogateescape')
    from tools.probe_unity_data import _get_textasset_payload
    assert _get_textasset_payload(Dummy()) == b'\x8bABC\xd2'


def test_private_textasset_path_uses_path_id_not_object_name():
    from tools.probe_unity_data import private_textasset_path
    path = private_textasset_path(
        'Software Inc_Data/resources.assets',
        624,
        '\udc8bBad/Name',
    )
    assert path.as_posix() == 'PRIVATE-EVIDENCE/textassets/resources.assets/624.bin'


def test_all_textassets_are_private_export_candidates_even_without_tokens():
    from tools.probe_unity_data import should_export_private_textasset
    record = {
        'source_asset': 'Software Inc_Data/resources.assets',
        'path_id': 625,
        'object_name': 'femalefirstnames',
        'payload_size': 3,
        'payload_sha256': '0' * 64,
        'tokens': [],
    }
    assert should_export_private_textasset(record) is True
