# GGL LLM Module (`ggl-llm`)

## Scope
This folder defines the **logical module boundary** for all GGL LLM-related assets in this repository.

The goal is to provide a single navigation entrypoint for contributors while existing implementation files remain in place.

In scope:
- GGL parsing and legality checks (Python and JavaScript implementations)
- Oracle runtime boundary handling for GGL evaluation/execution handoff
- Training and runtime notes that describe behavior and model operation

Out of scope:
- Non-GGL language modules
- Unrelated runtime/tooling assets not mapped in this module

## Status
**Status: active (documentation-first module registration).**

At this stage, files are **not physically relocated**. Instead, this module is established through an explicit manifest so contributors can treat the listed artifacts as one coherent unit.

## Source-of-truth map
Primary source files for this module:

### Parsers / legality
- `oracle/ggl_parse.py`
- `oracle/ggl_legal.py`
- `oracle-js/ggl_parse.js`
- `oracle-js/ggl_legal.js`

### Runtime boundary handling
- `oracle/oracle.py`
- `oracle-js/oracle.js`

### Training / runtime notes
- `docs/GGL-MODEL TRAINING-LOG.md`
- `docs/INFERENCE_SVG.md`

## Module manifest
See [MODULE_MANIFEST.md](./MODULE_MANIFEST.md) for the explicit registered artifact list and ownership intent.
