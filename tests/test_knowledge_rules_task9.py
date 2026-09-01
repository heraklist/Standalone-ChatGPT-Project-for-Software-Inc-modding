from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]/"production/knowledge"
def read(n): return (ROOT/n).read_text(encoding="utf-8")

def test_code_compiler_distribution_and_security_rules():
    code=read("06_CODE_MODDING_CORE_AND_DISTRIBUTION.md"); runtime=read("07_CODE_RUNTIME_UI_PERSISTENCE_SECURITY.md")
    for p in ["C# 3","Workshop Code","async","await","string interpolation","nameof","dynamic","null-conditional","expression-bodied","enum usage","does** support `var`","LINQ","SWINCTYPE","SWINCTYPEMAJOR","SWINCTYPEMAJOR_MINOR","SOURCE_CONFLICT","-DisableModErrors","GiveMeFreedom","Software Inc_Data/Managed"]: assert p in code
    for p in ["Beta 1.8.34","UnityEngine.PlayerPrefs","SaveSetting","LoadSetting","Serialize","Deserialize","WindowManager.GenerateUI","case-sensitive","LINKED_ENGINE_API","horizontallayout","gridlayout","contentfitter","layoutelement"]: assert p in runtime

def test_furniture_material_localization_rules():
    f=read("08_FURNITURE.md"); m=read("09_MATERIALS.md"); l=read("10_LOCALIZATION.md")
    for p in ["128×128","TransformParent","already placed furniture does not update","fresh placement","Furniture/<Pack>/replacements.tyd","interaction points blue","snap points yellow"]: assert p in f
    for p in ["materials.tyd","256×256","material_table_name","three shared global material texture atlases","GPU","red=occlusion","green=smoothness/specularity","blue=metallic","alpha=rain/snow"]: assert p in m
    for p in ["femalefirstnames.txt","malefirstnames.txt","lastnames.txt","do **not** alphabetically sort","RELOAD_LOCALIZATION"]: assert p in l

def test_editor_content_contract():
    e=read("11_EDITOR_CONTENT_HARDWARE_BLUEPRINTS_BUILDINGS.md")
    for p in ["owned by `DATA`","EDITOR_CONTENT","STANDARD","2×2×2","office placement","CANDIDATE_NATIVE_ARTIFACT","FINAL_VERIFIED_NATIVE_ARTIFACT","TOOLING_BLOCKED"]: assert p in e
    for p in ["Never invent `Data/BuildingBlueprint.tyd`","`/Mods/Blueprints/`"]: assert p in e
