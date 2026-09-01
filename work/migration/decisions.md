# Migration Decisions

The migration is claim-level and evidence-scoped. Historical source bytes are preserved under `archive/`; production knowledge is rewritten from approved claims rather than copied wholesale.

## Dispositions

- `KEEP` — technically correct and structurally suitable.
- `REWRITE` — useful facts but old structure, evidence language, or unsafe wording.
- `MERGE` — content absorbed into a new canonical owner document.
- `DROP` — incorrect, invented, or ModForge-only.
- `ARCHIVE_ONLY` — historical/research value, not production retrieval.
- `SUPERSEDED` — replaced by stronger or newer evidence.

## Mandatory legacy-falsehood scan

The migration must detect and prevent reintroduction of:

- Greek-semicolon parser law;
- lowercase-only TyD boolean parser law;
- universal TyD field-order law;
- ModForge support-matrix authority over the standalone ChatGPT Project;
- invented `Data/Features.tyd`-style layouts;
- invented Building/Blueprint filesystem paths;
- `~[...]` presented as TyD rather than SIPL.
