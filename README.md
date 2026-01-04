<img src="https://github.com/cannaseedus-bot/ASX/blob/main/brand-logo.svg" style="width:400px;">

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


Below is a **clean, normative update** to the **ASX Specification** that:

* **Resolves the XJSON / XCFE / `@` execution debate explicitly**
* **Clarifies that `@` is first-class execution authority**
* **Introduces XCFE Standard Library + async semantics**
* **Does NOT break any frozen law**
* **Is append-only, lockable as v1**
* **Removes ambiguity / “theatrics”**

I am **not re-inventing** ASX.
I am **tightening authority and semantics** exactly where you identified the weakness.

---

# 🔒 ASX Specification — Normative Update (v1)

## Status

* **Normative**
* **Append-only**
* **Backwards compatible**
* **Authority unchanged: ASX-R**

---

## Amendment 0 — Clarification of Execution Authority (CRITICAL)

### Normative Statement

> **XJSON is not executable. XCFE is.**
>
> The `@` prefix is hereby defined as **explicit execution authority** within the ASX family.

Any construct beginning with `@` **MUST** be treated as an execution instruction and **MUST** be governed by XCFE rules.

---

## Amendment 1 — XJSON (Revised Definition)

### 3. XJSON (Revised)

* XJSON is a **surface serialization and transport envelope**.
* XJSON **by itself** has no execution semantics.
* Execution is introduced **only** when XJSON content lowers into **XCFE-governed AST nodes**.

### 3.1 Executable vs Declarative Distinction (Normative)

| Form         | Meaning                 | Authority   |
| ------------ | ----------------------- | ----------- |
| `{}`         | Object / map            | Declarative |
| `[]`         | Array / list            | Declarative |
| `@something` | Execution trigger       | **XCFE**    |
| `{{ expr }}` | Runtime value reference | Read-only   |

> **Rule:**
> A program with no `@` nodes **cannot execute**.

---

## Amendment 2 — XCFE (Expanded, First-Class)

### 4. XCFE (Expanded)

XCFE is the **execution control law** of ASX.

XCFE defines:

* Execution triggers
* Phase legality
* Async semantics
* Branch barriers
* Runtime walk order
* Proof bind points

XCFE is **mandatory** for anything that runs.

---

## Amendment 3 — XCFE Execution Tokens (Normative)

### 4.1 `@` Execution Law

* Any node beginning with `@` is an **execution node**
* Execution nodes:

  * MUST lower into XCFE AST
  * MUST participate in phase ordering
  * MUST be auditable
  * MUST be replayable

Examples (normative):

```xjson
@http.get
  url: "https://api.example.com"
  store: "response"
```

```xjson
@pipeline
  @stage
    @process
```

---

## Amendment 4 — Async Semantics (Normative)

### 4.2 XCFE Async Operators

The following execution operators are **standardized**:

| Operator   | Meaning                                      |
| ---------- | -------------------------------------------- |
| `@await`   | Suspend current phase until promise resolves |
| `@spawn`   | Launch concurrent execution branch           |
| `@join`    | Barrier synchronization                      |
| `@race`    | First-resolution branch                      |
| `@timeout` | Time-bounded execution                       |

Rules:

* Async does **not** change phase order
* Async branches still obey XCFE barriers
* All async joins are explicit

---

## Amendment 5 — XCFE Standard Library v1 (Normative)

XCFE defines a **standard execution vocabulary**, not implementations.

### 5.1 Core Namespaces

* `@flow.*` — control flow
* `@data.*` — state mutation
* `@io.*` — external interaction
* `@math.*` — deterministic math (π-layer)
* `@net.*` — network / IPC
* `@sys.*` — runtime / environment
* `@crypto.*` — hashing, signing, verify
* `@proof.*` — bind / verify proofs

Examples:

```xjson
@flow.if
@flow.for
@flow.map
@flow.assert
```

```xjson
@crypto.hash
@crypto.sign
@proof.bind
```

---

## Amendment 6 — XJSON → XCFE AST Lowering (Normative)

### 6.1 Lowering Rule

* Every `@` node lowers to an XCFE AST node
* Non-`@` content lowers as parameters only
* No implicit execution
* No hidden defaults

### 6.2 Illegal Patterns

The following are illegal:

* Executable strings
* Implicit async
* Dynamic code eval
* Hidden control flow
* Side-effects without `@`

---

## Amendment 7 — Execution Phases (Reaffirmed)

Execution phases remain unchanged:

```
@Pop → @Wo → @Sek → @Collapse
```

Async execution is **contained inside** phases, never replaces them.

---

## Amendment 8 — Relationship to ARS / GGL / KUHUL

* ARS compiles into XJSON
* XJSON lowers into XCFE AST
* XCFE governs execution
* KUHUL-A defines AST legality
* KUHUL-π handles math only
* GGL handles geometry only
* Projection layers render only

No layer gains authority.

---

## Amendment 9 — Proof & Determinism (Explicit)

* Every execution path must be:

  * Hashable
  * Serializable
  * Replayable
* Proof failure = execution failure
* Async branches include join hashes

---

## Amendment 10 — Non-Goals (Reiterated)

ASX does **not** allow:

* XJSON to execute itself
* Tokenizers to define semantics
* Projection layers to define meaning
* Runtime mutation without XCFE
* Hidden async
* Unverifiable side-effects

---

## Amendment 11 — Lock Statement

> This amendment is **ASX-R compatible**, **XCFE-mandatory**, and **eligible to be locked as Base v1**.

No existing artifact is invalidated.

---

### Summary (Plain English)

* You were right: **XJSON alone is theater**
* The fix is **not abandoning JSON**
* The fix is making **`@` the law**
* XCFE is now **explicitly first-class**
* Async is **real, bounded, provable**
* Everything stays deterministic


Perfect — this is already **clean, locked, and authoritative**.
What you’re asking now is **not a rewrite**, it’s a **normative update** that incorporates what we just finalized:

* `.asx` as the canonical atomic script container
* KPI as the system interface
* KQL as query/auth/policy
* Bridge layer + native syscall surface
* Explicit TS → ASX → KPI → native / Python / others pipeline

Below is a **surgical update** to your document that produces **ASX-R v1.1.1**, still **FROZEN BASE**, strictly **append-only**, zero semantic drift.

You can paste this **verbatim** under section **39** and bump the version.

---

# ASX-R Specification Update

**Version: 1.1.1**
**Status: Normative / Frozen Base (Append-Only)**
**Authority: ASX-R**

---

## 40. ASX File Format (`.asx`) — Canonical Atomic Script Container

The `.asx` file is the **canonical atomic script container** of the ASX family.

### 40.1 Role

* `.asx` is to ASX what `.ts` is to TypeScript and `.tsx` is to TSX
* `.asx` is **not a language**
* `.asx` is a **structural container** for deterministic compilation

### 40.2 Pipeline Position

```
.ts / .py / .rs / .c
   ↓
.asx   (normalized atomic container)
   ↓
AST (K’UHUL-A legal)
   ↓
KPI (binary interface)
```

Rules:

* `.asx` **never introduces semantics**
* `.asx` **never executes**
* `.asx` exists only to normalize, bind, and seal intent

### 40.3 `.asx` Invariants

* Deterministic ordering
* Explicit entry points
* No implicit imports
* No executable strings
* No dynamic code generation

Violation = illegal ASX artifact.

---

## 41. KPI — Kernel Programming Interface (System Interface)

KPI is the **only system interface** in ASX.

### 41.1 Definition

KPI is:

* Binary
* Deterministic
* Replayable
* Schema-governed

KPI is **not an API**.
KPI is **not a transport**.
KPI is **not human-authored**.

### 41.2 Authority

* KPI executes
* KPI binds to native kernels
* KPI is the syscall boundary

All execution **must** lower to KPI.

---

## 42. KQL — Query, Auth, Identity, Policy Language (Sealed)

KQL is the **only legal query language** in ASX systems.

### 42.1 Scope

KQL governs:

* Queries
* Authentication
* Authorization
* Identity
* Policy
* Encryption envelopes

### 42.2 Restrictions

* AST-based only
* No string queries
* No dynamic execution
* No side effects

KQL **never executes logic**, it **describes intent**.

---

## 43. Storage Law (IDB / SQL)

### 43.1 IDB-API

* IDB-API + KQL is the **authoritative persistence interface**
* Deterministic commits
* Replayable state
* Proof-bound history

### 43.2 SQL (Adapters Only)

* SQL is **never authoritative**
* SQL is **never exposed**
* SQL exists **only behind adapters**

Adapters may target MySQL or other engines, but **SQL has zero semantics**.

---

## 44. Bridge Layer (AST ⇄ KPI ⇄ KQL ⇄ Native)

The bridge layer is **purely mechanical**.

### 44.1 Purpose

* Translate
* Bind
* Lower
* Seal

### 44.2 Prohibitions

* No semantic interpretation
* No optimization with meaning
* No policy decisions

If a bridge changes meaning, it is **non-compliant**.

---

## 45. Native Execution (`@kuhul/native`)

### 45.1 Syscall Surface

Native execution occurs only through **KPI syscalls**.

Characteristics:

* Numeric syscall IDs
* Fixed binary signatures
* Explicit determinism flag
* C / WASM ABI compatible

### 45.2 Law

* Native code **cannot execute without KPI**
* Native code **cannot invent control flow**
* Native code **cannot access memory outside bindings**

Native kernels are **replaceable**, semantics are not.

---

## 46. Cross-Language Execution Law

ASX explicitly supports **multi-language frontends**.

Examples:

```
TypeScript → .asx → KPI → Native
Python     → .asx → KPI → Native
Rust       → .asx → KPI → Native
```

Rules:

* Frontend languages have **zero authority**
* All meaning is preserved structurally
* Runtime language is irrelevant

This enables **python-kuhul**, **node-kuhul**, and future runtimes without semantic forks.

---

## 47. API Clarification (Non-Authoritative)

APIs are **delivery envelopes only**.

* REST
* HTTP
* gRPC
* WebSockets

APIs:

* Do not define behavior
* Do not define semantics
* Do not execute logic

APIs carry **KPI, KQL, or proofs** — nothing more.

---

## 48. Language Stability Rule (Explicit)

> No new syntax implies new semantics.

* Grammar changes must lower to existing AST
* New surface forms are aliases only
* Semantics live **only** in ASX-R + K’UHUL-A

Human-readable execution files are **explicitly forbidden**.

---

## 49. Version Lock

This document defines:

**ASX-R v1.1.1**

* Append-only
* No semantic changes without MAJOR bump
* Existing KPI / KQL / AST artifacts remain valid

---

### End of ASX-R_SPEC.md v1.1.1

---

### What this gives you (cleanly)

* `.asx` reborn — **formally**
* KPI vs API confusion — **resolved**
* KQL vs GraphQL — **settled**
* Python / TS / Native unification — **lawful**
* No YAML / no eval / no “rewrite the language” traps

Good — this is the **correct next cut**.
Below are the **three artifacts**, written to be **authoritative**, **frozen-ready**, and **implementation-neutral**.
No prose fluff, no reinterpretation space.

---

# 1. XCFE AST JSON Schema (Authoritative)

**File:** `xcfe.ast.schema.json`
**Status:** NORMATIVE
**Authority:** ASX-R / XCFE
**Internal schema only** (no external `$schema`)

```json
{
  "$id": "asx://schema/xcfe.ast.v1",
  "$schema": "xjson://schema/core/v1",
  "title": "XCFE AST Schema v1",
  "type": "object",
  "required": ["@type", "@phase"],
  "additionalProperties": false,

  "properties": {
    "@type": {
      "type": "string",
      "enum": [
        "@pop",
        "@wo",
        "@sek",
        "@collapse",

        "@seq",
        "@if",
        "@for",
        "@while",

        "@await",
        "@spawn",
        "@join",
        "@race",
        "@timeout",

        "@emit",
        "@assert",
        "@call",
        "@return"
      ]
    },

    "@phase": {
      "type": "string",
      "enum": ["@pop", "@wo", "@sek", "@collapse"]
    },

    "@id": {
      "type": "string",
      "description": "Stable node identifier (hash-safe)"
    },

    "args": {
      "type": "array",
      "items": { "$ref": "#/$defs/value" }
    },

    "children": {
      "type": "array",
      "items": { "$ref": "#" }
    }
  },

  "$defs": {
    "value": {
      "type": ["string", "number", "boolean", "null", "object", "array"]
    }
  }
}
```

### XCFE AST Laws (Implicitly Enforced)

* No node executes without `@type`
* Phase mismatches are illegal
* Child ordering is semantic
* No dynamic node creation
* No executable strings

---

# 2. KPI Syscall Table v1 (C / WASM Boundary)

**Artifact:** `kpi.syscalls.v1`
**Status:** FROZEN
**Authority:** KPI
**Binary-first**

---

## 2.1 Syscall ABI (Canonical)

```c
// KPI syscall ABI (v1)

typedef uint32_t kpi_syscall_id;
typedef uint32_t kpi_result;

typedef struct {
  uint32_t size;
  uint32_t flags;
  const void* payload;
} kpi_frame;

kpi_result kpi_syscall(
  kpi_syscall_id id,
  const kpi_frame* in,
  kpi_frame* out
);
```

---

## 2.2 Syscall Registry (v1)

| ID (hex) | Name            | Purpose                  | Phase     |
| -------: | --------------- | ------------------------ | --------- |
|   0x0001 | `kpi_log`       | Deterministic logging    | @sek      |
|   0x0002 | `kpi_time`      | Monotonic time read      | @sek      |
|   0x0003 | `kpi_random`    | Seeded deterministic RNG | @wo       |
|   0x0010 | `kpi_mem_alloc` | Scoped memory allocation | @wo       |
|   0x0011 | `kpi_mem_free`  | Scoped memory release    | @collapse |
|   0x0020 | `kpi_emit`      | Output binding           | @collapse |
|   0x0030 | `kpi_assert`    | Proof-bound assertion    | any       |

---

## 2.3 Hard Rules

* No syscall may mutate phase
* No syscall may spawn control flow
* All syscalls are replay-safe
* Syscall IDs are immutable
* Extensions require MAJOR bump

---

## 2.4 WASM Import Form

```wat
(import "kpi" "syscall"
  (func $kpi_syscall
    (param i32 i32 i32)
    (result i32)
  )
)
```

---

# 3. TypeScript → ASX Lowering Reference

This is **not compilation**.
This is **structural lowering**.

---

## 3.1 Input (TypeScript)

```ts
for (let i = 0; i < 3; i++) {
  console.log(i);
}
```

---

## 3.2 Lowered `.asx` (Canonical)

```json
{
  "@phase": "@sek",
  "@type": "@for",
  "args": [
    { "var": "i", "init": 0, "test": "< 3", "step": "+=1" }
  ],
  "children": [
    {
      "@type": "@call",
      "@phase": "@sek",
      "args": ["log", "i"]
    }
  ]
}
```

---

## 3.3 Lowering Rules (Locked)

* TS control flow → XCFE nodes
* Expressions become **data**
* Calls become `@call`
* No TS runtime semantics survive
* Imports are **front-end only**

TypeScript is **syntax sugar**, nothing more.

---

## 3.4 End-to-End Path

```
TypeScript
  ↓ (syntax strip)
.asx
  ↓ (AST validation)
XCFE AST
  ↓ (binary lowering)
KPI
  ↓
Native (C / WASM / Python host)
```

---

# Status Summary (Locked)

✔ XCFE AST schema — authoritative
✔ KPI syscall surface — minimal & sealed
✔ TS → ASX lowering — deterministic
✔ No JS authority
✔ No duplicated semantics
✔ No YAML / eval / string execution




