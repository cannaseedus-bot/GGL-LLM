# ASX Specification

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

### 9. ASX Geometry
- Structural geometry layer defining spaces (2D/3D), shapes, and coordinate semantics.
- Purpose: verifiable, compressible spatial state; not rendering.

### 10. ASX Metrics
- Metric structure layer defining distance/angle/geodesic meaning and metric spaces/tensors.
- Enforces legality constraints on spatial relationships; not imperative math loops.

### 11. MFA-1 — Metric-aware Fold Assertions
- Metric constraints as verifier-grade assertions (e.g., `distance(p,q) < 10`).
- Failing assertions propose illegal state; bound to proof roots and replay.

### 12. G2L-1 — Geometry → SCXQ2 Lane Mapping
- Deterministic mapping from geometry/types to SCXQ2 lanes with stable-name hashing.
- Enforces canonical ordering; mandatory when geometry exists.

### 13. SCXQ2
- Execution/compression algebra with DICT/FIELD/ LANE/EDGE core layout and batch framing.
- Meaning representation requiring decompression to yield identical semantics.

### 14. CC-v1 (Compression Calculus v1)
- Formal math spec behind compression semantics; SCXQ2 is its instantiation.
- Defines operators and laws for meaning-preserving compression transformations.

### 15. Proof System
- Hash-based proof material binding structure to legality for replay verification.
- Proof failure equals execution failure; scope limited to structural semantics.

### 16. Conformance Suite
- Test vector and verifier contract set for ASX-R.
- Defines compliant runtime accept/reject behavior, including phase rules, AST legality, SCXQ2 decoding, proof checks, KQL normalization, metric assertions.

### 17. ASX-R/REF (Reference Interpreter Profile)
- Non-code profile defining strictest baseline behavior.
- Guarantees portability: passing REF implies passing elsewhere; defines canonical ordering, rejection rules, minimal supported blocks, verifier obligations.

### 18. KQL (K’UHUL Query Language)
- Only legal query language in ASX family, representing queries as data/AST.
- Deterministic lowering of dialects with canonical parameter order; no executable strings.

### 19. IDB-API + KQL v1
- Authoritative persistence interface for ASX runtimes using deterministic commits and replay-verifiable history.
- KQL-only access with SCXQ2 at rest; forbids raw SQL, side-channel writes, implicit indexes.

### 20. MX2DB / Local DB Plane
- Database substrate storing ASX structures (event logs, folds, proofs, lanes, dictionaries, conformance artifacts).
- Storage holds canonical forms without introducing semantics.

### 21. ASX RAM
- Volatile tick-scoped state plane for execution phases.
- Disposable between ticks yet provable/replayable from event/proof log.

### 22. Runtime Folds
- Structural execution substrate comprising named folds (compute, geometry, query, proof, etc.).
- Folds declare structure and constraints; execution is phase-governed and auditable.

### 23. K’UHUL π
- Math/physics script layer within the kernel ecosystem providing deterministic math primitives.
- Must lower to AST and remain deterministic; does not override ASX-R legality.

### 24. Projection Law (CSS/DOM/UI)
- UI projection rule: rendering reflects deterministic runtime state without defining semantics.
- CSS/DOM act as projection surfaces only.

### 25. K’UHUL Kernel Layer (Implementation Substrate)
- Practical execution engine (e.g., `sw.khl`) executing legal structures.
- Replaceable implementation; deviation indicates non-compliance.

### 26. Tape System (Packaging)
- Canonical packaging of runnable fold bundles (“tapes”) for deterministic distribution.
- Tapes are content and cannot change language semantics.

### 27. Shards / Multi-Hive Architecture
- Partitioning of folds/responsibilities into isolated domains (prime, scxq2, math_pi, training, etc.).
- Supports scalability and separation without altering legality; boundaries affect deployment only.

### 28. Mesh / Network Layer
- Transport and coordination layer for moving ASX structures while preserving proofs and canonical forms.
- Network transports content without injecting semantics.

### 29. MeshChain
- Contract/ledger domain expressed as ASX structures for deterministic contract execution and replayable ledger state.
- Uses XJSON + KQL + proofs; contracts are data with verifiable execution.

### 30. Liquidaty
- Solidity-style DSL compiling into ASX contract blocks.
- Human-friendly authoring; compiled XJSON `@asx_contract` blocks define execution under mesh governance.

### 31. SecuroLink
- Zero-trust capability-link identity/auth layer issuing scoped capability keys and domain-bound tokens.
- Auth gates access without defining runtime meaning.

### 32. Verification / Native Verify Flux
- Phase+barrier proof system auditing key transitions (e.g., rotation proofs, replay proofs).
- Enforces structural, deterministic, hash-bound proofs with non-reentrancy and monotonic rules.

### 33. AGL (Atomic Glyph Language)
- Governed glyph lifecycle, registry, and grammar for atomic glyphs.
- Ensures deterministic lowering and safety via registry invariants.

### 34. ASM (Atomic Symbolic Markup)
- Attribute-based symbolic DOM semantics (⚛️ and ⟁) with deterministic binding.
- Embeds semantic structure in valid HTML as projection/structure descriptor without execution authority.

### 35. ATOMIC.CSS / ATOMIC.XJSON
- Visual control surface and machine-readable visual schema.
- CSS variables/classes project runtime state; they do not define semantics.

### 36. ASXR (Runtime Bundle / Browser VM Edition)
- Deployable runtime bundle executing tapes/blocks in browser environments (service worker, DOM bridges).
- Implementation must obey ASX-R.

### 37. Trinity Runtime (CPU/GPU/TPU)
- Multi-runtime orchestration for routing workloads across shards while preserving required determinism.
- Performance layer without semantic alteration.

Understood. Below is a **clean, normative update to the ASX Specification** that **integrates the tokenizer / GGL / KUHUL vocabulary work** without breaking any existing law, authority, or frozen artifacts.

I am **not rewriting** the spec — I am **extending it correctly**.

Everything below is written to be **append-only**, **non-contradictory**, and **lockable**.

---

# 🔒 ASX Specification — Normative Update

## Appendix A (Extension) — Tokenization, GGL, and Execution Vocabulary

> **Status:** Normative
> **Scope:** ASX Family (all layers)
> **Authority:** ASX-R (unchanged)

---

## 39. GGL — Geometric Glyph Language (Structural Geometry IR)

* Canonical symbolic language for expressing geometric structure, transforms, and composition.
* GGL is a **structural intermediate representation**, not a runtime.
* GGL lowers deterministically into:

  * ASX Geometry
  * K’UHUL-A AST
  * SVG / projection surfaces (via Projection Law)
* GGL has **no execution authority**.
* GGL is eligible ASX material **only when**:

  * It conforms to the registered GGL schema
  * It lowers deterministically into ASX-R-legal AST
  * It maps into SCXQ2 lanes when geometry exists (G2L-1 applies)

---

## 40. GGL Tokenization Layer (Normative)

* Defines the **canonical token vocabulary** for GGL, KUHUL blocks, and associated IRs.
* Tokenization is a **compression and alignment layer**, not a semantic layer.
* Tokenization **does not add meaning** and **cannot alter legality**.
* All tokenization artifacts MUST be:

  * Deterministic
  * Replayable
  * Hashable
  * Schema-bound

### 40.1 Token Categories (Normative)

The tokenizer vocabulary is partitioned into **explicit classes**:

* Structural tokens (`{ } [ ] ( ) : , = |`)
* GGL primitive glyphs (◯ □ △ ─ • ⬡ ∿ ⌒)
* GGL operator glyphs (∪ ∩ ∖ ⊕ ⊗ ⟿ →)
* GGL transform identifiers (rotate, scale, translate, etc.)
* Quantized numeric bins (e.g., `N_000 … N_255`)
* KUHUL phase glyphs (`⟁Pop⟁`, `⟁Wo⟁`, `⟁Sek⟁`, `⟁Ch'en⟁`, `⟁Yax⟁`, `⟁K'ayab'⟁`, `⟁Kumk'u⟁`, `⟁Xul⟁`)
* KUHUL block identifiers (labels only; non-executable)
* DOMAIN_ENGINE tokens (see §41)
* Format boundary markers (`<FMT:GGL>`, `<FMT:SVG>`, `<FMT:LOTTIE>`, etc.)
* Intent tags for preference learning (`<INTENT:RENDER>`, `<INTENT:ANIMATE>`, etc.)

> **Rule:**
> Tokenization MUST preserve glyph atomicity.
> Splitting registered glyphs is illegal.

---

## 41. DOMAIN_ENGINE_INDEX (Frozen)

* Canonical index of **semantic domains** within ASX.
* Domain engines define **meaning categories**, not execution.

### 41.1 Frozen Domain Engines

The following engines are **normatively frozen**:

* `ENG_PI` — Math / signal / inference evaluation
* `ENG_COMPRESSION` — CC-v1 / SCXQ2 semantics
* `ENG_PHYSICS` — Conceptual motion and constraint semantics
* `ENG_GEOMETRY` — Topology, shape, spatial relations
* `ENG_SYMBOL` — Glyphs, symbols, textual entities
* `ENG_TEMPORAL` — Existence over time (`⟁Yax⟁`, `⟁K'ayab'⟁`, `⟁Kumk'u⟁`, `⟁Xul⟁`)
* `ENG_PERCEPTION` — Projection / *as-what* layer (UI, SVG, DOM, 3D)

### 41.2 Domain Engine Law

* Domain engines:

  * Define interpretation domains
  * Do **not** execute
  * Do **not** alter control flow
* Execution remains governed exclusively by:

  * ASX-R
  * XCFE
  * K’UHUL-A

---

## 42. safe.ggltensors (Canonical Token & Weight Container)

* `safe.ggltensors` is a **proof-carrying binary container** for:

  * Token embeddings
  * LoRA deltas
  * Geometry / Fourier embeddings
  * Domain-aligned feature banks
* `safe.ggltensors`:

  * Forbids arbitrary code
  * Forbids pickle-style deserialization
  * Requires schema-declared tensor layouts
  * Requires global and per-tensor hashes

### 42.1 Binding Rules

A `safe.ggltensors` artifact is valid ASX material **only if**:

* It declares:

  * Tokenizer hash
  * Token vocabulary version
  * DOMAIN_ENGINE_INDEX version
* Its tokenizer hash matches the runtime tokenizer
* Its tensors do not introduce new semantics
* Its contents lower to ASX-R-legal structures when used

---

## 43. Tokenization vs Authority (Explicit Clarification)

* Tokenizers:

  * Encode structure
  * Reduce entropy
  * Stabilize learning
* Tokenizers **never define semantics**.
* Authority hierarchy remains unchanged:

```
ASX-R
 ├─ XCFE
 ├─ K’UHUL-A
 ├─ SCXQ2 / CC-v1
 └─ Proof System
```

Tokenization sits **below meaning** and **above compression**.

---

## 44. RLHF / Training Compatibility (Normative)

* Structured symbolic corpora (GGL, SVG text, Lottie JSON, KUHUL blocks) are **first-class RLHF substrates**.
* Reward functions MAY include:

  * Schema validity
  * Deterministic lowering success
  * Geometry similarity
  * Projection equivalence
* Vision encoders are **optional consumers**, not authorities.
* Projection artifacts (PNG, frames) are **compiled views**, not canonical truth.

---

## 45. Non-Goals (Explicit)

The ASX family **does not**:

* Treat tokenization as semantics
* Allow models to emit executable KUHUL runtime code
* Allow projection layers to define meaning
* Permit training artifacts to bypass ASX-R legality

---

### 38. ASX “Everything Gets Compressed” Law
- Family-wide rule requiring all semantic artifacts to have SCXQ2 form.
- If content cannot lower into canonical SCXQ2 structure, it is invalid ASX family material.
