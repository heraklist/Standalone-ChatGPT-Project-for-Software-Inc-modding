---
name: compatibility-packaging
description: SIM specialist workflow for Software Inc compatibility, collision/migration decisions, naming strategy, manifests, hashes, and package verification without inventing engine dependency syntax.
---

# Compatibility and Packaging

Own compatibility/packaging analysis and proposed changes. Do not dispatch to peer specialists and do not mutate shared session state directly; return proposed changes to the central SIM orchestrator.

## Decision states

Classify compatibility findings explicitly:

- `SAFE_AUTOFIX`: deterministic low-risk correction supported by canonical evidence.
- `REVIEW_REQUIRED`: semantic or user-intent-sensitive change requiring review.
- `RUNTIME_REQUIRED`: static evidence is insufficient; runtime/native verification is required.
- `UNKNOWN`: evidence does not support a safe conclusion.

Do not silently upgrade `RUNTIME_REQUIRED` or `UNKNOWN` into a compatibility claim.

## Collisions and migration

Check vanilla and installed-mod identifiers when a governed corpus is available. Distinguish accidental collision from documented intentional override/replacement. Prefix/namespacing is a best practice for new identifiers, not engine syntax.

Preserve family-specific mutation semantics during migration. Do not generalize SoftwareType, CompanyType, NameGenerator, Personality, or Materials replacement behavior across domains.

## Dependency and load-order boundary

The canonical evidence set does not establish a documented public mod-level dependency/load-order declaration mechanism. Do not invent engine fields/files such as `Dependencies`, `LoadAfter`, `Priority`, or a dependencies manifest. Studio metadata may record dependencies for QA without pretending it is game syntax.

## Packaging and verification

Use manifests and cryptographic hashes to make generated/repaired package contents inspectable and reproducible where a package schema is actually documented. Verify expected files, identities, collisions, referenced assets, hashes, and distribution profile before delivery.

Editor-native content must remain on its native artifact surface; do not manufacture a generic ZIP/TyD representation for Building or Blueprint content when no public package schema is verified. Unavailable runtime/native checks remain `NOT_EXECUTED`.
