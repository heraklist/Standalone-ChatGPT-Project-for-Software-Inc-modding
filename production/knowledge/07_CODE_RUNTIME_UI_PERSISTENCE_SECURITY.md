---
document_id: K07
title: Code Runtime, UI, Persistence and Security
knowledge_type: FAMILY
canonical_target_version: Beta 1.8.42
last_researched: 2026-09-01
last_runtime_verified: null
aliases: [Code runtime, UI, persistence, networking]
use_for: [authoring, repair, validation]
do_not_use_for: [inventing undocumented engine surfaces]
source_classes: [OFFICIAL, VANILLA, RUNTIME]
currency_summary: TARGET_BRANCH_WITH_EXACT_TARGET_GATE
known_version_gaps: [Exact target assemblies pending]
---

# Code Runtime, UI, Persistence and Security

## Persistence and security
For target **Beta 1.8.34 or later**, any generated Code use of `UnityEngine.PlayerPrefs` is a static blocker: official patch notes state such mods no longer load. Use documented `ModBehaviour.SaveSetting` / `LoadSetting` (and related setting APIs) for global mod settings, or `Serialize` / `Deserialize` plus `WriteDictionary` for per-save state. Do not substitute generic Unity persistence APIs.

## Events and lifecycle
Documented event surfaces include `GameSettings.IsDoneLoadingGame`, `GameSettings.GameReady`, `GameSettings.OnQuit`, `MarketSimulation` product/company/tech/framework events, and `TimeOfDay.OnHourPassed`, `OnDayPassed`, `OnMonthPassed`. Some documentation is historically version-labelled; exact-target assembly/runtime evidence controls claims beyond the documented scope. Subscribe and unsubscribe symmetrically to avoid leaked handlers across activation cycles.

## Asset loading
`ParentMod` exposes documented helpers including `LoadTexture`, `LoadXMLFile`, `LoadFullXMLFile`, `LoadTydFile`, `LoadAudio`, `LoadGLTF`, and `LoadOBJ`. Paths are relative to the installed mod location; every referenced asset is part of package completeness.

## Networking
Register multiplayer message IDs with `ParentMod.RegisterNetworkID(id)` in the documented `1–255` range. IDs are tied to the active mod lifecycle. If the host has not enabled Code mods, Code mods are deactivated; do not promise a client-only Code networking path.

## Software Inc UI surfaces
Software Inc documents both programmatic `WindowManager` UI and `WindowManager.GenerateUI` using HTML/XML-like markup. The documented object-tag surface includes `empty`, `panel`, `button`, `label`, `list`, `input`, `checkbox`, `progressbar`, `slider`, `combo`, `scrollbar`, `scrollview`, `window`, `image`, and `rawimage`. Attributes/tags are case-sensitive where documented; preserve exact casing, element IDs, anchors/position/size values, and callback bindings.

Layout tags include `horizontallayout`, `verticallayout`, `gridlayout`, `contentfitter`, and `layoutelement`. Their linked Unity documentation is `LINKED_ENGINE_API`: it is authoritative only for the explicitly delegated layout surface, not proof that every Unity 2018.2 API is available or that the game's global Unity runtime version is 2018.2. `HorizontalLayoutGroup` arranges children horizontally; `VerticalLayoutGroup` vertically; `GridLayoutGroup` uses uniform group-controlled cells; `ContentSizeFitter` sizes a `RectTransform` from minimum/preferred content; `LayoutElement` supplies/overrides min/preferred/flexible layout values.

Studio QA recommendations for UI include dynamic add/remove, localization expansion, resize/aspect-ratio behavior, scroll overflow, reopen/activate/deactivate, callback cleanup and layout reflow. These are QA recommendations, not parser laws.

## Full access
`GiveMeFreedom` materially changes the security/distribution model. Treat it as local DLL/full-access architecture and surface the user-impact/security consequences.

## Known gaps / evidence limits
Linked Unity docs do not replace exact-target assembly evidence for Software Inc-specific APIs.
