from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]/'production/knowledge'
def read(n): return (ROOT/n).read_text(encoding='utf-8')

def test_tyd_and_sipl_parser_boundaries():
    tyd=read('03_TYD_FOUNDATIONS.md'); sipl=read('05_SIPL.md')
    assert 'TyD list is `[ a; b ]`' in tyd
    assert 'SIPL array construction is `~[a, b]`' in tyd
    assert '`True` and `False`' in tyd
    assert 'SIPL comments use `//`' in sipl and 'TyD comments use `#`' in sipl
    assert 'fork of the C# TyD implementation' in tyd

def test_data_structure_and_override_rules():
    data=read('04_DATA_MODDING.md')
    for phrase in ['SoftwareTypes/','CompanyTypes/','NameGenerators/','Personalities.tyd','`Override True` is a partial','feature list is replaced','`Override Delete`','CompanyTypes/delete.txt','`[REPLACE]`','normally merges','`Replace True`','`AmountScript`','`MaxFactor`']:
        assert phrase in data
    for phrase in ['not canonical `Data/Features.tyd`','`Data/AddOns.tyd`','`Data/Manufacturing.tyd`']:
        assert phrase in data
    assert 'Data/Building.tyd' not in data
    assert 'Data/BuildingBlueprint.tyd' not in data

def test_sipl_entrypoints_runtype_and_constraints():
    sipl=read('05_SIPL.md')
    for ep in ['Script_EndOfDay','Script_AfterSales','Script_OnRelease','Script_NewCopies','Script_WorkItemChange']:
        assert ep in sipl
    for scope in ['ProductScope','SaleScope','CopyScope','DevScope']: assert scope in sipl
    for phrase in ['`Local` is default','AfterSales is host-only','WorkItemChange is local-player-only','no `new`','no `for`','`+=`','`++`','no multiline comments','implicit-`x`']:
        assert phrase.lower() in sipl.lower()
    for builtin in ['Abs','SelectMany','GetRandomElement','RandomInteger','LIST_SCOPE_MEMBERS']:
        assert builtin in sipl
