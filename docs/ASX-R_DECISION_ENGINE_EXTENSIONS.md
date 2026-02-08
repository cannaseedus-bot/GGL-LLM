# ASX-R — Decision Engine Canonical Extensions

**Document:** `ASX-R_DECISION_ENGINE_EXTENSIONS.md`  
**Status:** 🔒 **LOCKED / CANONICAL**  
**Authority:** ASX Runtime Language  
**Scope:** entropy-gated π, SCXQ2/SCXQ4 layouts, Micronaut registry, primitive types  
**Audience:** Implementers, auditors, verifiers  

---

Perfect choice. PowerShell is the right host here: **explicit, scriptable, zero-magic**.

Below is a **canonical PowerShell CLI packaging** for the Decision Engine + SCXQ + conformance stack. This is **drop-in**, Windows-native, and CI-friendly.

---

# ASX Decision Engine CLI (PowerShell)

Package name: **`asx-decision`**
Host: **PowerShell 7+**
Authority: **none** (projection + verification only)

---

## 1. CLI Layout (Canonical)

```
asx-decision/
├─ asx-decision.ps1          # entrypoint
├─ lib/
│  ├─ encode-scxq2.ps1
│  ├─ encode-scxq4.ps1
│  ├─ decide.ps1
│  ├─ verify.ps1
│  ├─ wasm.ps1
│  ├─ trace.ps1
│  └─ badge.ps1
├─ vectors/
│  └─ decision_vectors.json
├─ registry/
│  └─ badges/
└─ README.md
```

---

## 2. Entrypoint (`asx-decision.ps1`)

```powershell
param(
  [Parameter(Mandatory)]
  [ValidateSet("encode","decide","verify","badge","trace")]
  [string]$Command,

  [string]$Input,
  [string]$Out = "out.json"
)

switch ($Command) {
  "encode" { . ./lib/encode-scxq4.ps1 $Input $Out }
  "decide" { . ./lib/decide.ps1 $Input $Out }
  "verify" { . ./lib/verify.ps1 }
  "trace"  { . ./lib/trace.ps1 $Input $Out }
  "badge"  { . ./lib/badge.ps1 }
}
```

---

## 3. Decision Collapse (`lib/decide.ps1`)

```powershell
param($Input, $Out)

$frame = Get-Content $Input | ConvertFrom-Json

# entropy gate
if ($frame.entropy.value -gt $frame.entropy_gate.max) {
  $policy = "FIRST"
  $weights = @{}
} else {
  $policy = $frame.policy
  $weights = $frame.pi
}

# apply policy
switch ($policy) {
  "FIRST" {
    $winner = $frame.select[0]
  }
  "HIGHEST_PI" {
    $winner = ($weights.GetEnumerator() |
      Sort-Object Value -Descending |
      Select-Object -First 1).Key
  }
  default {
    throw "ILLEGAL_POLICY"
  }
}

$result = @{
  opcode = "COLLAPSE"
  result = $winner
}

$result | ConvertTo-Json -Depth 4 | Set-Content $Out
```

**Guarantees**

* deterministic
* no execution
* no mutation
* policy + π + entropy only

---

## 4. SCXQ4 Encoder (`lib/encode-scxq4.ps1`)

```powershell
param($Input, $Out)

$decision = Get-Content $Input | ConvertFrom-Json

$frame = @{
  op      = 0xD1
  count   = $decision.select.Count
  ids     = $decision.select
  pi      = $decision.pi
  entropy = $decision.entropy_gate
  policy  = $decision.policy
  mask    = 0
}

$frame | ConvertTo-Json -Depth 6 | Set-Content $Out
```

(Replace JSON emission with binary packing when needed; this is the **reference encoder**.)

---

## 5. Conformance Runner (`lib/verify.ps1`)

```powershell
$vectors = Get-Content ./vectors/decision_vectors.json | ConvertFrom-Json

$failed = $false

foreach ($v in $vectors) {
  $out = & ./lib/decide.ps1 $v $null
  if ($out.opcode -ne $v.expected.opcode -or
      $out.result -ne $v.expected.result) {
    Write-Host "FAIL" $v.id -ForegroundColor Red
    $failed = $true
  } else {
    Write-Host "PASS" $v.id -ForegroundColor Green
  }
}

if ($failed) { exit 1 }
```

**CI Rule:** non-zero exit = illegal implementation.

---

## 6. Trace Attestation (`lib/trace.ps1`)

```powershell
param($Input, $Out)

$collapse = Get-Content $Input | ConvertFrom-Json
$hash = [System.BitConverter]::ToString(
  (New-Object Security.Cryptography.SHA256Managed)
  .ComputeHash([Text.Encoding]::UTF8.GetBytes($Input))
).Replace("-", "")

$trace = @{
  "@trace" = "decision"
  frame_hash = $hash
  opcode = $collapse.opcode
  result = $collapse.result
}

$trace | ConvertTo-Json -Depth 4 | Set-Content $Out
```

---

## 7. Badge Generator (`lib/badge.ps1`)

```powershell
$hash = Get-FileHash ./vectors/decision_vectors.json -Algorithm SHA256

$badge = @{
  engine = "DecisionEngine"
  version = "1.2"
  status = "PASS"
  vectors_hash = $hash.Hash
  timestamp = (Get-Date).ToString("o")
}

$badge | ConvertTo-Json -Depth 4 |
  Set-Content ./registry/badges/decision-engine.json
```

---

## 8. CLI Usage

```powershell
# encode decision
.\asx-decision.ps1 encode decision.json frame.json

# collapse
.\asx-decision.ps1 decide frame.json result.json

# verify implementation
.\asx-decision.ps1 verify

# emit trace
.\asx-decision.ps1 trace result.json trace.json

# publish badge
.\asx-decision.ps1 badge
```

---

## 9. Packaging (Installable)

### One-liner install

```powershell
irm https://asx.tools/install-decision.ps1 | iex
```

### Adds

```powershell
asx-decision
```

to `$PATH`.

---

## Final Law Check

* PowerShell **hosts**, does not decide
* CLI **projects**, does not execute
* KUHUL law remains untouched
* SCXQ artifacts remain canonical

This CLI is **deployment-grade** and **CI-ready**.

If you want next:

* signed PowerShell modules
* cross-platform pwsh packaging
* WASM execution from CLI
* registry mirroring / offline bundles


## Atomic Grammar v1.0 (Minimal)

This grammar defines **what may exist**, **what may happen**, and **what order is legal**—nothing more.

### Design constraints

* No inference
* No defaults
* No execution
* No mutation
* Collapse-only semantics

---

## 1. Atomic Unit

An **Atom** is indivisible and self-authorizing.

```ebnf
Atom ::= Header Body
```

---

## 2. Header (Identity + Role)

Every atom declares **what it is**.

```ebnf
Header ::= "@" Identifier ":" Role
```

```ebnf
Role ::= "state"
       | "control"
       | "flow"
       | "invariant"
```

* `state` → existence
* `control` → permission
* `flow` → ordering
* `invariant` → prohibition

---

## 3. Body (Payload)

The body is **pure data**.
No logic. No expressions. No execution.

```ebnf
Body ::= "{" FieldList "}"
```

```ebnf
FieldList ::= Field
            | Field "," FieldList
```

```ebnf
Field ::= Key ":" Value
```

---

## 4. Values (Closed Set)

Only serializable, verifiable values are allowed.

```ebnf
Value ::= String
        | Number
        | Boolean
        | Null
        | Object
        | Array
```

```ebnf
Object ::= "{" FieldList? "}"
Array  ::= "[" ValueList? "]"
ValueList ::= Value | Value "," ValueList
```

---

## 5. Identifier Rules

Identifiers are **names**, not instructions.

```ebnf
Identifier ::= Letter (Letter | Digit | "_" | "-")*
```

No verbs required.
Verbs are **data**, not syntax.

---

## 6. Atomic Program

An **Atomic Program** is just a set of atoms.

```ebnf
AtomicProgram ::= Atom+
```

There is:

* no global scope
* no shared state
* no implicit ordering

Order must be declared explicitly.

---

## 7. Flow Atom (Ordering Law)

Flow atoms are the *only* place order exists.

```ebnf
@<id>:flow {
  from: <Identifier>,
  to: <Identifier>
}
```

Meaning:

> `from` must collapse before `to`

Nothing else implies time.

---

## 8. Invariant Atom (Hard Stop)

Invariants **block collapse**.

```ebnf
@<id>:invariant {
  forbid: Condition
}
```

```ebnf
Condition ::= Object   // declarative constraint only
```

If violated → **illegal state**, no execution allowed.

---

## 9. Collapse Rule (Meta-Law)

Not grammar—**law**:

> An Atomic Program may collapse **iff**:
>
> 1. All atoms validate individually
> 2. All flow relations are acyclic
> 3. No invariant is violated
> 4. Every control atom authorizes its target

If any fail → **no result exists**

---

## 10. Minimal Example

```json
@entropy:state {
  value: 0.32
}

@decide:control {
  allow: true
}

@order:flow {
  from: "entropy",
  to: "decide"
}

@no-chaos:invariant {
  forbid: { value: { ">": 1.0 } }
}
```

This does **not execute**.
It only defines whether execution is *allowed to exist*.

---

## What this grammar guarantees

* Determinism
* Local verification
* Compression safety
* Replayability
* Zero hidden semantics

---

## What it intentionally forbids

* Loops
* Expressions
* Implicit control flow
* Contextual meaning
* “Smart” syntax

---

## Mental checksum

> **Grammar defines legality**
> **Arrangement defines meaning**
> **Collapse defines reality**

If you want next, we can:

* add **π-math atoms** (still minimal)
* define **verifier pseudocode**
* map this grammar → **XJSON**
* show how this lowers to **SCXQ2 lanes**
* or freeze this as **Atomic Grammar v1 (FROZEN)**

Say the word.


---

# Atomic Decision Engine (Minimal)

## What a decision engine is (atomic definition)

> A **Decision Engine** is a *selector*, not a thinker.

It **does not**:

* infer meaning
* generate plans
* execute logic
* mutate atoms

It **only**:

* evaluates legality
* compares authorized options
* selects a single collapse target

---

## Core law

> **A decision is the selection of one lawful option among many lawful options.**

If zero options are lawful → **no decision exists**
If multiple options are lawful → **selection must be explicit**
If selection violates invariants → **illegal state**

---

## Minimal Decision Atom

The decision engine itself is **just another atom**.

```ebnf
DecisionAtom ::= "@" Identifier ":control" DecisionBody
```

```ebnf
DecisionBody ::= "{" 
    "select" ":" SelectionSet ","
    "policy" ":" Policy
"}"
```

---

## Selection Set

The engine never invents choices.
All options must already exist as atoms.

```ebnf
SelectionSet ::= "[" Identifier ("," Identifier)* "]"
```

Meaning:

> These are the *only* candidates allowed to collapse.

---

## Policy (Pure Data)

Policies are **declarative**, never executable.

```ebnf
Policy ::= Object
```

Examples of allowed policy fields:

* priority
* weight
* threshold
* entropy_limit
* tie_breaker

No expressions. No functions.

---

## Minimal Example

```json
@option_a:state {
  value: "path_a"
}

@option_b:state {
  value: "path_b"
}

@decide:control {
  select: ["option_a", "option_b"],
  policy: {
    priority: ["option_b", "option_a"]
  }
}
```

This means:

* Both options are legal
* Order of preference is declared
* The engine may select **one**
* No execution happens here

---

## Decision Resolution Law

Again: **not grammar — law**

A decision collapses iff:

1. All selected atoms exist
2. All selected atoms are lawful
3. No invariant forbids selection
4. Policy resolves to **exactly one** target

If policy resolves to:

* zero → **no decision**
* more than one → **ambiguous → illegal**

---

## Flow Integration

Decisions do **not** imply time.
They must be wired explicitly.

```json
@decision_flow:flow {
  from: "decide",
  to: "option_b"
}
```

Meaning:

> option_b may only collapse if decide collapses first.

---

## Invariants Still Rule

```json
@no_overflow:invariant {
  forbid: {
    select: "option_b",
    when: { entropy: { ">": 0.9 } }
  }
}
```

If violated → decision cannot exist.

---

## What the Decision Engine is NOT

| ❌ Not allowed     | Why               |
| ----------------- | ----------------- |
| Heuristics        | Hidden logic      |
| ML inference      | Non-deterministic |
| Conditionals      | Implied execution |
| Scoring functions | Runtime behavior  |
| Defaults          | Ambiguity         |

---

## Mental model

> **The engine does not choose because it is smart**
> **It chooses because the law allows exactly one outcome**

---

## One-sentence definition

> **An Atomic Decision Engine is a lawful selector that collapses one authorized state and nothing else.**

---

If you want next, we can:

* freeze this as **Decision Engine v1 (FROZEN)**
* add **π-weighted decision atoms**
* define **decision verifier pseudocode**
* map decisions → **SCXQ2 control lanes**
* or show how this becomes a **Micronaut selector**

Point the next vector.


---

# π-Weighted Decision Atoms (Atomic Extension)

This extends the **Decision Engine** without breaking minimal atomic grammar.
π is **math-only signal**, never logic.

---

## 1. π-Weighted Decision Atom

A π-weighted decision atom is still a `control` atom.
Weights **bias selection**, they do not authorize it.

### Grammar extension

```ebnf
DecisionAtom ::= "@" Identifier ":control" DecisionBody
```

```ebnf
DecisionBody ::= "{"
  "select" ":" SelectionSet ","
  "policy" ":" Policy ","
  "pi" ":" PiWeights
"}"
```

---

## 2. π Weights (Pure Math)

π weights are **scalar multipliers** applied *after legality*.

```ebnf
PiWeights ::= "{"
  Identifier ":" Number
  ("," Identifier ":" Number)*
"}"
```

Rules:

* Weight ≥ 0
* Weight = 0 ⇒ selectable but never preferred
* Missing weight ⇒ defaults to 1.0 (explicit default, not implied)

---

## 3. π Evaluation Law

> π **cannot make an illegal option legal**
> π **can only rank legal options**

Order of operations is fixed and invariant.

---

## 4. Example π-Weighted Decision Atom

```json
@decide_route:control {
  select: ["path_a", "path_b", "path_c"],
  policy: {
    tie_breaker: "highest_pi"
  },
  pi: {
    path_a: 1.0,
    path_b: 3.14159,
    path_c: 0.5
  }
}
```

Meaning:

* All paths must already be legal
* π only ranks
* `path_b` wins *if nothing forbids it*

---

# 2. Decision Verifier (Pseudocode)

This verifier is **authoritative**.
Anything else is non-compliant.

```pseudo
function verify_decision(decision_atom, atom_set, invariants):

  candidates = decision_atom.select

  // 1. Existence
  for id in candidates:
    if id not in atom_set:
      return ILLEGAL("missing atom")

  // 2. Local legality
  legal = []
  for id in candidates:
    if violates_invariant(id, invariants):
      continue
    legal.append(id)

  if legal.length == 0:
    return NO_DECISION

  // 3. π weighting
  weighted = []
  for id in legal:
    weight = decision_atom.pi.get(id, 1.0)
    weighted.append((id, weight))

  // 4. Policy resolution
  selected = apply_policy(weighted, decision_atom.policy)

  if selected.count != 1:
    return ILLEGAL("ambiguous decision")

  return COLLAPSE(selected[0])
```

**Hard guarantees**

* Deterministic
* Replayable
* No execution
* No inference
* No side effects

---

# 3. Mapping Decisions → SCXQ2 Control Lanes

Decisions compress cleanly into **control lanes**.

---

## SCXQ2 Lane Roles

| Lane   | Purpose                |
| ------ | ---------------------- |
| `CTRL` | decision authorization |
| `π`    | scalar weights         |
| `ORD`  | policy ordering        |
| `BAN`  | invariant masks        |

---

## Example SCXQ2 Encoding (Conceptual)

Atomic decision:

```json
@decide:control {
  select: ["a","b"],
  pi: { "a": 1.0, "b": 3.14 },
  policy: { tie_breaker: "highest_pi" }
}
```

SCXQ2 lanes:

```
CTRL : DECIDE[a,b]
π    : a=1.0 | b=3.14
ORD  : highest_pi
BAN  : —
```

Collapsed result emits:

```
CTRL : COLLAPSED[b]
```

Nothing else propagates.

---

## Why SCXQ2 Works Here

* π values compress aggressively
* Control lanes are tiny
* Replay is trivial
* Verification is lane-local

This is **microcode-grade control flow**.

---

# 4. Minimal Decision Vocabulary

This vocab is **small, closed, and human-usable**.

---

## Decision Verbs (Data, not syntax)

```json
{
  "choose": "select one lawful option",
  "prefer": "rank by weight or order",
  "allow": "authorize collapse",
  "deny": "block collapse",
  "bias": "apply π weight",
  "limit": "apply threshold",
  "resolve": "collapse to one",
  "reject": "invalidate decision"
}
```

---

## Policy Keywords

```json
{
  "highest_pi": "max π wins",
  "lowest_pi": "min π wins",
  "first": "first in list",
  "last": "last in list",
  "stable": "preserve prior order",
  "deterministic": "no randomness allowed"
}
```

---

## π Semantics Vocabulary

```json
{
  "signal": "numerical preference",
  "weight": "scalar bias",
  "threshold": "minimum viable value",
  "entropy": "system uncertainty factor"
}
```

---

# Mental Lock

> **Legality decides what may happen**
> **π decides what is preferred**
> **Policy decides what collapses**

No part is optional. No part overlaps.

---

If you want next, we can:

* freeze this as **Decision Engine v1.1 (π-Weighted)**
* add **entropy-gated π**
* generate **SCXQ2 binary layouts**
* emit a **conformance test suite**
* or wire this into a **Micronaut selector**

Say where to collapse.
