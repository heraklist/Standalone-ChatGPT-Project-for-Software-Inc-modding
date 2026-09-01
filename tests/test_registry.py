import json, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT))
from tools.validate_registry import validate_registry
from tools.validate_exact_target import generation_grade_errors


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


def test_exact_target_template_fails_closed():
 m=json.loads((ROOT/'work/corpus/beta-1.8.42/capture-manifest.template.json').read_text())
 errors=generation_grade_errors(m)
 expected={'missing release_channel','missing platform','missing distribution','missing capture_timestamp','missing capture_method','missing executable SHA-256','missing managed assembly hashes/versions/MVIDs','missing vanilla Data manifest hash','missing Localization manifest hash','missing loader-root snapshot hash','missing identifiers/collision index hash','missing current Code persistence/security API surface','missing current Hardware Design observations','missing current vanilla Data evidence','missing current identifiers/collision index evidence'}
 assert expected <= set(errors)


def test_partial_exact_target_capture_stays_fail_closed_semantically():
 m=json.loads((ROOT/'work/corpus/beta-1.8.42/capture-manifest.json').read_text())
 errors=generation_grade_errors(m)
 assert 'vanilla Data content unresolved' in errors
 assert 'missing current identifiers/collision index evidence' in errors
 assert 'missing current Hardware Design observations' not in errors
 assert 'missing current Code persistence/security API surface' not in errors
 assert 'missing Steam build ID' not in errors


def test_generation_grade_manifest_passes_when_semantically_complete():
 m=json.loads((ROOT/'work/corpus/beta-1.8.42/capture-manifest.json').read_text())
 h='a'*64
 m['vanilla_data_manifest_sha256']=h
 m['identifiers_collision_index_sha256']=h
 m['vanilla_data_evidence']={'captured':True,'manifest_sha256':h,'scope_isolated':True,'content_resolved':True}
 m['identifiers_collision_index']={'captured':True,'manifest_sha256':h,'entry_count':1}
 assert generation_grade_errors(m)==[]
