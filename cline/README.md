# Cline Bridge (multi-language verifier assets)

## 1) Folder role
Cross-language ABI and artifact verification assets for bridge/conformance workflows, including Python, JavaScript, and Java verifier implementations plus vectors/results.

## 2) Current maturity/status
**Partial (verification-focused executable tooling)**: verifier logic and conformance vectors are present; snapshot output indicates current verification failures are being tracked.

## 3) Key entry points
- `cline/lib/bridge/abi_verifier.py`
  - Python verifier implementation (canonicalization, hashing, header parsing, verification flow).
- `cline/lib/bridge/abi_verifier.js`
  - JavaScript verifier implementation.
- `cline/lib/bridge/AbiVerifier.java`
  - Java verifier implementation.
- `cline/lib/bridge/conformance_vectors.json`
  - Shared test vectors for cross-runtime consistency checks.
- `cline/lib/bridge/verification.json`
  - Latest verification status snapshot/result payload.

## 4) Relationship to other folders
- Bridges implementations like `oracle/` and `oracle-js/` by enforcing consistent ABI/hash/verifier behavior across languages.
- Serves as conformance infrastructure for multi-runtime parity validation.

## 5) Minimal usage/dev notes
- Treat this folder as verification/conformance infrastructure rather than an end-user app.
- Start from one verifier implementation (`abi_verifier.py`, `.js`, or `.java`) depending on runtime/toolchain.
- Use `conformance_vectors.json` as the common input contract when checking parity.
- Inspect `verification.json` for current known pass/fail state and diagnostics.
