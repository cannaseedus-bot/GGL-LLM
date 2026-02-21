# Micronaut Semantics Profile

## Identity chain

`micronaut = MoE agent = domain experts + tool experts + coding experts + math experts`

Micronaut is modeled as a policy-gated MoE agent container. Semantics, opcodes, crowns, personalities, and policies remain the governing layers.

## Expert classes (normative)

- **Domain expert**: spec laws and runtime constraints.
- **Tool expert**: adapters, IO routes, orchestrator/tool invocation strategy.
- **Coding expert**: implementation planning, refactor strategy, test generation.
- **Math expert**: proofs, scoring, optimization and constraint checks.

## Config extension style

Micronaut supports Gemini-style layered extension profiles using TOML and YAML:

- `extensions/micronaut.moe.toml`
- `extensions/micronaut.moe.yaml`

These extension files describe:

1. expert activation/routing
2. training layers (`adapter`, `lora`, `policy-head`, `routing-head`)
3. brainstorming augmentation controls
4. prompt-management requirements
5. topology schema laws

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
5. No hidden tool invocation outside policy-authorized expert routing.
