# KUHUL Execution Lattice (Micronaut Agent Semantics)

## Scope

This chapter freezes the interpretation of KUHUL as a deterministic execution lattice that extends the core four XCFE phases with time-aware and context-binding phases.

## Core statement

KUHUL is not treated as a general-purpose host language. It is a phase-encoded execution contract where text remains inert unless a legal phase glyph grants authority.

## Canonical phase groups

### Group A — Computation phases

- `⟁Pop⟁`: intent root / acquisition boundary
- `⟁Wo⟁`: transform / materialization request
- `⟁Sek⟁`: effect dispatch (the only host-mutating phase)
- `⟁Ch'en⟁`: commit / finalize / proof boundary

### Group B — Existence-over-time phases

- `⟁Yax⟁`: binding / contextual anchor (no mutation)
- `⟁K'ayab'⟁`: hot cycle (fast loop)
- `⟁Kumk'u⟁`: deep cycle (slow loop)
- `⟁Xul⟁`: yield / suspend / scheduler handoff

## Micronaut agent equivalence

For Micronaut object execution, the following equivalence is normative for the semantic adapter layer:

- micronaut = agent
- semantics = opcode legality and phase authority
- crowns = privileged policy envelopes bound to the active phase
- personalities = selected behavior profiles constrained by policy
- policies = deterministic guards over allowed opcodes, state transitions, and effect scopes

## Opcode + policy lattice

Each executable opcode MUST declare:

1. owning phase (`Pop|Wo|Sek|Ch'en|Yax|K'ayab'|Kumk'u|Xul`)
2. legality constraints
3. required policy crown
4. trace emission shape

Execution is valid only if opcode legality and policy crown constraints both pass.

## Kuhul grams (binary language substrate)

Micronaut agent implementations MAY consume symbolic grams represented as base64 payloads that decode to deterministic binary n-gram/k-gram streams.

- input representation: base64 text envelope
- decoded representation: binary grams (n-grams and k-grams)
- semantic role: pattern substrate for policy/personality selection and bounded phase dispatch

The decoded gram stream MUST be traceable and hash-bindable in the same run record as phase/opcode transitions.

## Minimal runtime adapter contract

A compliant adapter exposes:

- `init(config) -> handle`
- `execute(kpi_or_program) -> result + trace`
- `kill(handle) -> boolean`

Where `execute` MUST emit enough structured trace to replay phase transitions, opcode calls, policy decisions, and gram decoding checkpoints.


## Micronaut MoE specialization law

Micronaut deployments MAY express a policy-gated MoE layer where expert classes are explicit and deterministic:

- domain experts
- tool experts
- coding experts
- math experts

MoE selection MUST remain bounded by phase + policy legality and MUST emit trace checkpoints for expert routing decisions.

Gemini-style TOML/YAML extension profiles are allowed as configuration carriers, but they do not override KUHUL phase authority or topology schema laws.
