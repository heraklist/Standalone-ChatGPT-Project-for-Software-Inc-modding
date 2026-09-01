from __future__ import annotations

import argparse
import hashlib
import json
import re
import zipfile
from collections import Counter, defaultdict
from pathlib import Path

FAMILIES = ('SOFTWARE_TYPE','COMPANY_TYPE','NAME_GENERATOR','PERSONALITIES','HARDWARE_DESIGN','OTHER')
NS_BY_FAMILY = {
    'SOFTWARE_TYPE':'software_type',
    'COMPANY_TYPE':'company_type',
    'NAME_GENERATOR':'name_generator',
    'PERSONALITIES':'personality',
    'HARDWARE_DESIGN':'hardware_design',
}


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _text(payload: bytes) -> str:
    return payload.decode('utf-8-sig', errors='surrogateescape')


def classify_payload(payload: bytes) -> str:
    text = _text(payload)
    if re.match(r'^\s*SoftwareType\b\s*\{', text, flags=re.S):
        return 'SOFTWARE_TYPE'
    if re.match(r'^\s*CompanyType\b\s*\{', text, flags=re.S):
        return 'COMPANY_TYPE'
    if re.match(r'^\s*PersonalityGraph\b\s*\{', text, flags=re.S):
        return 'PERSONALITIES'
    if re.match(r'^\s*Design\b\s*\{', text, flags=re.S) and re.search(r'\bID\s+', text) and re.search(r'\bBaseMesh\s+', text) and re.search(r'\bObjects\s*\[', text):
        return 'HARDWARE_DESIGN'
    lines = [line.strip() for line in text.replace('\r','').split('\n') if line.strip()]
    if lines and lines[0] == '[REPLACE]':
        lines = lines[1:]
    if lines and re.match(r'^-start\s*\(', lines[0], flags=re.I):
        return 'NAME_GENERATOR'
    return 'OTHER'


def _unquote(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == '"' and value[-1] == '"':
        value = value[1:-1]
        value = value.replace('\\"','"').replace('\\\\','\\')
    return value.strip()


def _first_field(text: str, field: str) -> str | None:
    m = re.search(rf'\b{re.escape(field)}\s+("(?:\\.|[^"\\])*"|[^\s#;\]\}}]+)', text)
    return _unquote(m.group(1)) if m else None


def extract_top_level_identifiers(family: str, object_name: str, payload: bytes) -> list[str]:
    text = _text(payload)
    if family == 'SOFTWARE_TYPE':
        value = _first_field(text, 'Name')
        return [value] if value else []
    if family == 'COMPANY_TYPE':
        return [object_name] if object_name else []
    if family == 'NAME_GENERATOR':
        return [object_name] if object_name else []
    if family == 'HARDWARE_DESIGN':
        value = _first_field(text, 'ID')
        return [value] if value else []
    if family == 'PERSONALITIES':
        start = re.search(r'\bPersonalities\b\s*\[', text)
        if not start:
            return []
        tail = text[start.end():]
        end = re.search(r'(?m)^\s*Incompatibilities\b', tail)
        section = tail[:end.start()] if end else tail
        values=[]
        for m in re.finditer(r'(?m)^\s*\{?\s*Name\s+("(?:\\.|[^"\\])*"|[^\s#;\]\}}]+)', section):
            value=_unquote(m.group(1))
            if value and value not in values:
                values.append(value)
        return values
    return []


def _canonical_path(family: str, object_name: str) -> str | None:
    if family == 'SOFTWARE_TYPE': return f'SoftwareTypes/{object_name}.tyd'
    if family == 'COMPANY_TYPE': return f'CompanyTypes/{object_name}.tyd'
    if family == 'NAME_GENERATOR': return f'NameGenerators/{object_name}.txt'
    if family == 'PERSONALITIES': return 'Personalities.tyd'
    if family == 'HARDWARE_DESIGN': return f'HardwareDesign/{object_name}.tyd'
    return None


def analyze_records(records: list[dict], payloads: dict[str, bytes]) -> dict:
    missing=[]
    mismatches=[]
    family_counts=Counter({k:0 for k in FAMILIES})
    data_entries=[]
    ns=defaultdict(list)

    for record in records:
        path_id=int(record.get('path_id',-1))
        private_path=record.get('private_path')
        payload=payloads.get(private_path) if isinstance(private_path,str) else None
        if payload is None:
            missing.append(path_id)
            continue
        expected_size=record.get('payload_size')
        expected_hash=record.get('payload_sha256')
        actual_hash=sha256_bytes(payload)
        if expected_size != len(payload) or expected_hash != actual_hash:
            mismatches.append(path_id)
            continue

        family=classify_payload(payload)
        family_counts[family]+=1
        if family == 'OTHER':
            continue
        object_name=str(record.get('object_name') or '')
        identifiers=extract_top_level_identifiers(family, object_name, payload)
        entry={
            'family': family,
            'canonical_path': _canonical_path(family, object_name),
            'source_asset': record.get('source_asset'),
            'path_id': path_id,
            'object_name': object_name,
            'payload_size': len(payload),
            'payload_sha256': actual_hash,
            'identifiers': identifiers,
        }
        data_entries.append(entry)
        namespace=NS_BY_FAMILY[family]
        for ident in identifiers:
            ns[namespace].append({'identifier':ident,'canonical_path':entry['canonical_path'],'path_id':path_id})

    namespaces={}
    collisions=[]
    for namespace, items in sorted(ns.items()):
        by_id=defaultdict(list)
        for item in items:
            by_id[item['identifier']].append(item)
        identifiers=[]
        for ident in sorted(by_id, key=lambda s:s.casefold()):
            occurrences=by_id[ident]
            identifiers.append({'identifier':ident,'occurrences':occurrences})
            if len(occurrences)>1:
                collisions.append({'namespace':namespace,'identifier':ident,'occurrences':occurrences})
        namespaces[namespace]={'identifier_count':len(identifiers),'identifiers':identifiers}

    complete = not missing and not mismatches
    return {
        'complete': complete,
        'missing_payload_path_ids': sorted(missing),
        'hash_or_size_mismatch_path_ids': sorted(mismatches),
        'family_counts': {k:family_counts[k] for k in FAMILIES},
        'data_entries': sorted(data_entries,key=lambda e:(e['family'],str(e['canonical_path']).casefold())),
        'collision_index': {
            'namespaces': namespaces,
            'collisions': collisions,
            'total_identifier_count': sum(v['identifier_count'] for v in namespaces.values()),
        },
    }


def analyze_probe_zip(path: Path) -> dict:
    with zipfile.ZipFile(path) as zf:
        bad=zf.testzip()
        if bad:
            raise ValueError(f'corrupt ZIP member: {bad}')
        names=set(zf.namelist())
        for required in ('probe-summary.json','textasset-manifest.json','errors.json'):
            if required not in names:
                raise ValueError(f'missing {required}')
        summary=json.loads(zf.read('probe-summary.json'))
        errors=json.loads(zf.read('errors.json'))
        records=json.loads(zf.read('textasset-manifest.json'))
        if summary.get('game_version') != 'Beta 1.8.42':
            raise ValueError('probe is not Beta 1.8.42')
        if errors:
            raise ValueError(f'probe contains {len(errors)} extraction errors')
        if summary.get('private_export_policy') != 'ALL_TEXTASSETS':
            raise ValueError('probe does not contain full private TextAsset export')
        payloads={}
        for r in records:
            p=r.get('private_path')
            if isinstance(p,str) and p in names:
                payloads[p]=zf.read(p)
        result=analyze_records(records,payloads)
        result['probe_zip_sha256']=hashlib.sha256(path.read_bytes()).hexdigest()
        result['probe_summary']=summary
        return result


def write_sanitized_outputs(result: dict, out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    data_manifest={
        'game_version':'Beta 1.8.42',
        'source_class':'VANILLA',
        'source_role':'EXACT_VANILLA_CORPUS',
        'currency':'EXACT_TARGET',
        'verification':'VANILLA_OBSERVED',
        'resolved': bool(result['complete']),
        'source_probe_zip_sha256':result['probe_zip_sha256'],
        'family_counts':result['family_counts'],
        'entries':result['data_entries'],
        'raw_payloads_committed':False,
    }
    collision={
        'game_version':'Beta 1.8.42',
        'currency':'EXACT_TARGET',
        'complete':bool(result['complete']),
        **result['collision_index'],
    }
    summary={
        'game_version':'Beta 1.8.42',
        'complete':bool(result['complete']),
        'missing_payload_path_ids':result['missing_payload_path_ids'],
        'hash_or_size_mismatch_path_ids':result['hash_or_size_mismatch_path_ids'],
        'family_counts':result['family_counts'],
        'recognized_data_entries':len(result['data_entries']),
        'total_identifier_count':result['collision_index']['total_identifier_count'],
        'collision_count':len(result['collision_index']['collisions']),
        'generation_grade_candidate': bool(result['complete'] and all(result['family_counts'][k] > 0 for k in ('SOFTWARE_TYPE','COMPANY_TYPE','NAME_GENERATOR','PERSONALITIES'))),
        'note':'Hardware Design classification is recorded when serialized Design TextAssets are present; assembly/runtime evidence remains separately scoped.',
    }
    for name,obj in [
        ('resolved-vanilla-data-manifest.json',data_manifest),
        ('identifiers-collision-index.json',collision),
        ('analysis-summary.json',summary),
    ]:
        (out_dir/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')


def create_sanitized_bundle(out_dir: Path, zip_path: Path) -> Path:
    allowed = (
        'resolved-vanilla-data-manifest.json',
        'identifiers-collision-index.json',
        'analysis-summary.json',
    )
    if zip_path.exists():
        zip_path.unlink()
    with zipfile.ZipFile(zip_path, 'w', compression=zipfile.ZIP_DEFLATED) as zf:
        for name in allowed:
            src = out_dir / name
            if not src.is_file():
                raise FileNotFoundError(f'missing sanitized output: {name}')
            zf.write(src, name)
    return zip_path


def main(argv=None)->int:
    ap=argparse.ArgumentParser()
    ap.add_argument('probe_zip', type=Path)
    ap.add_argument('--out-dir', type=Path, default=Path.cwd()/'Beta1842-sanitized-analysis')
    ns=ap.parse_args(argv)
    try:
        result=analyze_probe_zip(ns.probe_zip)
        write_sanitized_outputs(result,ns.out_dir)
        bundle=create_sanitized_bundle(ns.out_dir, ns.out_dir.parent/'Beta1842-sanitized-analysis.zip')
        digest=hashlib.sha256(bundle.read_bytes()).hexdigest()
        (bundle.parent/(bundle.name+'.sha256.txt')).write_text(f'{digest}  {bundle.name}\n', encoding='utf-8')
    except Exception as exc:
        print(f'ANALYSIS_ERROR: {type(exc).__name__}: {exc}')
        return 1
    print(f'ANALYSIS_COMPLETE: {ns.out_dir}')
    print(f'SANITIZED_BUNDLE: {bundle}')
    print(f'SHA256: {digest}')
    return 0

if __name__=='__main__':
    raise SystemExit(main())
