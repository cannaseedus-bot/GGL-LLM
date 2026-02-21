# GGL-LLM Docs

This folder contains the GGL-LLM model-facing documentation that was previously mixed into top-level `docs/` spec files.

## Contents

- `INFERENCE_SVG.md` — Safe.GGLTensor inference mouth and SVG/GGL projection contract notes.
- `GGL-MODEL-TRAINING-LOG.md` — historical training/debug/evaluation log for early GGL model runs.

## Why this folder exists

GGL-LLM documentation has a different lifecycle than frozen core specs: it includes training observations, model ABI pitfalls, and operational notes. Keeping it here avoids clutter in language/runtime spec docs.
