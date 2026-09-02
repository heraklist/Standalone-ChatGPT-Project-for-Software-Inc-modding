---
document_id: K03
title: TyD Foundations
knowledge_type: LANGUAGE
canonical_target_version: Beta 1.8.42
last_researched: 2026-09-01
last_runtime_verified: null
aliases: [TyD, syntax, parser]
use_for: [authoring, repair, validation]
do_not_use_for: [inventing undocumented engine surfaces]
source_classes: [OFFICIAL, VANILLA, RUNTIME]
currency_summary: TARGET_BRANCH_WITH_EXACT_TARGET_GATE
known_version_gaps: [Beta 1.8.42 exact environment corpus pending]
---

# TyD Foundations

## Software Inc TyD fork
Software Inc documents use of a fork of the C# TyD implementation. The Software Inc fork/runtime surface outranks generic upstream TyD when they differ. Upstream syntax is reference material only when corroborated.

## Values, lists and tables
TyD uses simple values, quoted strings, numbers, `null`, lists `[ ... ]`, and tables `{ ... }`. List/table items may be separated by newlines or semicolons. Canonical generated TyD booleans are `True` and `False`.

## Strings and comments
TyD comments use `#`. Quoted strings use double quotes and escape embedded quotes as `\"`.

## Canonical generation rules
Generate the form demonstrated by Software Inc documentation/vanilla (`True`/`False`). Do not assert that lowercase TyD booleans are universally parser-invalid without fork/runtime evidence. Do not invent a Greek-semicolon parser law or universal field-order law.

## TyD vs SIPL boundary
A TyD list is `[ a; b ]`; SIPL array construction is `~[a, b]`. TyD `#` comments and SIPL `//` comments belong to different parsers. Lowercase `true`/`false` observed inside SIPL script strings do not contradict canonical TyD data booleans.

## Known gaps / evidence limits
Exact Beta 1.8.42 parser behavior beyond documented/shipped patterns remains exact-target evidence work.
