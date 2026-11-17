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

## Primary-source addendum (official wiki + patch notes, provided directly)

Primary-source copies of the official `Modding` wiki page (revision 1374, last edited 6 Apr 2026)
and the Coredumping site's news/patch-note stream were obtained directly, confirming earlier
search-based findings and adding version-scoped evidence:

- **`meta.tyd` CONFIRMED (coverage gap closed).** The Modding page documents an optional root
  `meta.tyd` overriding a mod's `Name`/`Description`/`Author`; otherwise the folder name is the mod
  name. In-game auto-creation is noted as "not implemented yet as of Alpha 11.4.7". Added to `04`.
- **Loader roots CONFIRMED verbatim.** `Mods` (software types + personalities), `Furniture`,
  `Materials` (room/path/roof textures), `DLLMods` (C#/dll), `Localization` (translations) — exactly
  as the pack documents. Furniture may be added with `.obj` 3D object files.
- **Localization CONFIRMED verbatim.** `femalefirstnames.txt`/`malefirstnames.txt`/`lastnames.txt`,
  newline-separated, ordered by commonness; `COMPARE_LOCALIZATION`, `CONVERT_LOCALIZATION_TYD`
  (XML→TyD), `RELOAD_LOCALIZATION` (does not refresh live UI).
- **NEW entry point `Script_OnUpdate` → `FUTURE_DEV`.** The "Final Overhaul update" (2026-10-04)
  lists "Added Script_OnUpdate to level 3 feature modding." This update is **after** Beta 1.8.42
  (patch notes dated 2026-08-20) and **explicitly breaks save compatibility** (overhaul testing
  branch). It is therefore NOT part of the canonical Beta 1.8.42 five-entry-point surface; recorded
  as a forthcoming `FUTURE_DEV` addition in `05` known gaps. This is a textbook case for the version
  firewall: a real, official change that must not be back-applied to the target.
- **Beta 1.8.42 CONFIRMED as a real version** (official patch notes, 2026-08-20), validating the
  canonical target identity.
- **Overhaul-branch modding changes (FUTURE_DEV, not for 1.8.42):** furniture must be explicitly
  marked as ceiling fixtures for modding (instead of relying on building boundary); software box art
  becomes customizable/moddable (overrides floppy/CD illustration); room material window respects
  interior/exterior toggles; xml files whitelisted for code mods; code-mod error handling stabilized.
- **Version-labeling note.** The game is Early Access and the dev uses both "Beta 1.8.x" (patch notes)
  and internal "Alpha 11.x" (wiki) labels in the same period; treat version strings carefully when
  classifying currency.

These primary sources do not alter the exact-target gate, which still requires the direct Beta 1.8.42
environment/assembly evidence the capture manifest defines.

## Full-page primary-source verification (Code, Material, Data, TyD, Furniture, Hardware)

Complete official wiki pages were obtained and read. The knowledge pack matches them, in most
cases verbatim. Page revisions/dates: Code Modding (rev 1375, 14 Apr 2026), Material Modding
(rev 939, 12 Mar 2023), Data Modding (rev 956, 30 Oct 2023), TyD (rev 548, 3 Feb 2020),
Furniture Modding (rev 1246, 29 Aug 2025), Hardware Design (rev 898, 8 Mar 2022).

### Previously-unverified items, now CONFIRMED verbatim

- **SIPL scope ↔ entry-point mapping** (the main open item): the Data Modding table lists exactly
  `Script_EndOfDay→ProductScope`, `Script_AfterSales→SaleScope`, `Script_OnRelease→ProductScope`,
  `Script_NewCopies→CopyScope`, `Script_WorkItemChange→DevScope` — an exact match to `05`. The
  earlier search summary that suggested a different mapping was wrong. RunType rules, scope members,
  and `Product.GetVar/PutVar` also match verbatim.
- **Material Extra channel = red occlusion**: "red channel controls occlusion… green controls
  smoothness/specularity… blue controls metallic… alpha controls snow and rain" — exact match to `09`.
  Plus `(4096²)/(256²)=256` materials, 3 atlases, single draw call, up to 8 presets, `Skirting`,
  `FloorType` (Carpet default) — all confirmed.
- **Code `SWINCTYPE`/`SWINCTYPEMAJOR`/`SWINCTYPEMAJOR_MINOR`** (`SWINCBETA`/`SWINCRELEASE`,
  `SWINCBETA1`, `SWINCBETA1_7`/`SWINCBETA1_8`): confirmed verbatim.
- **Code `RegisterNetworkID` "between 1-255"**, auto de-registered on deactivation, host-must-enable:
  confirmed verbatim.
- **Code persistence**: `SaveSetting`/`LoadSetting` (+`TryLoadSetting`/`DeleteSetting`), and per-save
  `Serialize`/`Deserialize` over `WriteDictionary` with `[System.NonSerialized]`/empty-constructor
  rules: confirmed verbatim.
- **Code `WindowManager.GenerateUI` tag set** (`empty,panel,button,label,list,input,checkbox,
  progressbar,slider,combo,scrollbar,scrollview,window,image,rawimage` + layout tags): exact match
  to `07`, including case-sensitivity and the Unity 2018.2 layout links.
- **`ParentMod` loaders** (`LoadTexture/LoadXMLFile/LoadFullXMLFile/LoadTydFile/LoadAudio/LoadGLTF/
  LoadOBJ`): exact match to `07`.
- **Furniture `Thumbnail` 128×128** and **`Height2` max 2** (−0.1/−0.05 for carpets): confirmed
  verbatim, closing the last furniture gap. `FURNITURE_DEBUG` colours, `replacements.tyd`,
  TransformParent ordering, snap/interaction point names: all match `08`.
- **Hardware Design 2×2×2** cube at origin, base mesh + morph targets + attachment points on faces,
  sub-atlas UV textures: exact match to `11`.
- **TyD**: Tynan Sylvester's language; Software Inc uses a fork of the C# implementation
  (`khornel/TyDSharp`, upstream `TynanSylvester/TyD`); `#` comments, `[a; b]` lists, `{}` tables,
  `null`, quoted strings with `\"`; XML→TyD migration: exact match to `03`.

### Correction refined

The earlier `OnActive → OnActivate` note is kept but made precise: the Code Modding wiki **prose
literally says `OnActive`**, so the pack's original text faithfully quoted the wiki. Shipped mods
compile `OnActivate` (symmetric with `OnDeactivate`), which is the real `Assembly-CSharp` method;
`06` now records this as a `SOURCE_CONFLICT` resolved in favour of `OnActivate`.

### Additional primary-source-confirmed coverage (candidates for governed additions)

- **Furniture Extra/`ExtraMap` channels differ from room Materials**: furniture uses R=smoothness,
  G=emission, B=player-colour-mapping (room Materials use R=occlusion/G=smoothness/B=metallic).
- **Window lifecycle controls** `OnlyHide`/`StartHidden`/`Shown`/`OnClose`.
- **Console**: `GENERATE_LOCALIZATION`, `EXPORT_FURNITURE_POINTS`, `FURNITURE_THUMBNAIL`,
  `UNLOCK_FURNITURE`, `INSTA_DEVELOP_DESIGN`, `SHOW_INSPECTOR`, `SHOW_ICONS`, `EXECUTE`.
- **Add-on built-ins** `LocalizePlural('Employee', x)` and `Switch(x, clampBool, localizeBool, …)`.
- **Material `Skirting`** record and **`FloorType` default = Carpet**; **component Thumbnail 128×128**.
- **Vanilla data archive list** ends at **Beta 1.7.15** (official), directly confirming the pack's
  `OLDER_VANILLA_CORPUS` basis and the need for the exact-target gate.

### Overall verdict

Across every family, the knowledge pack is confirmed accurate against the current official wiki.
One real error was found and corrected (`OnActivate`), one documented gap closed (`meta.tyd`), and
one post-target change scoped as `FUTURE_DEV` (`Script_OnUpdate`). No claim required weakening; the
exact-target Beta 1.8.42 gate remains necessary and unchanged, since the public wiki is explicitly
version-lagged and the newest public vanilla data is Beta 1.7.15.
