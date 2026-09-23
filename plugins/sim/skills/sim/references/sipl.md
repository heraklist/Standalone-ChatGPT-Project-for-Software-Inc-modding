---
document_id: K05
title: SIPL
knowledge_type: LANGUAGE
canonical_target_version: Beta 1.8.42
last_researched: 2026-09-01
last_runtime_verified: null
aliases: [SIPL, scripts, Level 3, AmountScript]
use_for: [authoring, repair, validation]
do_not_use_for: [inventing undocumented engine surfaces]
source_classes: [OFFICIAL, VANILLA, RUNTIME]
currency_summary: TARGET_BRANCH
known_version_gaps: [Claim-specific reflected members require scope/version evidence]
---

# SIPL

## Language constraints
SIPL is an interpreted reflection-heavy language, not general C#. It has no namespace/class/function definitions. Numeric operations use double semantics. Temporary variables use `var`. No bitwise operations; no compound assignment (`+=`) or increment (`++`); no `new`; no `for`; no multiline comments. `foreach` is supported. Enums are unqualified. Chained comparisons are supported. Single quote characters have no special normal C# string-literal semantics; preserve documented single-quoted AmountScript patterns rather than rewriting them from C# assumptions.

## Arrays and constructors
SIPL arrays use `~[...]`. Constructors are invoked as `Type(...)` without `new`. SIPL comments use `//`; TyD comments use `#`.

## Entry points and scopes
Exactly five documented Level-3 entry points: `Script_EndOfDay` → `ProductScope`; `Script_AfterSales` → `SaleScope`; `Script_OnRelease` → `ProductScope`; `Script_NewCopies` → `CopyScope`; `Script_WorkItemChange` → `DevScope`. The four scope types are ProductScope, SaleScope, CopyScope and DevScope; common scope members include time/company/market/localization helpers. Product local vars use `Product.GetVar(name, default)` / `Product.PutVar(name, value)`.

## RunType
`Local` is default; `Host` and `Everyone` are alternatives. RunType applies to EndOfDay, OnRelease and NewCopies. AfterSales is host-only; WorkItemChange is local-player-only. Do not generate unsupported RunType combinations.

## Built-ins
Math: `Abs`, `Pow`, `Sqrt`, `Log`, `Log10`, `Round`, `Ceil`, `Floor`, `Min`, `Max`, `Sign`, `Sin`, `Cos`, `Lerp`, `Clamp`, `Clamp01`. Enumerable/implicit-`x`: `Any`, `All`, `None`, `ForEach`, `Select`, `SelectMany`, `Count`, `Where`, `First`, `Last`, `FindFirst`, `OrderBy`, `OrderByDescending`, `Distinct`, `Sum`, `Average`, `Min`, `Max`, `Size`, `GetRandomElement`. Other: `String`, `FormatString`, `Debug`, `Random`, `RandomRange`, `RandomInteger`.

## AmountScript
`AmountScript` uses SIPL expression semantics in the documented AddOn feature/`MaxFactor` context. `x` is the factor selected by the player. Validate the surrounding TyD string escaping separately from the SIPL expression.

## Inspection workflow
Use `LIST_SCOPE_MEMBERS X` for documented scope/member inspection and drill down with dot notation. Runtime/member inspection evidence must be version/environment scoped.

## Known gaps / evidence limits
A syntactically plausible reflected member is not accepted unless documented, shipped, assembly-observed, or runtime-proven for the relevant scope.
