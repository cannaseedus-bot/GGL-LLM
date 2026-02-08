# ASX-R — Interpreter Checklist

**Document:** `ASX-R_INTERPRETER_CHECKLIST.md`  
**Status:** Normative  
**Authority:** ASX Runtime Language  
**Scope:** Implementation certification checklist  
**Audience:** Implementers, auditors, verifiers  

---

## Certification Checklist

### A. Runtime Laws
- [ ] Enforces **explicit, serializable state** only.
- [ ] Enforces **closed world** schema boundaries.
- [ ] Rejects any **invalid schema** state or transition.
- [ ] Enforces **mandatory invariants** without exception.
- [ ] Rejects **time regression**.
- [ ] Enforces **phase entry/exit legality**.
- [ ] Guarantees **determinism** across identical inputs.
- [ ] Supports **replay sufficiency** with validation at each step.
- [ ] Maintains **interpreter non-authority**.
- [ ] Enforces **projection one-way flow**.
- [ ] Treats **Atomic Blocks** as structural primitives.
- [ ] Treats **Atomic CSS** as projection-only.
- [ ] Applies **compression as execution** (SCXQ2).
- [ ] Blocks **side channels** and hidden globals.
- [ ] Asserts **binary compliance** (no partial passes).

---

### B. Schema Enforcement
- [ ] Validates against `ASX-R_STATE_TRANSITION.schema.json`.
- [ ] Rejects additional properties not declared by schema.
- [ ] Rejects any transition lacking declared inputs.
- [ ] Verifies `schema_hash` for prior and next states.

---

### C. Time + Phase Discipline
- [ ] `epoch` and `tick` always explicit.
- [ ] Enforces monotonic `epoch` and `tick` progression.
- [ ] Phase transitions match declared entry/exit constraints.
- [ ] No phase skipping.

---

### D. Determinism + Replay
- [ ] Multiple replays produce byte-identical state sequences.
- [ ] Independent interpreters yield identical admissible states.
- [ ] No dependency on external time or environment.

---

### E. Projection Isolation
- [ ] Projection outputs never mutate runtime state.
- [ ] Observations cannot create or modify state.
- [ ] Projection caches are non-authoritative.

---

### F. Evidence Package
- [ ] Conformance report generated per `ASX-R_CONFORMANCE.md`.
- [ ] Hashes for runtime laws and schema included.
- [ ] Test results archived with deterministic replay traces.

---

**Certification requires all checks to pass.**
