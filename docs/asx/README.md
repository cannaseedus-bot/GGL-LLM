# ASX Family Overview

## Where to start
1. Read the normative glossary below.
2. Continue to the runtime authority docs in [../asx-r/README.md](../asx-r/README.md).
3. For tokenization/grammar ABI constraints, go to [../tokenizer-abi/README.md](../tokenizer-abi/README.md).
4. For geometric language details, go to [../ggl/README.md](../ggl/README.md).

## Appendix A — ASX Family Glossary (Normative)

### 1. ASX
- Language family umbrella defining hierarchy, invariants, and authority model.
- All ASX artifacts reduce to canonical structure with verifiable legality.
- Contains ASX-R, XJSON, XCFE, SCXQ2/CC-v1, K’UHUL layers, query/storage layers, proof layers, conformance.

### 2. ASX-R
- Authoritative runtime language defining legal executions independent of implementation.
- Non-negotiables: determinism, structural legality, replayability, fixed phases, compression semantics.
- Execution phases: `@Pop → @Wo → @Sek → @Collapse` (XCFE-governed).
- Authority source for all other layers.

### 3. XJSON
- Surface serialization and transport form representing ASX structures as JSON envelopes.
- Must lower deterministically into ASX-R-legal AST shapes; not itself the language.

### 4. XCFE
- Control-flow law governing allowed phase ordering, barriers, branch legality, and control vectors.
- Guarantees auditable, proof-bindable branching with no hidden control flow.
- Mandated by ASX-R for anything that runs.

### 5. K’UHUL-A
- AST execution law defining legal execution shapes, node types, child order, and explicitness.
- Requires all content to lower to K’UHUL-A AST with no implicit behavior or hidden mutation.

### 6. K’UHUL-S
- Glyph surface syntax providing compressed/visual surface forms for programs.
- Glyphs have no authority and must deterministically lower to K’UHUL-A AST; ambiguity is illegal.

### 7. ARS
- Structural scripting syntax (human-writable) compiling into XJSON blocks then ASX-R AST.
- Not a JS-like runtime; includes phase, let/const, emit, assert, plan, apply, seal, structural declarations.

### 8. ARS Classes
- Structural types (schemas/templates) defining allowed fields, typing, and defaults.
- Exclude methods, inheritance dispatch, and runtime polymorphism; used for typed state and deterministic validation.
