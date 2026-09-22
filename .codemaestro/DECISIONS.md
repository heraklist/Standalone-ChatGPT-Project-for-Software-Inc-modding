# Decisions

1. Use repository evidence as source of truth.
2. Package from sim/v0.2.1-remediation@9c8ac46bf7cb821436dd935fda6e7c51a5ca2568.
3. Do not merge PR #16, publish a release, or claim Stable readiness.
4. Preserve A06=FAIL and A07–A12=NOT_TESTED exactly; do not infer acceptance from repository-green CI.
5. Build both the canonical v0.1 generation-grade project bundle and the SIM v0.2 Preview bundle.
6. Run the same repository verification gates used by CI before packaging.
7. Include the entire tracked project source in the delivery, not only the upload/runtime subset.
8. Include CodeMaestro continuity state under .codemaestro/.
9. Include .env.example with no secrets. This repository currently requires no runtime environment variables for its Python build/verification flow.
10. Package from tracked Git content only, excluding .git, caches, virtual environments, untracked local state, and secrets.
11. Treat the generated delivery as a Preview/build handoff artifact, not a release/publication action.
