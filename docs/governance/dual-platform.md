# Dual-Platform Packaging

The authored knowledge surface is maintained **once** in `production/` and projected onto
two delivery platforms. There is no second, hand-maintained copy of the knowledge; both
bundles are generated, and the base repository stays clean.

| Platform | Builder | Output (git-ignored `dist/`) | Loading model |
| --- | --- | --- | --- |
| ChatGPT Project | `tools/build_release.py` | `software-inc-mod-studio-project-<version>.zip` | All 18 knowledge files uploaded as resident Project context; `PROJECT_INSTRUCTIONS.md` is the resident instruction. |
| Claude (Skill / Code plugin) | `tools/build_claude_skill.py` | `dist/claude/` (`SKILL.md`, `references/`, `.claude-plugin/plugin.json`) | `SKILL.md` is resident; the 18 knowledge files are `references/` opened on demand (progressive disclosure). |

## Single source of truth

Both builders read the same files:

- `production/project-instructions/PROJECT_INSTRUCTIONS.md` — becomes the ChatGPT resident
  instruction **and** the body of `SKILL.md`.
- `production/knowledge/*` — the exact 18-file canonical pack — becomes the ChatGPT upload set
  **and** the Claude `references/`.

Because ChatGPT loads everything at once while a Claude Skill discloses progressively, the
router document `00_INDEX.md` is the entry point the skill body points at first. The Claude
`SKILL.md` ends with a generated reference index derived from each knowledge file's own
front-matter (`title`, `aliases`) — no content is authored twice and nothing is invented.

## What stays identical across platforms

The evidence firewall, version-awareness, fail-closed retrieval, artifact-surface rules, and
verification doctrine live entirely inside the authored content, so they apply unchanged on
both platforms. Platform-specific wrappers (Project upload manifest vs. `SKILL.md` front-matter
and `plugin.json`) carry **no** engine knowledge.

## Building

```bash
python tools/build_release.py              # ChatGPT structural preview
python tools/build_release.py --generation-grade
python tools/build_claude_skill.py         # Claude Skill + Code plugin wrapper
```

## Invariants (enforced by tests)

- The Claude skill reproduces `PROJECT_INSTRUCTIONS.md` verbatim as its body (no fork).
- `references/` contains exactly the 18 canonical knowledge files.
- `plugin.json` version tracks `knowledge-pack-manifest.json` `pack_version`.
- The build is deterministic (stable file hashes).
