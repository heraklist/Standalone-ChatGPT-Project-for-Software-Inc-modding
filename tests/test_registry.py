import json, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT))
from tools.validate_registry import validate_registry

def test_registry_has_required_critical_claims():
 r=json.loads((ROOT/'production/knowledge/17_EVIDENCE_REGISTRY.json').read_text())
 required={'tyd_fork_authority','tyd_sipl_array_boundary','data_public_folder_taxonomy','override_true_partial','amountscript_context','sipl_entrypoints_runtype','code_csharp3_workshop','code_enum_caveat','playerprefs_block','swinc_symbols','code_ui_linked_engine','furniture_contract','material_contract','localization_name_lists','reload_mod_caveat','scenario_no_current_surface','building_blueprint_schema_unverified','exact_target_release_gate'}
 assert required <= set(r['claims'])
 assert validate_registry(ROOT/'production/knowledge/17_EVIDENCE_REGISTRY.json') == []

def test_media_records_are_metadata_only_and_parented():
 r=json.loads((ROOT/'production/knowledge/17_EVIDENCE_REGISTRY.json').read_text())
 assert len(r['media'])==8
 for m in r['media'].values():
  assert m['raw_committed'] is False
  assert len(m['sha256'])==64 and m['width']>0 and m['height']>0
  assert m['parent_source'] in r['sources']
  for c in m['supported_claims']: assert c in r['claims']

def test_linked_engine_sources_remain_scoped():
 r=json.loads((ROOT/'production/knowledge/17_EVIDENCE_REGISTRY.json').read_text())
 linked=[s for s in r['sources'].values() if s['source_role']=='LINKED_ENGINE_API']
 assert len(linked)==5
 assert all(s['currency']=='UNKNOWN_VERSION' and s['delegated_by']=='code_modding' for s in linked)
