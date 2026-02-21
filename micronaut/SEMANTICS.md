# Micronaut Semantics Profile

## Identity chain

`micronaut = agent = semantics = opcodes = crowns = personalities = policies`

Micronaut acts as an agent container whose behavior is defined by explicit semantics and constrained by policy crowns.

## Execution model

- Phases provide authority boundaries.
- Opcodes are phase-owned operations.
- Crowns are policy envelopes that authorize opcode classes.
- Personalities are deterministic parameterizations selected within policy limits.

## Binary gram substrate

Micronaut supports base64-encoded symbolic payloads that decode into binary n-gram and k-gram structures (KUHUL grams).

- Base64 is transport only.
- Binary grams are the execution substrate consumed by semantic/policy modules.
- Decode + consume steps are trace-emitted for reproducibility.

## Safety requirements

1. No opcode dispatch without a legal phase anchor.
2. No crown escalation outside declared policy transitions.
3. No personality switch without trace entry and deterministic reason code.
4. All gram decodes must be hash-verifiable in trace artifacts.
