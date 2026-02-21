# Micronaut (SCO/1 object package)

## 1) Folder role
Defines a sealed SCO/1-style "Micronaut" object package: object metadata, semantics declaration, IO/trace artifacts, and orchestrator wiring.

## 2) Current maturity/status
**Partial / spec-heavy package**: object metadata and artifact layout are defined, with placeholder executable semantics (`micronaut.s7`) plus trace/proof and IO files for file-routed orchestration.

## 3) Key entry points
- `micronaut/object.toml`
  - Primary object declaration (`id`, `entry`, `semantics`, IO/trace locations, orchestrator script).
- `micronaut/micronaut.s7`
  - Declared SCO/1 entry object (currently a placeholder scaffold).
- `micronaut/semantics.xjson`
  - Semantic schema/contract reference for the object.
- `micronaut/micronaut.ps1`
  - File-router orchestration script entry.
- Supporting runtime assets:
  - `micronaut/brains/*.json`
  - `micronaut/io/*`
  - `micronaut/trace/*`, `micronaut/proof/*`

## 4) Relationship to other folders
- Complements oracle and bridge work by representing a packaged runtime object with traces/proofs rather than a parser-only library.
- Can serve as an integration target for tooling that consumes object metadata and verifies execution/trace outputs.

## 5) Minimal usage/dev notes
- Start from `object.toml` to understand expected entrypoints and artifact locations.
- Treat `micronaut.s7` as the logical executable entry, but note it is currently placeholder-level.
- Inspect `io/`, `trace/`, and `proof/` to understand expected runtime outputs and audit trail format.
- Use `micronaut.ps1` for orchestrated file-based execution experiments on compatible environments.
