# Tokenizer ABI and Grammar ABI

## Where to start
1. Read the authority ladder and TABI/GABI rules on this page.
2. Implement verifier behavior from the byte-exact acceptance notes in [../README.md](../README.md) history if needed.
3. Cross-check runtime enforcement in [../asx-r/README.md](../asx-r/README.md).

## ASX Tokenizer + Grammar ABI v1.0.0 (FROZEN)

### Authority ladder

1. **asx://canon/json.bytes.v1** decides bytes → hashes.
2. **Tokenizer ABI** decides ids ↔ strings ↔ special tokens.
3. **Grammar ABI** decides parseable surface forms → AST.
4. **Lowering ABI** decides AST → XCFE execution nodes.
5. Proof envelope binds them all.

If any of these mismatch → **reject**, never “best effort”.

## 1) Tokenizer ABI (TABI-1)

### 1.1 Required files (must travel together)

A tokenizer set is valid only if all exist and match hashes:

- `vocab.json` *(token → id, complete map)*
- `id_to_token.json` *(id → token, complete map)*
- `special_tokens.json` *(explicit special definitions)*
- `normalization.json` *(exact normalization rules)*
- `tokenizer.meta.json` *(ABI header + hashes)*

### TABI-1 invariant: Special IDs are immovable

These IDs are **hard-fixed** across all time for this ABI major:

- PAD=0, BOS=1, EOS=2, UNK=3

### 1.3 Token string law

Token strings are **byte-meaningful**. No invisible normalization drift.

Allowed token classes (prefix-coded):

- `⟁GGL:` geometric glyph & operators
- `⟁ARS:` @-grammar surface tokens
- `⟁X:` XJSON control words
- `TXT:` plain text tokens

### 1.4 Normalization ABI (must be deterministic)

`normalization.json` must declare **exact** steps, and runtimes are not allowed to change behavior outside declared normalization rules.

### 1.5 Compatibility rules

- **PATCH**: clarifications/docs/examples only; no token/id changes.
- **MINOR**: append-only token additions within reserved ranges; never renumber.
- **MAJOR**: renumbering, special ID changes, or normalization changes.

## 2) Grammar ABI (GABI-1)

- Surfaces: **ARS.@** and **GGL**.
- Canonical internal forms lower deterministically into XCFE nodes.
- Decimal rule: decimals are **strings** in AST; no float literals in canonical AST.

## 3) ABI handshake and runtime rejection

- Model checkpoints must declare ABI locks for tokenizer + grammar metadata hashes.
- Runtime accepts only when ABI ids and canonical hashes match.
- Mismatch is hard fail (`abi_mismatch.tokenizer`, `abi_mismatch.grammar`, `abi_mismatch.canon`).
