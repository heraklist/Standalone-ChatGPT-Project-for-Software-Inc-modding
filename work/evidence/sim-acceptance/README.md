# SIM acceptance evidence

This directory stores non-sensitive metadata for live SIM acceptance runs. It is evidence, not a substitute for executing the actual ChatGPT surface.

Do not record PASS unless the named case was actually executed against the named surface with the verified Preview candidate and all required outcomes were directly observed. Do not infer PASS from repository tests, from the written protocol, or from a different surface.

Use `PLATFORM_LIMITATION` only when the tested surface itself demonstrates a blocking platform limitation. Use `NOT_TESTED` when the case was not executed. If a deterministic check cannot run, record the check as `NOT_EXECUTED` and lower the verification ceiling rather than converting the missing check into success.

Evidence records should contain only non-sensitive metadata: date, case ID, surface, candidate version/digest, result, capability observations, required/forbidden outcome summaries, verification ceiling, and concise notes. Do not commit private transcripts, user identifiers, credentials, raw proprietary game data, or user artifacts.

## 2026-09-02 agent checkpoint

The current repository agent can exercise GitHub CI/build verification but has no exposed action for installing/uploading a local custom Skill into separate Plain ChatGPT, ChatGPT Project, or Codex sessions. Accordingly, live A01–A12 results are not synthesized here. They remain `NOT_TESTED` until an actual supported Skills surface is exercised.
