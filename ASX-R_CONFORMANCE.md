# ASX-R — Conformance Vectors

**Document:** `ASX-R_CONFORMANCE.md`  
**Status:** Normative  
**Authority:** ASX Runtime Language  
**Scope:** Compliance vectors + test requirements  
**Audience:** Implementers, auditors, verifiers  

---

## Purpose

This document defines the **minimum conformance vectors** required for ASX-R implementations. Each vector must be satisfied with **objective, reproducible tests**. Partial compliance is not allowed.

---

## Compliance Vectors (Normative)

### V1 — Explicit State Serialization
**Requirement:** All runtime state must be serializable into ASX JSON with no hidden or ambient data.

**Tests:**
1. Serialize the full runtime state and validate that no interpreter-maintained data exists outside the serialized form.
2. Rehydrate exclusively from ASX JSON and prove byte-identical state equivalence.

---

### V2 — Closed World Enforcement
**Requirement:** Only declared fields and transitions may exist.

**Tests:**
1. Introduce undeclared fields in state input; validation must fail.
2. Introduce undeclared transition type; transition validation must fail.

---

### V3 — Schema Validation as Law
**Requirement:** Any state or transition failing schema validation is illegal.

**Tests:**
1. Provide invalid schema inputs and assert rejection without coercion.
2. Confirm validation occurs before any projection or state selection.

---

### V4 — Mandatory Invariants
**Requirement:** Structural and temporal invariants must be enforced without exception.

**Tests:**
1. Break canonical ordering and ensure rejection.
2. Force epoch regression and ensure rejection.
3. Violate phase legality and ensure rejection.

---

### V5 — Explicit, Monotonic Time
**Requirement:** Time must be represented explicitly and must not regress.

**Tests:**
1. Attempt transitions with decreasing epoch/tick; must reject.
2. Verify phase progression includes explicit time fields.

---

### V6 — Phase Discipline
**Requirement:** Only legal phase transitions may occur.

**Tests:**
1. Attempt to skip a declared phase; must reject.
2. Attempt out-of-phase mutation; must reject.

---

### V7 — Determinism
**Requirement:** Given identical inputs and state, the admissible next state is identical.

**Tests:**
1. Execute identical replay sequences; outputs must be byte-identical.
2. Run multiple interpreters; results must match exactly.

---

### V8 — Replay Sufficiency
**Requirement:** Replay with validation reproduces runtime behavior with no external dependencies.

**Tests:**
1. Replay a recorded state sequence; the admissible states must match.
2. Remove external I/O; ensure behavior is unchanged.

---

### V9 — Interpreter Non-Authority
**Requirement:** Interpreters may select among admissible states but may not invent or mutate.

**Tests:**
1. Attempt interpreter-driven mutation; must be rejected as invalid state.
2. Attempt derived transitions not declared in schema; must fail validation.

---

### V10 — Projection One-Way
**Requirement:** Projections are non-authoritative and cannot alter runtime state.

**Tests:**
1. Inject projection-originated mutation; must be ignored or rejected.
2. Verify that projection observations do not affect admissible states.

---

### V11 — Atomic Blocks Structural Law
**Requirement:** Atomic Blocks define only structure; no behavior.

**Tests:**
1. Confirm Atomic Block declarations do not encode transition logic.
2. Validate structural consistency through schema checks only.

---

### V12 — Atomic CSS as Projection State
**Requirement:** Atomic CSS reflects state but never mutates it.

**Tests:**
1. Modify Atomic CSS and assert no runtime changes occur.
2. Validate that Atomic CSS cannot introduce new state fields.

---

### V13 — Compression as Execution (SCXQ2)
**Requirement:** Compression participates in execution via canonical mappings.

**Tests:**
1. Verify equivalence-class execution yields identical admissible states.
2. Ensure objects are not imperatively traversed or moved.

---

### V14 — No Side Channels
**Requirement:** No external mutable state or interpreter-specific behavior.

**Tests:**
1. Disable external globals; runtime behavior must be unchanged.
2. Attempt timing-based variation; output must remain deterministic.

---

### V15 — No Partial Compliance
**Requirement:** All vectors must pass.

**Tests:**
1. Assert conformance report fails if any vector fails.

---

## Conformance Report Format

A conformance report **MUST** include:

* Implementation identity + version
* Runtime laws version hash
* Schema version hashes
* Test runner identity
* Per-vector pass/fail results with evidence

---

## Reference Artifacts

* `RUNTIME_LAWS.md`
* `ASX-R_STATE_TRANSITION.schema.json`
* `ASX-R_INTERPRETER_CHECKLIST.md`

---

**Compliance is binary.**
