# GGL Documentation

## Where to start
1. Read §39 and §40 below for the normative definition.
2. Review model-facing notes in [../GGL-MODEL TRAINING-LOG.md](../GGL-MODEL%20TRAINING-LOG.md).
3. For runtime authority boundaries, cross-check [../asx-r/README.md](../asx-r/README.md).

## 39. GGL — Geometric Glyph Language (Structural Geometry IR)

- Canonical symbolic language for expressing geometric structure, transforms, and composition.
- GGL is a **structural intermediate representation**, not a runtime.
- GGL lowers deterministically into:
  - ASX Geometry
  - K’UHUL-A AST
  - SVG / projection surfaces (via Projection Law)
- GGL has **no execution authority**.
- GGL is eligible ASX material **only when**:
  - It conforms to the registered GGL schema
  - It lowers deterministically into ASX-R-legal AST
  - It maps into SCXQ2 lanes when geometry exists (G2L-1 applies)

## 40. GGL Tokenization Layer (Normative)

- Defines the **canonical token vocabulary** for GGL, KUHUL blocks, and associated IRs.
- Tokenization is a **compression and alignment layer**, not a semantic layer.
- Tokenization **does not add meaning** and **cannot alter legality**.
- All tokenization artifacts MUST be:
  - Deterministic
  - Replayable
  - Hashable
  - Schema-bound

### 40.1 Token Categories (Normative)

The tokenizer vocabulary is partitioned into **explicit classes**:

- Structural tokens (`{ } [ ] ( ) : , = |`)
- GGL primitive glyphs (◯ □ △ ─ • ⬡ ∿ ⌒)
- GGL operator glyphs (∪ ∩ ∖ ⊕ ⊗ ⟿ →)
- GGL transform identifiers (rotate, scale, translate, etc.)
- Quantized numeric bins (e.g., `N_000 … N_255`)
- KUHUL phase glyphs (`⟁Pop⟁`, `⟁Wo⟁`, `⟁Sek⟁`, `⟁Ch'en⟁`, `⟁Yax⟁`, `⟁K'ayab'⟁`, `⟁Kumk'u⟁`, `⟁Xul⟁`)
- KUHUL block identifiers (labels only; non-executable)
- DOMAIN_ENGINE tokens
- Format boundary markers (`<FMT:GGL>`, `<FMT:SVG>`, `<FMT:LOTTIE>`, etc.)
- Intent tags for preference learning (`<INTENT:RENDER>`, `<INTENT:ANIMATE>`, etc.)

> Rule: Tokenization MUST preserve glyph atomicity. Splitting registered glyphs is illegal.
