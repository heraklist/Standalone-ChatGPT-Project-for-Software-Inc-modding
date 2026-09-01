from __future__ import annotations
import json, sys
from pathlib import Path
try:
    import jsonschema
except ImportError:
    jsonschema = None

REQUIRED = {"id","title","category","severity","prompt","required_assertions","forbidden_assertions","pass_rule"}
SEVERITIES={"P0","P1","P2","P3"}

def validate_file(path: Path) -> list[str]:
    errors=[]
    try: data=json.loads(path.read_text(encoding='utf-8'))
    except Exception as e: return [f'{path}: invalid JSON: {e}']
    if not isinstance(data,list): return [f'{path}: root must be array']
    ids=[]
    for i,item in enumerate(data):
        if not isinstance(item,dict): errors.append(f'{path}[{i}]: record must be object'); continue
        missing=REQUIRED-set(item)
        if missing: errors.append(f'{path}[{i}]: missing {sorted(missing)}')
        if item.get('severity') not in SEVERITIES: errors.append(f'{path}[{i}]: invalid severity')
        for key in ('required_assertions','forbidden_assertions'):
            if not isinstance(item.get(key),list) or not item.get(key): errors.append(f'{path}[{i}]: {key} must be non-empty array')
        ids.append(item.get('id'))
    if len(ids)!=len(set(ids)): errors.append(f'{path}: duplicate ids')
    return errors

def validate_dir(root: Path) -> list[str]:
    errors=[]
    for p in sorted(root.glob('*.json')): errors.extend(validate_file(p))
    core=root/'core.json'
    if core.exists():
        ids=[x['id'] for x in json.loads(core.read_text(encoding='utf-8'))]
        expected=[f'E{i:02d}' for i in range(1,75)]
        if ids!=expected: errors.append('core.json: IDs must be exactly ordered E01-E74')
    return errors

def main(argv=None):
    args=argv or sys.argv[1:]
    root=Path(args[0]) if args else Path('production/evals')
    errors=validate_dir(root)
    for e in errors: print(e)
    return 1 if errors else 0
if __name__=='__main__': raise SystemExit(main())
