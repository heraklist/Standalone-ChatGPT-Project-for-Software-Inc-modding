# Design Baseline

## Canonical authority

Repository evidence is authoritative over conversation-only assumptions.

Canonical anchors:
- released v0.1.0 foundation: main;
- canonical design: docs/superpowers/specs/2026-08-31-software-inc-mod-studio-design-v1.2.md;
- SIM v0.2 architecture/specification: docs/superpowers/specs/;
- SIM implementation plans: docs/superpowers/plans/;
- current runtime source: production/sim/;
- canonical 18-file knowledge pack: production/knowledge/;
- exact-target evidence: work/corpus/beta-1.8.42/;
- repository gates: schemas/, tools/, tests/, .github/workflows/.

## Architecture

Repository lifecycle:
- archive/: immutable historical evidence;
- work/: active evidence, migration, acceptance, and audit state;
- production/: runtime/upload authority;
- docs/: design, governance, and plans;
- schemas/: machine contracts;
- tools/: deterministic validators/builders;
- tests/: executable regression coverage.

SIM packaging exposes one public production/sim/SKILL.md and package-time internal references. Internal package paths are intentional generated outputs, not missing source files.

## Build surfaces

Legacy canonical generation-grade bundle:
python tools/build_release.py --generation-grade

SIM Preview bundle:
python tools/build_sim_release.py --channel preview

Independent SIM verification:
python tools/verify_sim_release.py dist/sim-0.2.0-preview.zip dist/sim-0.2.0-preview.release-report.json --expected-version 0.2.0-preview
