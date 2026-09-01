# Repository Lifecycle

The repository uses four lifecycle roots:

- `archive/` — historical and immutable after import.
- `work/` — mutable research and migration state; never uploaded to the live Project.
- `production/` — approved live and release artifacts only.
- `docs/` — current canonical design, implementation plans, and governance.

Production changes require passing CI. Historical material in `archive/` is not silently rewritten: corrections create a new provenance note or superseding artifact while preserving the original imported evidence.
