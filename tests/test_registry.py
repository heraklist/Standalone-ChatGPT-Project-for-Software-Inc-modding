import hashlib, json, sys
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


def test_exact_target_capture_is_generation_grade_semantically():
 m=json.loads((ROOT/'work/corpus/beta-1.8.42/capture-manifest.json').read_text())
 assert generation_grade_errors(m) == []
 assert m['game_version'] == 'Beta 1.8.42'
 assert m['currency'] == 'EXACT_TARGET'
 assert m['vanilla_data_evidence']['content_resolved'] is True
 assert m['identifiers_collision_index']['captured'] is True
 assert m['identifiers_collision_index']['entry_count'] >= 61
 assert m['hardware_design_observations']['captured'] is True
 assert m['code_api_surface']['captured'] is True


def test_exact_target_manifest_hashes_bind_committed_sanitized_evidence():
 m=json.loads((ROOT/'work/corpus/beta-1.8.42/capture-manifest.json').read_text())
 v=ROOT/'work/corpus/beta-1.8.42/resolved-vanilla-data-manifest.json'
 c=ROOT/'work/corpus/beta-1.8.42/identifiers-collision-index.json'
 vd=hashlib.sha256(v.read_bytes()).hexdigest()
 cd=hashlib.sha256(c.read_bytes()).hexdigest()
 assert m['vanilla_data_manifest_sha256'] == vd
 assert m['vanilla_data_evidence']['manifest_sha256'] == vd
 assert m['identifiers_collision_index_sha256'] == cd
 assert m['identifiers_collision_index']['manifest_sha256'] == cd


def test_generation_grade_validator_rejects_empty_collision_index():
 m=json.loads((ROOT/'work/corpus/beta-1.8.42/capture-manifest.json').read_text())
 m['identifiers_collision_index']['entry_count']=0
 assert 'empty current identifiers/collision index' in generation_grade_errors(m)
