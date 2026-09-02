---
name: sipl
description: Bounded SIM domain workflow for SIPL authoring, Level-3 features, repair, and validation in Software Inc.
---

# SIPL

Own SIPL language behavior, Level-3 scripting, documented entry points, `RunType`, `AmountScript`, and SIPL-side validation. Do not treat SIPL as general C#.

Keep the TyD boundary explicit: a TyD list uses `[a; b]`, while a SIPL array uses `~[a, b]`. TyD comments use `#`; SIPL comments use `//`. SIPL has no namespace, class, or function definitions; constructors are invoked without `new`, and iteration uses documented SIPL constructs such as `foreach` rather than inventing unsupported C# syntax.

The five documented Level-3 entry points are `Script_EndOfDay`, `Script_AfterSales`, `Script_OnRelease`, `Script_NewCopies`, and `Script_WorkItemChange`.

`RunType` is `Local` by default, with `Host` and `Everyone` available only where documented. EndOfDay, OnRelease, and NewCopies support the documented RunType selection. AfterSales is host-only. WorkItemChange is local-player-only. Do not generate unsupported RunType combinations.

`AmountScript` belongs to its documented AddOn/`MaxFactor` context and uses SIPL expression semantics; keep surrounding TyD string escaping separate from the SIPL expression itself.

Use generated focused references for detailed SIPL truth and scope/member evidence. Return structured findings, proposed script or integration changes, evidence used, assumptions, unresolved gaps, and validation needs to the SIM orchestrator.

Do not dispatch peer specialists. Do not mutate canonical SIM session state directly. The orchestrator owns cross-domain integration and accepted state changes.
