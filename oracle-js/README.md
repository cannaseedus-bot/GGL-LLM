# Oracle JS (JavaScript)

## 1) Folder role
JavaScript implementation of the GGL legality oracle pipeline, mirroring the staged checks used in the Python oracle.

## 2) Current maturity/status
**Executable (library-style)**: core pipeline functions are present and wired for boundary checks, tokenization, parsing, legality, and lowering.

## 3) Key entry points
- `oracle-js/oracle.js`
  - `gglLegalityOracle(text, abi, wantLower=true)` — top-level legality pipeline.
  - `extractGgl(text)` — boundary extraction.
  - `abiHash(tokenizerAbiObj, grammarAbiObj)` — ABI hash helper.
- `oracle-js/tokenize_abi.js`, `oracle-js/ggl_parse.js`, `oracle-js/ggl_legal.js`, `oracle-js/ggl_lower.js`
  - Stage-specific logic for tokenizer validation, parsing, legality, and lowering.
- `oracle-js/canon.js`, `oracle-js/sha.js`
  - Canonicalization and hashing helpers.

## 4) Relationship to other folders
- Designed for parity with `oracle/` (Python reference runtime).
- Useful where JS/Node integration is preferred while preserving the same conceptual oracle stages and error signaling model.

## 5) Minimal usage/dev notes
- Import `gglLegalityOracle` from `oracle-js/oracle.js` in a Node/ESM context.
- Provide ABI objects with `tokenizer` and `grammar` members (matching the Python ABI structure conceptually).
- Expected flow:
  1. Prepare text inside `<GGL>...</GGL>`.
  2. Call `gglLegalityOracle(text, abi, true)`.
  3. Inspect result fields like `ok`, `stage`, `code`, and optional `ast`/`lowered`.
