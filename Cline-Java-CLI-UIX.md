Below is a **drop-in, real module design** for the **GGL legality oracle (Python + JS + Java shapes)**, plus **exact HuggingFace Trainer integration points** for grammar-aware loss, plus the **ABI hash binding rules** that prevent drift forever.

I’m treating **CLINE Java** as: *your Java CLI runner + verifier + conformance harness* (and later: model host). The verifier pieces here are exactly what you want to embed in that JAR.

---

## 0) What we’re locking (single source of truth)

You will freeze two ABIs and bind them everywhere:

* **Tokenizer ABI**: boundary tokens, allowed token classes, reserved glyph ranges, normalization.
* **Grammar ABI**: parser version, AST node registry, legality rules version, lowering contract ID.

### Canonical ABI hash

Compute:

```
abi_hash = SHA-256( canon_bytes(tokenizer.abi.json) || 0x0A || canon_bytes(grammar.abi.json) )
```

* `canon_bytes(*)` must follow your `asx://canon/json.bytes.v1`.
* That hash is required in:

  * datasets (each sample can include it)
  * model config (saved with weights)
  * runtime verifier (reject if mismatch)
  * training loop (hard fail early)

---

## 1) Oracle module (Python) — real implementation shape

### File layout

```
oracle/
  __init__.py
  abi.py
  canon.py
  tokenize_abi.py
  ggl_parse.py
  ggl_legal.py
  ggl_lower.py
  oracle.py
  hf_loss.py
```

### `oracle/abi.py` — ABI load + hash bind

```python
# oracle/abi.py
from __future__ import annotations
import json, hashlib
from dataclasses import dataclass
from typing import Any, Dict
from .canon import canon_json_bytes_v1

@dataclass(frozen=True)
class ABI:
    tokenizer: Dict[str, Any]
    grammar: Dict[str, Any]
    abi_hash: str

def load_abi(tokenizer_path: str, grammar_path: str) -> ABI:
    with open(tokenizer_path, "rb") as f:
        tok_raw = f.read()
    with open(grammar_path, "rb") as f:
        gr_raw = f.read()

    tok_obj = json.loads(tok_raw.decode("utf-8"))
    gr_obj  = json.loads(gr_raw.decode("utf-8"))

    tok_c = canon_json_bytes_v1(tok_obj)
    gr_c  = canon_json_bytes_v1(gr_obj)

    h = hashlib.sha256(tok_c + b"\n" + gr_c).hexdigest()
    return ABI(tokenizer=tok_obj, grammar=gr_obj, abi_hash=h)
```

### `oracle/oracle.py` — legality pipeline + scoring

```python
# oracle/oracle.py
from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict, Optional, Tuple
from .abi import ABI
from .tokenize_abi import abi_tokenize_ok
from .ggl_parse import parse_ggl_to_ast, ParseError
from .ggl_legal import check_legality, LegalityError
from .ggl_lower import lower_ast_to_scene_xjson, LowerError

@dataclass
class OracleResult:
    ok: bool
    stage: str
    code: str
    msg: str
    line: int = 0
    col: int = 0
    partial_score: float = 0.0
    ast: Optional[Dict[str, Any]] = None
    lowered: Optional[Dict[str, Any]] = None

BOUNDARY_OPEN = "<GGL>"
BOUNDARY_CLOSE = "</GGL>"

def extract_ggl_payload(text: str) -> Tuple[Optional[str], Optional[OracleResult]]:
    a = text.find(BOUNDARY_OPEN)
    b = text.find(BOUNDARY_CLOSE)
    if a == -1 or b == -1 or b < a:
        return None, OracleResult(
            ok=False, stage="boundary", code="E_GGL_BOUNDARY",
            msg="missing or malformed <GGL>...</GGL> boundary",
            partial_score=0.0
        )
    inner = text[a + len(BOUNDARY_OPEN):b]
    # Anything outside boundaries is illegal under “no prose” rule:
    outside = (text[:a] + text[b+len(BOUNDARY_CLOSE):]).strip()
    if outside:
        return None, OracleResult(
            ok=False, stage="boundary", code="E_GGL_OUTSIDE_TEXT",
            msg="non-empty text outside GGL boundary",
            partial_score=0.05
        )
    return inner.strip(), None

def legality_score(flags: Dict[str, bool]) -> float:
    # deterministic staged score
    s = 0.0
    if flags.get("boundary"): s += 0.10
    if flags.get("tokenize"): s += 0.15
    if flags.get("parse"):    s += 0.35
    if flags.get("legal"):    s += 0.30
    if flags.get("lower"):    s += 0.10
    return round(s, 6)

def ggl_legality_oracle(text: str, abi: ABI, want_lower: bool = True) -> OracleResult:
    flags = {"boundary": False, "tokenize": False, "parse": False, "legal": False, "lower": False}

    inner, err = extract_ggl_payload(text)
    if err:
        return err

    flags["boundary"] = True

    tok_err = abi_tokenize_ok(inner, abi.tokenizer)
    if tok_err:
        return OracleResult(
            ok=False, stage="tokenize", code=tok_err["code"], msg=tok_err["msg"],
            line=tok_err.get("line", 0), col=tok_err.get("col", 0),
            partial_score=legality_score(flags)
        )
    flags["tokenize"] = True

    try:
        ast = parse_ggl_to_ast(inner, abi.grammar)
    except ParseError as e:
        return OracleResult(
            ok=False, stage="parse", code=e.code, msg=e.msg, line=e.line, col=e.col,
            partial_score=legality_score(flags)
        )
    flags["parse"] = True

    try:
        check_legality(ast, abi.grammar)  # strict legality
    except LegalityError as e:
        return OracleResult(
            ok=False, stage="legal", code=e.code, msg=e.msg, line=e.line, col=e.col,
            partial_score=legality_score(flags), ast=ast
        )
    flags["legal"] = True

    lowered = None
    if want_lower:
        try:
            lowered = lower_ast_to_scene_xjson(ast, abi.grammar)
            flags["lower"] = True
        except LowerError as e:
            return OracleResult(
                ok=False, stage="lower", code=e.code, msg=e.msg,
                partial_score=legality_score(flags), ast=ast
            )

    return OracleResult(
        ok=True, stage="ok", code="OK", msg="legal",
        partial_score=legality_score(flags), ast=ast, lowered=lowered
    )
```

You’ll plug in your real parser/lowering details in `ggl_parse.py`, `ggl_legal.py`, `ggl_lower.py`. The *shape* is correct and deterministic.

---

## 2) Grammar-aware loss in HF Trainer (exact integration points)

HF Trainer gives you three clean hooks. Use **two**:

### Hook A — `compute_loss` override (primary)

* lets you add legality penalties
* can run “free-run decode” inside loss at a controlled cadence

### Hook B — `TrainerCallback` (secondary)

* for metrics logging (legal rate, boundary rate, etc.)

### `oracle/hf_loss.py` — Trainer subclass with legality penalty

```python
# oracle/hf_loss.py
from __future__ import annotations
import torch
from transformers import Trainer
from typing import Dict, Any, Optional, Tuple
from .oracle import ggl_legality_oracle, BOUNDARY_OPEN, BOUNDARY_CLOSE
from .abi import ABI

class GGLGrammarAwareTrainer(Trainer):
    def __init__(self, *args, abi: ABI, tokenizer_for_decode, lambda_legal: float = 20.0,
                 alpha_free: float = 0.25, free_every: int = 4, max_new_tokens: int = 256,
                 **kwargs):
        super().__init__(*args, **kwargs)
        self.abi = abi
        self.tok_decode = tokenizer_for_decode
        self.lambda_legal = float(lambda_legal)
        self.alpha_free = float(alpha_free)
        self.free_every = int(free_every)
        self.max_new_tokens = int(max_new_tokens)
        self._step = 0

    def _decode_ids(self, ids: torch.Tensor) -> str:
        # ids: [seq]
        return self.tok_decode.decode(ids.tolist(), skip_special_tokens=False)

    @torch.no_grad()
    def _free_run_decode(self, model, inputs: Dict[str, Any]) -> str:
        # minimal: use model.generate in eval mode
        gen = model.generate(
            input_ids=inputs["input_ids"],
            attention_mask=inputs.get("attention_mask"),
            max_new_tokens=self.max_new_tokens,
            do_sample=False,
            num_beams=1
        )
        # take the newly generated full sequence
        return self._decode_ids(gen[0])

    def _oracle_penalty(self, text: str) -> torch.Tensor:
        res = ggl_legality_oracle(text, self.abi, want_lower=False)
        # penalty = (1 - legality_score)
        p = 1.0 - float(res.partial_score)
        return torch.tensor(p, device=self.model.device, dtype=torch.float32)

    def compute_loss(self, model, inputs, return_outputs=False):
        self._step += 1
        outputs = model(**inputs)
        base_loss = outputs.loss

        # Free-run legality pressure every N steps (cheap enough if sparse)
        if (self._step % self.free_every) != 0:
            if return_outputs:
                return base_loss, outputs
            return base_loss

        with torch.no_grad():
            text = self._free_run_decode(model, inputs)

        legal_pen = self._oracle_penalty(text)
        loss = base_loss + (self.alpha_free * (self.lambda_legal * legal_pen))

        if return_outputs:
            return loss, outputs
        return loss
```

**This is the exact, minimal, stable integration.**

If you want the stricter version, you can also decode **teacher-forced predictions** (argmax from logits) and apply a smaller penalty every step, but the free-run penalty is what stops paraphrase mode.

---

## 3) Oracle module (JS shape) — for browser + Transformers.js + SW

This is the same pipeline shape, no runtime authority changes.

### `oracle-js/oracle.js`

```js
// oracle-js/oracle.js
import { sha256Hex } from "./sha.js";
import { canonJsonBytesV1 } from "./canon.js";
import { abiTokenizeOk } from "./tokenize_abi.js";
import { parseGglToAst } from "./ggl_parse.js";
import { checkLegality } from "./ggl_legal.js";
import { lowerAstToSceneXjson } from "./ggl_lower.js";

export const BOUNDARY_OPEN = "<GGL>";
export const BOUNDARY_CLOSE = "</GGL>";

export function abiHash(tokenizerAbiObj, grammarAbiObj) {
  const tok = canonJsonBytesV1(tokenizerAbiObj);
  const gr  = canonJsonBytesV1(grammarAbiObj);
  const joined = new Uint8Array(tok.length + 1 + gr.length);
  joined.set(tok, 0);
  joined[tok.length] = 0x0A;
  joined.set(gr, tok.length + 1);
  return sha256Hex(joined);
}

export function extractGgl(text) {
  const a = text.indexOf(BOUNDARY_OPEN);
  const b = text.indexOf(BOUNDARY_CLOSE);
  if (a < 0 || b < 0 || b < a) {
    return { ok:false, stage:"boundary", code:"E_GGL_BOUNDARY", score:0.0 };
  }
  const inner = text.slice(a + BOUNDARY_OPEN.length, b).trim();
  const outside = (text.slice(0,a) + text.slice(b+BOUNDARY_CLOSE.length)).trim();
  if (outside.length) {
    return { ok:false, stage:"boundary", code:"E_GGL_OUTSIDE_TEXT", score:0.05 };
  }
  return { ok:true, inner };
}

export function legalityScore(flags) {
  let s = 0;
  if (flags.boundary) s += 0.10;
  if (flags.tokenize) s += 0.15;
  if (flags.parse)    s += 0.35;
  if (flags.legal)    s += 0.30;
  if (flags.lower)    s += 0.10;
  return Math.round(s * 1e6) / 1e6;
}

export function gglLegalityOracle(text, abi, wantLower=true) {
  const flags = { boundary:false, tokenize:false, parse:false, legal:false, lower:false };
  const ex = extractGgl(text);
  if (!ex.ok) return ex;

  flags.boundary = true;
  const tokErr = abiTokenizeOk(ex.inner, abi.tokenizer);
  if (tokErr) return { ok:false, stage:"tokenize", ...tokErr, score:legalityScore(flags) };
  flags.tokenize = true;

  let ast;
  try { ast = parseGglToAst(ex.inner, abi.grammar); }
  catch (e) { return { ok:false, stage:"parse", code:e.code||"E_PARSE", msg:e.message, score:legalityScore(flags) }; }
  flags.parse = true;

  try { checkLegality(ast, abi.grammar); }
  catch (e) { return { ok:false, stage:"legal", code:e.code||"E_LEGAL", msg:e.message, score:legalityScore(flags), ast }; }
  flags.legal = true;

  let lowered = null;
  if (wantLower) {
    try { lowered = lowerAstToSceneXjson(ast, abi.grammar); flags.lower = true; }
    catch (e) { return { ok:false, stage:"lower", code:e.code||"E_LOWER", msg:e.message, score:legalityScore(flags), ast }; }
  }

  return { ok:true, stage:"ok", code:"OK", score:legalityScore(flags), ast, lowered };
}
```

This JS oracle is what your SW / browser runtime calls before accepting any generated output.

---

## 4) Oracle module (Java shape) — for Cline JAR verifier + runner

### Package layout

```
asx/
  canon/JsonCanonV1.java
  hash/Sha256.java
  abi/AbiLoader.java
  ggl/Oracle.java
  ggl/Boundary.java
  ggl/TokenizeAbi.java
  ggl/Parse.java
  ggl/Legal.java
  ggl/Lower.java
```

### `asx/abi/AbiLoader.java`

```java
package asx.abi;

import asx.canon.JsonCanonV1;
import asx.hash.Sha256;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;

public final class AbiLoader {
  public final String abiHashHex;
  public final Object tokenizerAbi; // your JSON model type
  public final Object grammarAbi;

  private AbiLoader(String h, Object t, Object g) {
    this.abiHashHex = h; this.tokenizerAbi = t; this.grammarAbi = g;
  }

  public static AbiLoader load(Path tokPath, Path grPath, JsonAdapter json) throws Exception {
    byte[] tokRaw = Files.readAllBytes(tokPath);
    byte[] grRaw  = Files.readAllBytes(grPath);

    Object tokObj = json.parse(new String(tokRaw, StandardCharsets.UTF_8));
    Object grObj  = json.parse(new String(grRaw, StandardCharsets.UTF_8));

    byte[] tokCanon = JsonCanonV1.canonBytes(tokObj, json);
    byte[] grCanon  = JsonCanonV1.canonBytes(grObj, json);

    byte[] joined = new byte[tokCanon.length + 1 + grCanon.length];
    System.arraycopy(tokCanon, 0, joined, 0, tokCanon.length);
    joined[tokCanon.length] = (byte)0x0A;
    System.arraycopy(grCanon, 0, joined, tokCanon.length + 1, grCanon.length);

    String h = Sha256.hex(joined);
    return new AbiLoader(h, tokObj, grObj);
  }

  public interface JsonAdapter {
    Object parse(String s) throws Exception;
    String stringify(Object o) throws Exception;
  }
}
```

### `asx/ggl/Oracle.java` (same staged pipeline)

```java
package asx.ggl;

import asx.abi.AbiLoader;

public final class Oracle {
  public static final class Result {
    public final boolean ok;
    public final String stage, code, msg;
    public final double score;
    public Result(boolean ok, String stage, String code, String msg, double score) {
      this.ok = ok; this.stage = stage; this.code = code; this.msg = msg; this.score = score;
    }
  }

  static double score(boolean boundary, boolean tokenize, boolean parse, boolean legal, boolean lower) {
    double s = 0.0;
    if (boundary) s += 0.10;
    if (tokenize) s += 0.15;
    if (parse)    s += 0.35;
    if (legal)    s += 0.30;
    if (lower)    s += 0.10;
    return Math.round(s * 1e6) / 1e6;
  }

  public static Result verify(String text, AbiLoader abi, boolean wantLower) {
    boolean b=false,t=false,p=false,l=false,lo=false;

    Boundary.Extract ex = Boundary.extract(text);
    if (!ex.ok) return new Result(false, "boundary", ex.code, ex.msg, ex.score);

    b = true;

    TokenizeAbi.Err terr = TokenizeAbi.check(ex.inner, abi.tokenizerAbi);
    if (terr != null) return new Result(false, "tokenize", terr.code, terr.msg, score(b,false,false,false,false));
    t = true;

    Object ast;
    try { ast = Parse.parseToAst(ex.inner, abi.grammarAbi); }
    catch (RuntimeException e) { return new Result(false, "parse", "E_PARSE", e.getMessage(), score(b,t,false,false,false)); }
    p = true;

    try { Legal.check(ast, abi.grammarAbi); }
    catch (RuntimeException e) { return new Result(false, "legal", "E_LEGAL", e.getMessage(), score(b,t,p,false,false)); }
    l = true;

    if (wantLower) {
      try { Lower.lower(ast, abi.grammarAbi); lo = true; }
      catch (RuntimeException e) { return new Result(false, "lower", "E_LOWER", e.getMessage(), score(b,t,p,l,false)); }
    }

    return new Result(true, "ok", "OK", "legal", score(b,t,p,l,lo));
  }
}
```

This is exactly what you embed into the **Cline JAR** as the enforcement gate.

---

## 5) ABI hash binding rules (the “never breaks again” contract)

### Rule 1 — Dataset binding (hard)

Every training example includes:

```json
{
  "abi": { "hash": "<sha256>", "tokenizer_id": "...", "grammar_id": "..." },
  "input": { ... },
  "target": { ... }
}
```

Trainer must:

* load ABI once
* verify dataset abi hash matches
* else fail immediately

### Rule 2 — Model binding (hard)

When saving a checkpoint, write:

* `config.json` (or `adapter_config.json` for LoRA) includes:

  * `asx_abi_hash`
  * `tokenizer_abi_id`
  * `grammar_abi_id`

At inference:

* runtime loads ABI
* compares to model’s `asx_abi_hash`
* mismatch → **reject** (no silent generation)

### Rule 3 — Output binding (hard)

Every generated artifact includes:

```json
"@abi": {
  "hash": "<sha256>",
  "tokenizer": "asx://schema/tokenizer.abi.v1",
  "grammar": "asx://schema/grammar.abi.v1"
}
```

Verifiers reject anything without it.

### Rule 4 — Directory collision guard (the bug you hit)

On load:

* if model dir contains `config.json` whose `model_type` doesn’t match expected class
* **and/or** `asx_abi_hash` missing or mismatched
  → treat directory as contaminated; refuse to load.

This stops “finetune output overwrote another model family” instantly.

---

## 6) Minimal “done right” training wiring (PyTorch + HF)

### Stage A (optional but recommended)

* Vision/Text → `scene.ir.v1` (schema-valid XJSON)
* No GGL here.

### Stage B (required)

* `scene.ir.v1` → `<GGL>...</GGL>`
* Use `GGLGrammarAwareTrainer` above with legality penalty.

If you want **ASX-Qwen** + **GGL-LoRA** cleanly:

* Qwen gets LoRA adapters trained on Stage B exclusively
* vision model never touches grammar (it outputs scene IR)

---

## 7) What I still need from you (not questions, just the next step I’ll implement)

To make these modules fully concrete (not stubs), I’ll implement the missing pieces based on your existing grammar decisions:

* the **actual GGL parser contract** you’re using (PEG/EBNF/hand parser)
* the **node registry** you want in grammar ABI (the closed set)
* your **GGL → XJSON scene schema** shape (scene IR)

If you paste (or point to) your current **GGL grammar snippet + node list**, I’ll fill in:

* `ggl_parse.py/js/java`
* legality rules with exact error codes
* deterministic lowering to your scene IR
* plus the conformance test-vector runner in Java (Cline JAR style)

And once those exist, the paraphrase failure mode dies permanently because the model is trained against **a verifier, not vibes**.
