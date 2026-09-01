# Evidence Update Process

## Principle

Evidence is claim-scoped. Source provenance, version currency, scope, confidence, and verification level are independent dimensions. An official source is not automatically exact-target current; a runtime observation is not automatically a universal parser rule.

## Adding or changing evidence

1. Preserve the source or an allowed reproducible reference to it.
2. Add/update the source record in `17_EVIDENCE_REGISTRY.json`.
3. Identify every affected claim and its owner knowledge document.
4. Classify currency and scope before changing generation rules.
5. Record conflicts as `SOURCE_CONFLICT`, `VERSION_CONFLICT`, `SCOPE_CONFLICT`, or `UNRESOLVED` instead of silently selecting a preferred statement.
6. Update the owner document only to the strength supported by the evidence.
7. Update affected evals and regression tests.
8. Run full CI before release.

## Linked engine APIs

A `LINKED_ENGINE_API` source is delegated authority only for the Software Inc surface that explicitly links/exposes it. Do not generalize a Unity documentation version or API to unrelated Software Inc subsystems.

## Older vanilla corpora

Older vanilla corpora are useful for observed examples, identifiers, and migration research. They do not establish exact-target public loader law. Keep `OLDER_VERSION` currency explicit.

## Exact Beta 1.8.42 capture

Generation-grade status requires the complete capture contract in `work/corpus/beta-1.8.42/capture-manifest.template.json`, including executable and managed assembly identity, Data/Localization/loader-root/collision manifests, current Code persistence/security surface, and Hardware Design observations.

Unknown values remain `UNKNOWN`/null. Never infer a Steam build ID, Unity runtime version, assembly MVID, or hash.

## Archive supersession

`archive/` is immutable historical evidence. When research is wrong or stale:

```text
preserve old artifact
→ add corrected source/evidence
→ mark supersession in source map/registry
→ update production owner document
→ add regression test for the corrected claim
```

Do not rewrite historical files to erase prior mistakes.
