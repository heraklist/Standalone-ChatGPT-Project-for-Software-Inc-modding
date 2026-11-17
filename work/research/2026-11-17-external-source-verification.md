# External Source Verification — 2026-11-17

Verification of the production knowledge pack against official documentation, patch notes, and
community material. This is a **work/** research artifact, not production authority. Promotions to
production follow `docs/governance/evidence-update-process.md`; unresolved items stay fail-closed.

## Method and source access

Primary sources were triangulated through web search and direct reads of community source code on
GitHub. **Direct fetch of `softwareinc.coredumping.com` and `softwareinc.fandom.com` was blocked by
this session's network policy** (an environment allowlist change was attempted and rejected by the
platform), so wiki content was verified via search extraction rather than full-page capture. GitHub
(`raw.githubusercontent.com`) and `gh` code search were reachable and used as ground truth for the
Code family. Nothing here was promoted from a single unverifiable snippet.

### Sources consulted
- **Official wiki (Coredumping):** Modding, Data_Modding, Code_Modding, SIPL, Material_Modding,
  Furniture_Modding, Hardware_Design, Console, TyD pages (`softwareinc.coredumping.com/wiki`).
- **Official patch notes:** Beta 1.8.34 (PlayerPrefs security fix), itch.io devlogs, tuxdb mirror.
- **Community code (ground truth for Code API):** `software-inc-multiplayer/software-inc-multiplayer`,
  `DenJur/SoftwareIncStartOptions`, `Dykke/modframework`, `Trawis/T5B1`, `hrkrx/SoftwareIncDLLModifications`,
  `AlbinoGeek/Hardware-Mod`.

## Result summary

The knowledge pack is **highly accurate**. Across TyD, SIPL, Data, Code, Furniture, Materials,
Localization, Console, and Hardware Design, independent sources confirmed the documented claims.
**One confirmed error** was found (`OnActive` → `OnActivate`). A small number of claims could not be
independently corroborated and remain documented-only; several evidence-backed coverage gaps are
logged for the upgrade backlog.

### CONFIRMED (official + community agree with the pack)

| Domain | Claim verified |
| --- | --- |
| TyD (`03`) | Simple values / quoted strings / numbers / `null`; lists `[]`, tables `{}`; items split by newline or `;`; `#` comments; `True`/`False` used as record values (`AutoBounds True`, `Skirting False`). |
| SIPL (`05`) | Interpreted, reflection-heavy, "kept simple"; no `+=`/`++`, no class/function defs. **RunType** valid only for `EndOfDay`/`OnRelease`/`NewCopies`; `AfterSales` host-only; `WorkItemChange` local-only — exact match. `CopyScope.Product` dot-notation confirmed via `LIST_SCOPE_MEMBERS`. |
| Data (`04`) | `Mods/<Mod>/SoftwareTypes|CompanyTypes|NameGenerators`, root `Personalities.tyd`; `CompanyTypes/delete.txt`; `Override True` partial + replacing `Features` clears the list. |
| Code (`06`/`07`) | `DLLMods/`; built-in compiler is **C# 3** and **crashes on enums**; Workshop requires game-compiled source; `ModMeta` is an **abstract class** (since Alpha 10.8), overrides `Name`, `Name` identifies save data; override serialization, return `null` = no save; `GiveMeFreedom` for file/network and is a DLL/full-access path (not normal Workshop); **Beta 1.8.34 blocks `UnityEngine.PlayerPrefs`** → migrate to `SaveSetting`/`LoadSetting`; `WindowManager.GenerateUI` from XML with `panel`/`button`/`checkbox`, reloadable live; reference assemblies from `Software Inc_Data/Managed`. |
| Furniture (`08`) | `replacements.tyd` at mod root; `FURNITURE_DEBUG` colors exact (build red↔cyan, nav green↔pink, interaction blue, snap yellow); `EXPORT_FURNITURE_BOUNDS` + `AutoBounds True`. |
| Materials (`09`) | `materials.tyd`; **256×256** PNG; categories `Floor/Interior/Exterior/Roof/Path`; `FloorType` `Wood/Ceramic/Carpet/Concrete`; **3 global atlases**; Extra channels green=smoothness, blue=metallic, alpha=rain/snow. |
| Localization (`10`) | `Localization/<Language>/`; `femalefirstnames.txt`/`malefirstnames.txt`/`lastnames.txt`, most-common-first; TyD records; compare/reload commands; reload doesn't refresh live UI. |
| Console (`12`) | `RELOAD_MOD`/`RECOMPILE_DLL_MOD`/`RELOAD_DLL_MOD`/`UNLOAD_DLL_MOD`/`LIST_SCOPE_MEMBERS` exact; reloads don't update a running game. |
| Hardware (`11`) | Base mesh + Mesh objects + morph targets + attachment points on faces; **2×2×2** cube centered at origin; UV atlas per Mesh; SoftwareType `Design` reference + `Hardware True`. |

### CONFIRMED ERROR → correction applied

- **`06_CODE_MODDING_CORE_AND_DISTRIBUTION.md`: `OnActive` → `OnActivate`.** Real Software Inc mods
  use `public override void OnActivate()` / `OnDeactivate()` (verbatim in `DenJur/SoftwareIncStartOptions`
  and `software-inc-multiplayer`), and the Code Modding wiki/community note the correct method is
  `OnActivate`, not `OnActive`. Fixed in the owner document in this change.

### UNVERIFIED — documented-only, kept as-is (fail-closed, do NOT change without primary source)

- **SIPL exact scope↔entry-point mapping** (`ProductScope`/`SaleScope`/`CopyScope`/`DevScope` per
  entry point). The `CopyScope.Product` example supports the pack's mapping as plausible, but the full
  per-entry-point table was not captured. One search summary suggested a different `OnRelease`/`NewCopies`
  mapping but was not reproducible and is treated as unreliable. Spot-check against the wiki/assembly.
- **Material Extra red = occlusion** — green/blue/alpha confirmed; the red (AO) channel is described on
  the wiki as a darkening/crevice map but was not explicitly confirmed as "red".
- **Furniture `Thumbnail` 128×128** — not confirmed by search (Materials 256×256 was). Not disconfirmed.
- **`RegisterNetworkID` 1–255, `Serialize`/`Deserialize`/`WriteDictionary`, `SWINCTYPE*` symbols** —
  documented on the wiki but not independently corroborated via code search.

### COVERAGE GAPS (evidence-backed; candidates for the upgrade backlog)

- **`meta.tyd`** mod metadata file (name/description/author) for Data mods — not currently documented.
- **Window lifecycle controls** `OnlyHide`, `StartHidden`, `Shown`, `OnClose` for `WindowManager`.
- **Furniture Extra channel scheme differs from Materials** (furniture: red=smoothness, green=emission,
  blue=player-color mapping); plus `IsSnapping`/`SnapsTo` and `Base`-record inheritance of snap points.
- **Material `Skirting` record** (interior walls) and `FloorType` default = `Carpet`.
- **Hardware SoftwareType `Hardware True`** value and `Design` record usage detail.
- **`NameGenerators` `[REPLACE]` caveat** — a single community report says it fails on the hardcoded
  vanilla `Company.txt`; unverified, record as community-reported only.

## Version caveat (validates the fail-closed design)

The newest **public** vanilla data archive is **Beta 1.7.15**, and the wiki pages are version-lagged
(several are 1,000–2,500 days old and were rewritten at Alpha 11). This directly confirms the
repository's core stance: official documentation is not automatically exact-target current, so
Beta 1.8.42 claims genuinely require the direct exact-target evidence gate. The verification **does not**
lift that gate.
