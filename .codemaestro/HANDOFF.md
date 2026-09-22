# Handoff

## Prerequisites

- Python 3.11+
- pip
- packages used by CI: pytest, jsonschema
- no runtime environment variables are currently required for the repository build/verification flow

Recommended clean setup:

python -m venv .venv

Linux/macOS:
source .venv/bin/activate

Windows PowerShell:
.venv\Scripts\Activate.ps1

python -m pip install --upgrade pip pytest jsonschema

## Verify

Run the commands listed in .codemaestro/VERIFICATION.md.

## Build canonical v0.1 project bundle

python tools/build_release.py --generation-grade

Expected output under dist/:
software-inc-mod-studio-project-0.1.0.zip
software-inc-mod-studio-project-0.1.0.release-report.json

## Build current SIM Preview

python tools/build_sim_release.py --channel preview

Expected output:
dist/sim-0.2.0-preview.zip
dist/sim-0.2.0-preview.release-report.json

Verify:
python tools/verify_sim_release.py dist/sim-0.2.0-preview.zip dist/sim-0.2.0-preview.release-report.json --expected-version 0.2.0-preview

## Continuation

Do not merge or publish PR #16 solely because repository CI is green.
Next product gate is a fresh live A06 retest on the supported ChatGPT Skill surface. If it passes, continue A07–A12 and update evidence from observed behavior only.
