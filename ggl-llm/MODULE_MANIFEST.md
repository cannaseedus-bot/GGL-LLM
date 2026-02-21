# GGL LLM Module Manifest

This document registers existing repository artifacts into a single logical GGL LLM module without relocating files.

## Registered artifacts

| Area | Artifact | Role |
|---|---|---|
| Parser / legality | `oracle/ggl_parse.py` | Python parser implementation for GGL |
| Parser / legality | `oracle/ggl_legal.py` | Python legality checks for GGL |
| Parser / legality | `oracle-js/ggl_parse.js` | JavaScript parser implementation for GGL |
| Parser / legality | `oracle-js/ggl_legal.js` | JavaScript legality checks for GGL |
| Runtime boundary | `oracle/oracle.py` | Python oracle runtime boundary and orchestration path |
| Runtime boundary | `oracle-js/oracle.js` | JavaScript oracle runtime boundary and orchestration path |
| Training/runtime notes | `docs/GGL-MODEL TRAINING-LOG.md` | Model-training chronology and observations |
| Training/runtime notes | `docs/INFERENCE_SVG.md` | Runtime/inference notes and SVG-related behavior |

## Integration model
- **Current model:** documentation-first module registration
- **Physical file locations:** unchanged
- **Contributor rule:** treat this manifest and `ggl-llm/README.md` as the discovery entrypoint for all GGL LLM work

## Future migration option
If we later relocate source files into `ggl-llm/`, maintain compatibility import/require shims in original paths to avoid breaking external references.
