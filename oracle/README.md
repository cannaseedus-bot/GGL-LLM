# Oracle (Python)

## 1) Folder role
Python reference implementation of the GGL legality oracle pipeline: boundary extraction, tokenizer checks, parsing, legality validation, and optional lowering to Scene XJSON.

## 2) Current maturity/status
**Executable (library-style)**: the modules are importable and form a complete end-to-end legality pipeline in Python, intended as the canonical/reference runtime.

## 3) Key entry points
- `oracle/oracle.py`
  - `ggl_legality_oracle(text, abi, want_lower=True)` — top-level legality pipeline.
  - `extract_ggl_payload(text)` — enforces `<GGL>...</GGL>` boundaries.
  - `OracleResult` — structured status payload.
- `oracle/abi.py`
  - `load_abi(tokenizer_path, grammar_path)` — loads ABI JSONs and computes hash.
- `oracle/tokenize_abi.py`, `oracle/ggl_parse.py`, `oracle/ggl_legal.py`, `oracle/ggl_lower.py`
  - Per-stage tokenizer, parse, legality, and lowering behavior.

## 4) Relationship to other folders
- Closest parity target for `oracle-js/` (same staged oracle design implemented in JavaScript).
- Provides Python-side behavior that bridge and verifier tooling (for example in `cline/`) can compare against when validating cross-runtime consistency.

## 5) Minimal usage/dev notes
- Use as a Python package from repo root:
  - `from oracle.abi import load_abi`
  - `from oracle.oracle import ggl_legality_oracle`
- Typical flow:
  1. Load tokenizer+grammar ABI JSON via `load_abi(...)`.
  2. Wrap candidate text in `<GGL>...</GGL>`.
  3. Run `ggl_legality_oracle(...)` and inspect `.ok`, `.stage`, `.code`, and optional `.ast`/`.lowered`.
- No app framework required; this folder is designed as composable modules.
