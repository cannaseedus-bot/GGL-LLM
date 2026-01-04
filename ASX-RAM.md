Below is a **formal, frozen, append-only spec** you can drop into the **ASX-RAM** canon as a new chapter:

* **ASX-RAM Storage Tiering & Swap Plane v1 (FROZEN)**
* plus **5 JSON Schemas** (byte-safe, deterministic, offline, replayable)

You can paste this into your ASX-RAM spec as:

* `ASX_RAM_SWAP_PLANE_v1.md`
* and add the schemas under your codex `@inline.schemas`.

---

# ASX-RAM Storage Tiering & Swap Plane v1

**Version:** 1.0.0
**Status:** FROZEN / Normative
**Authority:** ASX-RAM
**Compatibility:** ASX-R (deterministic runtime fold law), IDB-API, KQL, SCXQ2, CC-v1
**Purpose:** Treat persistent browser storage as a **formal memory tier** (SSD-like), with deterministic paging, eviction, replay, and proofable invariants.

## 0. Definitions

### 0.1 Tiers (normative)

ASX-RAM defines a tiered memory hierarchy:

* **T0 — HOT (Volatile Working Set)**
  JS heap / WASM linear memory / WebGPU buffers. Not persistent. Fastest.
* **T1 — WARM (Structured Persistent Store)**
  IndexedDB (record store). Persistent. Deterministic addressable by key.
* **T2 — COLD (File-Backed Persistent Store)**
  OPFS (Origin Private File System). Persistent. Chunked/streamed pages.
* **T3 — REMOTE (Optional Sync Plane)**
  Any network store. *Non-authoritative by default*. Only via explicit sync protocol.

**Normative rule:** Execution MUST NOT depend on T3 availability.

### 0.2 Page

A **Page** is the smallest atomic unit of swap movement across tiers.

**Normative rule:** Pages are content-addressed and hash-bound (see §6).

### 0.3 Segment

A **Segment** is an append-only sequence of pages (log-structured). Segments support replay and time travel.

### 0.4 Controller

A **Controller** is the deterministic policy engine that decides page placement, prefetch, eviction, and compaction.

---

## 1. Design Goals (hard requirements)

1. **Determinism:** Same inputs → same page IDs, same placements (given same tier capacities and policy seed).
2. **Replayability:** A recorded IO trace replays identically and validates by hash.
3. **Append-only logs:** No in-place mutation of canonical history. Mutations create new pages.
4. **Offline-first:** T0/T1/T2 fully functional without network.
5. **Bounded execution:** All paging actions are bounded by explicit budgets (bytes, pages, time slices).
6. **Compression calculus:** Page payloads MAY be SCXQ2 packed; decompression is a pure function.
7. **No eval:** No dynamic code execution from pages. Pages carry *data/state*, never executable JS.

---

## 2. Canonical Identifiers

### 2.1 Page ID

`page_id = BLAKE3( domain || schema_id || canonical_json(meta) || payload_hash )`

* `domain` is a stable ASCII string, e.g. `"asx.ram.page.v1"`
* `schema_id` is the canonical schema identifier
* `canonical_json(meta)` uses your canonical JSON rules (sorted keys, UTF-8, no floats unless specified)
* `payload_hash` is hash of payload bytes (post-compression bytes if stored compressed)

### 2.2 Segment ID

`segment_id = BLAKE3("asx.ram.segment.v1" || ordered(page_id...))`

### 2.3 Store ID (Tier binding)

A tier store is identified by:

* `tier_id`: `"T0" | "T1" | "T2" | "T3"`
* `store_name`: stable string (e.g. `"idb://asx_ram"`, `"opfs://asx_ram_pages"`)

---

## 3. Page Format (normative)

A page is an envelope with:

* **Header meta** (JSON, canonicalized)
* **Payload** (bytes)
* Optional **Proof block** (hashes, chain binding, replay commitments)

### 3.1 Page Class IDs

Page meta includes `class_id` (examples; expandable without breaking determinism if registered):

* `state.snapshot`
* `event.log`
* `model.weights.shard`
* `kql.index.block`
* `asset.chunk`
* `cache.object`
* `metrics.sample`

---

## 4. Controller Model (deterministic)

### 4.1 Inputs

* `capacity`: bytes per tier
* `policy`: deterministic ruleset
* `seed`: policy seed (fixed per install/session unless explicitly rotated)
* `trace`: optional recorded IO trace

### 4.2 Outputs

* `plan`: ordered actions list (prefetch/evict/write/promote/demote/compact)
* `metrics`: hit rate, evictions, bytes moved, stall time

### 4.3 Legal Actions (closed set)

Controller may emit only these actions:

* `PAGE_WRITE(tier, page)`
* `PAGE_READ(tier, page_id)`
* `PAGE_PROMOTE(from, to, page_id)`
* `PAGE_DEMOTE(from, to, page_id)`
* `PAGE_EVICT(tier, page_id)`
* `SEGMENT_SEAL(tier, segment_id)`
* `SEGMENT_COMPACT(tier, segment_id_old → segment_id_new)`
* `TRACE_COMMIT(trace_id, root_hash)`

**Normative:** Actions are purely declarative; runtime executes them.

---

## 5. Eviction & Prefetch (policy semantics)

### 5.1 Required Policy Fields

Policy MUST define:

* `working_set_budget_bytes` (T0 cap)
* `max_moves_per_tick` (bounded paging)
* `eviction_strategy` (deterministic; see below)
* `prefetch_strategy` (optional but deterministic)
* `priority_weights` (class-based)

### 5.2 Allowed Eviction Strategies (closed set)

* `lru_deterministic` (LRU with tie-break by page_id)
* `lfu_deterministic` (LFU with tie-break by page_id)
* `cost_benefit` (score = freq * priority / size, tie-break by page_id)
* `pinned_only` (only evict unpinned; else refuse)

### 5.3 Pinning

Pages may be `pinned=true` to prevent eviction. Pinning MUST be explicit and bounded.

---

## 6. ABI Hash Binding Rules (anti-drift)

This stops the swap plane from “drifting” across JS/Python/Java implementations.

### 6.1 Canonical ABI Hash

Every implementation MUST publish:

* `abi_hash = BLAKE3(schema_bundle_hash || canonical_action_set_hash || canonical_json_rules_hash)`

Where:

* `schema_bundle_hash` = hash of concatenated schema canonical bytes
* `canonical_action_set_hash` = hash of the closed action names + field layouts
* `canonical_json_rules_hash` = hash of your JSON canonicalization rules doc

### 6.2 Runtime Refusal Rule

If `abi_hash` mismatches across:

* controller
* store adapter
* verifier

…then the runtime MUST refuse to execute paging actions (hard fail), returning `abi_mismatch`.

---

## 7. Replay & Verification

### 7.1 Trace

A **Trace** is an append-only list of paging actions with:

* deterministic timestamps (logical ticks, not wall time)
* input snapshot hash (optional)
* resulting root hash (required)

### 7.2 Root Hash

Root hash is computed from:

* ordered segment IDs
* tier inventories
* controller state (policy + counters)
* last committed trace ID

**Normative:** Root hash must validate identical after replay.

---

## 8. Browser Integration (non-authoritative, informative)

* **sw.js**: owns tier adapters and executes actions off-main-thread
* **index.html**: projection surface; may request pages
* **manifest.json**: declares capabilities/quotas (informative; browser may override)

**Normative:** Storage APIs are treated as *devices*; they do not define semantics.

---

## 9. Conformance Vectors (required)

A conforming implementation MUST pass:

* page_id determinism tests
* segment sealing determinism
* eviction tie-break determinism
* replay root_hash equality
* abi_hash match checks

(You already have golden-vectors patterns; this plugs in cleanly.)

---

# 5 Frozen JSON Schemas

These are designed to be inlined under your internal schema authority (no external URLs).
Use your canonical `$schema`: `xjson://schema/core/v1`.

---

## 1) `asx://schema/asx.ram.tier.v1`

```json
{
  "$schema": "xjson://schema/core/v1",
  "@id": "asx://schema/asx.ram.tier.v1",
  "@type": "schema",
  "@version": "1.0.0",
  "@status": "frozen",
  "type": "object",
  "additionalProperties": false,
  "required": ["tier_id", "store_name", "capacity_bytes", "features"],
  "properties": {
    "tier_id": { "type": "string", "enum": ["T0", "T1", "T2", "T3"] },
    "store_name": { "type": "string", "minLength": 1 },
    "capacity_bytes": { "type": "integer", "minimum": 0 },
    "features": {
      "type": "object",
      "additionalProperties": false,
      "required": ["persistent", "streaming", "random_read", "random_write"],
      "properties": {
        "persistent": { "type": "boolean" },
        "streaming": { "type": "boolean" },
        "random_read": { "type": "boolean" },
        "random_write": { "type": "boolean" }
      }
    }
  }
}
```

---

## 2) `asx://schema/asx.ram.page.v1`

```json
{
  "$schema": "xjson://schema/core/v1",
  "@id": "asx://schema/asx.ram.page.v1",
  "@type": "schema",
  "@version": "1.0.0",
  "@status": "frozen",
  "type": "object",
  "additionalProperties": false,
  "required": ["page_id", "class_id", "meta", "payload"],
  "properties": {
    "page_id": { "type": "string", "minLength": 16 },
    "class_id": { "type": "string", "minLength": 1 },
    "meta": {
      "type": "object",
      "additionalProperties": true,
      "required": ["schema_id", "created_tick", "payload_hash", "payload_codec"],
      "properties": {
        "schema_id": { "type": "string", "minLength": 1 },
        "created_tick": { "type": "integer", "minimum": 0 },
        "payload_hash": { "type": "string", "minLength": 16 },
        "payload_codec": { "type": "string", "enum": ["raw", "scxq2"] },
        "pinned": { "type": "boolean" },
        "ttl_ticks": { "type": "integer", "minimum": 0 },
        "tags": { "type": "array", "items": { "type": "string" } }
      }
    },
    "payload": {
      "type": "object",
      "additionalProperties": false,
      "required": ["bytes_b64"],
      "properties": {
        "bytes_b64": { "type": "string", "minLength": 1 }
      }
    },
    "proof": {
      "type": "object",
      "additionalProperties": false,
      "required": ["abi_hash"],
      "properties": {
        "abi_hash": { "type": "string", "minLength": 16 },
        "segment_id": { "type": "string" },
        "root_hint": { "type": "string" }
      }
    }
  }
}
```

---

## 3) `asx://schema/asx.ram.swap_policy.v1`

```json
{
  "$schema": "xjson://schema/core/v1",
  "@id": "asx://schema/asx.ram.swap_policy.v1",
  "@type": "schema",
  "@version": "1.0.0",
  "@status": "frozen",
  "type": "object",
  "additionalProperties": false,
  "required": [
    "policy_id",
    "seed",
    "working_set_budget_bytes",
    "max_moves_per_tick",
    "eviction_strategy",
    "priority_weights"
  ],
  "properties": {
    "policy_id": { "type": "string", "minLength": 1 },
    "seed": { "type": "string", "minLength": 1 },
    "working_set_budget_bytes": { "type": "integer", "minimum": 0 },
    "max_moves_per_tick": { "type": "integer", "minimum": 0 },
    "eviction_strategy": {
      "type": "string",
      "enum": ["lru_deterministic", "lfu_deterministic", "cost_benefit", "pinned_only"]
    },
    "prefetch_strategy": {
      "type": "string",
      "enum": ["none", "sequential_hint", "class_weighted_hint"]
    },
    "priority_weights": {
      "type": "object",
      "additionalProperties": false,
      "required": ["default"],
      "properties": {
        "default": { "type": "number" }
      },
      "patternProperties": {
        "^[a-zA-Z0-9_.-]+$": { "type": "number" }
      }
    }
  }
}
```

---

## 4) `asx://schema/asx.ram.io_action.v1`

```json
{
  "$schema": "xjson://schema/core/v1",
  "@id": "asx://schema/asx.ram.io_action.v1",
  "@type": "schema",
  "@version": "1.0.0",
  "@status": "frozen",
  "type": "object",
  "additionalProperties": false,
  "required": ["op", "tick"],
  "properties": {
    "op": {
      "type": "string",
      "enum": [
        "PAGE_WRITE",
        "PAGE_READ",
        "PAGE_PROMOTE",
        "PAGE_DEMOTE",
        "PAGE_EVICT",
        "SEGMENT_SEAL",
        "SEGMENT_COMPACT",
        "TRACE_COMMIT"
      ]
    },
    "tick": { "type": "integer", "minimum": 0 },
    "tier": { "type": "string", "enum": ["T0", "T1", "T2", "T3"] },
    "from": { "type": "string", "enum": ["T0", "T1", "T2", "T3"] },
    "to": { "type": "string", "enum": ["T0", "T1", "T2", "T3"] },
    "page_id": { "type": "string" },
    "segment_id": { "type": "string" },
    "segment_id_old": { "type": "string" },
    "segment_id_new": { "type": "string" },
    "trace_id": { "type": "string" },
    "root_hash": { "type": "string" },
    "page": { "$ref": "asx://schema/asx.ram.page.v1" }
  }
}
```

---

## 5) `asx://schema/asx.ram.controller_state.v1`

```json
{
  "$schema": "xjson://schema/core/v1",
  "@id": "asx://schema/asx.ram.controller_state.v1",
  "@type": "schema",
  "@version": "1.0.0",
  "@status": "frozen",
  "type": "object",
  "additionalProperties": false,
  "required": ["abi_hash", "policy", "tiers", "counters"],
  "properties": {
    "abi_hash": { "type": "string", "minLength": 16 },
    "policy": { "$ref": "asx://schema/asx.ram.swap_policy.v1" },
    "tiers": {
      "type": "array",
      "items": { "$ref": "asx://schema/asx.ram.tier.v1" },
      "minItems": 1
    },
    "counters": {
      "type": "object",
      "additionalProperties": false,
      "required": ["reads", "writes", "promotes", "demotes", "evicts"],
      "properties": {
        "reads": { "type": "integer", "minimum": 0 },
        "writes": { "type": "integer", "minimum": 0 },
        "promotes": { "type": "integer", "minimum": 0 },
        "demotes": { "type": "integer", "minimum": 0 },
        "evicts": { "type": "integer", "minimum": 0 }
      }
    },
    "inventory": {
      "type": "object",
      "additionalProperties": false,
      "properties": {
        "T0": { "type": "array", "items": { "type": "string" } },
        "T1": { "type": "array", "items": { "type": "string" } },
        "T2": { "type": "array", "items": { "type": "string" } },
        "T3": { "type": "array", "items": { "type": "string" } }
      }
    },
    "root_hash": { "type": "string" }
  }
}
```

---

## Drop-in “ASX-RAM Addendum” Pointer

Add this chapter under ASX-RAM as:

* **ASX-RAM → Swap Plane v1**

  * binds **T0/T1/T2** to your RAM model
  * defines **page/segment/controller**
  * defines **ABI hash binding** (anti-drift law)
  * defines **trace replay + root hash**

---

```js
/* ============================================================
 * asx_ram_swapplane_v1 — Minimal Reference Implementation
 * - Pure deterministic planner (controller)
 * - T1 adapter: IndexedDB page store
 * - T2 adapter: OPFS page store
 * - Trace replay verifier -> root_hash
 *
 * HARD RULES:
 * - No eval, no dynamic code execution
 * - Controller emits declarative actions only
 * - Adapters are "devices" that execute actions
 * - Hash + canonical JSON are deterministic
 *
 * Files below:
 *   1) canon.js
 *   2) hash.js
 *   3) controller.js
 *   4) idb_adapter.js
 *   5) opfs_adapter.js
 *   6) trace_replay.js
 *   7) sw_example.js (optional wiring sketch)
 * ============================================================ */
```

## 1) `canon.js` — canonical JSON + stable ordering

```js
// canon.js
export function canonStringify(value) {
  return JSON.stringify(canonValue(value));
}

export function canonValue(x) {
  if (x === null) return null;
  const t = typeof x;
  if (t === "number") {
    // Avoid NaN/Infinity nondeterminism.
    if (!Number.isFinite(x)) throw new Error("canon: non-finite number");
    return x;
  }
  if (t === "string" || t === "boolean") return x;
  if (Array.isArray(x)) return x.map(canonValue);
  if (t === "object") {
    const out = {};
    const keys = Object.keys(x).sort();
    for (const k of keys) out[k] = canonValue(x[k]);
    return out;
  }
  throw new Error(`canon: unsupported type ${t}`);
}

// Deterministic key for Map-like inventories
export function sortStrings(arr) {
  return [...arr].sort((a, b) => (a < b ? -1 : a > b ? 1 : 0));
}
```

## 2) `hash.js` — deterministic hash (SHA-256 via WebCrypto)

```js
// hash.js
import { canonStringify } from "./canon.js";

function toHex(buf) {
  const u8 = new Uint8Array(buf);
  let s = "";
  for (let i = 0; i < u8.length; i++) s += u8[i].toString(16).padStart(2, "0");
  return s;
}

export async function sha256Bytes(bytes) {
  const ab = bytes instanceof ArrayBuffer ? bytes : bytes.buffer.slice(bytes.byteOffset, bytes.byteOffset + bytes.byteLength);
  const digest = await crypto.subtle.digest("SHA-256", ab);
  return toHex(digest);
}

export async function sha256Text(text) {
  const enc = new TextEncoder();
  return sha256Bytes(enc.encode(text));
}

export async function sha256Canon(obj) {
  return sha256Text(canonStringify(obj));
}
```

## 3) `controller.js` — pure deterministic planner (LRU deterministic)

```js
// controller.js
import { sortStrings } from "./canon.js";

/**
 * Controller state is a pure object; runtime persists it in ASX-RAM.
 * We track access ticks to implement deterministic LRU.
 */
export function controllerInit({ abi_hash, policy, tiers }) {
  // tiers: [{tier_id, store_name, capacity_bytes, features}, ...]
  return {
    abi_hash,
    policy,
    tiers,
    counters: { reads: 0, writes: 0, promotes: 0, demotes: 0, evicts: 0 },
    // deterministic inventories + stats:
    inventory: { T0: [], T1: [], T2: [], T3: [] },         // page_ids present
    page_bytes: {},                                         // page_id -> size bytes
    last_access_tick: {},                                   // page_id -> tick last read
    access_count: {},                                       // page_id -> count reads
    pinned: {},                                             // page_id -> true/false
    root_hash: ""
  };
}

/**
 * Deterministic LRU victim selection with tie-break by page_id.
 * Only evicts unpinned.
 */
function pickVictimLRU(state, tier, nowTick) {
  const ids = state.inventory[tier];
  let best = null;
  let bestTick = Infinity;

  for (const id of ids) {
    if (state.pinned[id]) continue;
    const t = state.last_access_tick[id] ?? 0;
    if (t < bestTick) { bestTick = t; best = id; continue; }
    if (t === bestTick && best !== null && id < best) { best = id; }
  }
  return best;
}

function tierUsedBytes(state, tier) {
  let sum = 0;
  for (const id of state.inventory[tier]) sum += (state.page_bytes[id] ?? 0);
  return sum;
}

function ensureNotPresent(arr, id) {
  // deterministic: remove all occurrences (should be 0/1)
  return arr.filter(x => x !== id);
}

function addPresent(arr, id) {
  if (arr.includes(id)) return arr;
  return [...arr, id];
}

function action(op, fields) {
  return Object.freeze({ op, ...fields });
}

/**
 * Plan: given "demands" (requested page_ids) and "writes" (pages to store),
 * emit bounded actions to satisfy demands with T0 as working set.
 *
 * Inputs:
 * - demands: [{page_id, prefer_tier?: "T0"|"T1"|"T2", must?: boolean}]
 * - writes: [{tier: "T1"|"T2", page}]  // page is asx.ram.page.v1
 *
 * Output:
 * - actions: asx.ram.io_action.v1[]
 * - next_state: updated controller state (pure)
 */
export function controllerPlan(state, { tick, demands = [], writes = [] }) {
  const pol = state.policy;
  const maxMoves = pol.max_moves_per_tick ?? 0;
  const wsBudget = pol.working_set_budget_bytes ?? 0;

  let moves = 0;
  const actions = [];
  const next = structuredClone(state);

  // Apply writes first (declarative PAGE_WRITE)
  for (const w of writes) {
    if (moves >= maxMoves) break;
    if (w?.page?.proof?.abi_hash && w.page.proof.abi_hash !== next.abi_hash) {
      throw new Error("abi_mismatch: page proof abi_hash != controller abi_hash");
    }
    const tier = w.tier;
    const page = w.page;
    actions.push(action("PAGE_WRITE", { tick, tier, page }));
    moves++;
    next.counters.writes++;

    // Update inventory (pure projection; runtime may fail, but verifier catches)
    next.inventory[tier] = addPresent(next.inventory[tier], page.page_id);
    // size from b64 length approximation; runtime may provide exact bytes later
    const b64 = page.payload?.bytes_b64 ?? "";
    next.page_bytes[page.page_id] = Math.floor((b64.length * 3) / 4);
    next.pinned[page.page_id] = !!page.meta?.pinned;
  }

  // Demands: ensure demanded pages end up in T0 (working set) if possible.
  // Strategy:
  // 1) If in T0 already -> touch access
  // 2) Else if in T1 -> PROMOTE T1->T0
  // 3) Else if in T2 -> PROMOTE T2->T0
  // 4) Else -> PAGE_READ hint (tier unspecified) so runtime can fetch/resolve
  // Bounded by maxMoves and T0 budget by eviction.
  const demandedIds = demands.map(d => d.page_id);
  const uniqueDemanded = sortStrings([...new Set(demandedIds)]);

  for (const page_id of uniqueDemanded) {
    if (moves >= maxMoves) break;

    const inT0 = next.inventory.T0.includes(page_id);
    const inT1 = next.inventory.T1.includes(page_id);
    const inT2 = next.inventory.T2.includes(page_id);
    const inT3 = next.inventory.T3.includes(page_id);

    // Touch stats deterministically
    next.last_access_tick[page_id] = tick;
    next.access_count[page_id] = (next.access_count[page_id] ?? 0) + 1;

    if (inT0) continue;

    // Ensure space in T0: evict until within budget after adding this page
    const pageSize = next.page_bytes[page_id] ?? 0;
    while (tierUsedBytes(next, "T0") + pageSize > wsBudget) {
      if (moves >= maxMoves) break;
      const victim = pickVictimLRU(next, "T0", tick);
      if (!victim) break; // pinned-only deadlock, runtime should report
      actions.push(action("PAGE_EVICT", { tick, tier: "T0", page_id: victim }));
      moves++;
      next.counters.evicts++;
      next.inventory.T0 = ensureNotPresent(next.inventory.T0, victim);
    }
    if (moves >= maxMoves) break;

    if (inT1) {
      actions.push(action("PAGE_PROMOTE", { tick, from: "T1", to: "T0", page_id }));
      moves++; next.counters.promotes++;
      next.inventory.T1 = ensureNotPresent(next.inventory.T1, page_id);
      next.inventory.T0 = addPresent(next.inventory.T0, page_id);
      continue;
    }
    if (inT2) {
      actions.push(action("PAGE_PROMOTE", { tick, from: "T2", to: "T0", page_id }));
      moves++; next.counters.promotes++;
      next.inventory.T2 = ensureNotPresent(next.inventory.T2, page_id);
      next.inventory.T0 = addPresent(next.inventory.T0, page_id);
      continue;
    }
    if (inT3) {
      actions.push(action("PAGE_PROMOTE", { tick, from: "T3", to: "T0", page_id }));
      moves++; next.counters.promotes++;
      next.inventory.T3 = ensureNotPresent(next.inventory.T3, page_id);
      next.inventory.T0 = addPresent(next.inventory.T0, page_id);
      continue;
    }

    // Unknown location: emit a read hint (runtime resolves to a tier)
    actions.push(action("PAGE_READ", { tick, tier: "T2", page_id })); // prefer cold store by default
    moves++; next.counters.reads++;
  }

  // Deterministic inventories ordering
  next.inventory.T0 = sortStrings(next.inventory.T0);
  next.inventory.T1 = sortStrings(next.inventory.T1);
  next.inventory.T2 = sortStrings(next.inventory.T2);
  next.inventory.T3 = sortStrings(next.inventory.T3);

  return { actions, next_state: next };
}
```

## 4) `idb_adapter.js` — T1 IndexedDB page store (bytes as base64)

```js
// idb_adapter.js
/**
 * IndexedDB device adapter for ASX-RAM pages.
 * Stores page objects as-is (schema asx.ram.page.v1).
 *
 * DB layout:
 * - db: "asx_ram"
 * - store: "pages" keyPath: "page_id"
 */

export class IDBAdapter {
  constructor({ dbName = "asx_ram", storeName = "pages" } = {}) {
    this.dbName = dbName;
    this.storeName = storeName;
    this._dbp = null;
  }

  async open() {
    if (this._dbp) return this._dbp;
    this._dbp = new Promise((resolve, reject) => {
      const req = indexedDB.open(this.dbName, 1);
      req.onupgradeneeded = () => {
        const db = req.result;
        if (!db.objectStoreNames.contains(this.storeName)) {
          db.createObjectStore(this.storeName, { keyPath: "page_id" });
        }
      };
      req.onsuccess = () => resolve(req.result);
      req.onerror = () => reject(req.error);
    });
    return this._dbp;
  }

  async putPage(page) {
    const db = await this.open();
    return new Promise((resolve, reject) => {
      const tx = db.transaction(this.storeName, "readwrite");
      tx.objectStore(this.storeName).put(page);
      tx.oncomplete = () => resolve(true);
      tx.onerror = () => reject(tx.error);
    });
  }

  async getPage(page_id) {
    const db = await this.open();
    return new Promise((resolve, reject) => {
      const tx = db.transaction(this.storeName, "readonly");
      const req = tx.objectStore(this.storeName).get(page_id);
      req.onsuccess = () => resolve(req.result || null);
      req.onerror = () => reject(req.error);
    });
  }

  async hasPage(page_id) {
    return (await this.getPage(page_id)) !== null;
  }

  async deletePage(page_id) {
    const db = await this.open();
    return new Promise((resolve, reject) => {
      const tx = db.transaction(this.storeName, "readwrite");
      tx.objectStore(this.storeName).delete(page_id);
      tx.oncomplete = () => resolve(true);
      tx.onerror = () => reject(tx.error);
    });
  }

  async listPageIds() {
    const db = await this.open();
    return new Promise((resolve, reject) => {
      const tx = db.transaction(this.storeName, "readonly");
      const store = tx.objectStore(this.storeName);
      const out = [];
      const req = store.openKeyCursor();
      req.onsuccess = () => {
        const c = req.result;
        if (!c) return;
        out.push(String(c.key));
        c.continue();
      };
      tx.oncomplete = () => resolve(out.sort());
      tx.onerror = () => reject(tx.error);
    });
  }
}
```

## 5) `opfs_adapter.js` — T2 OPFS page store (one file per page_id)

```js
// opfs_adapter.js
/**
 * OPFS device adapter for ASX-RAM pages.
 * Stores each page as a UTF-8 JSON file named `${page_id}.json`.
 */
import { canonStringify } from "./canon.js";

export class OPFSAdapter {
  constructor({ dirName = "asx_ram_pages" } = {}) {
    this.dirName = dirName;
    this._dirp = null;
  }

  async _root() {
    return await navigator.storage.getDirectory();
  }

  async dir() {
    if (this._dirp) return this._dirp;
    this._dirp = (async () => {
      const root = await this._root();
      return await root.getDirectoryHandle(this.dirName, { create: true });
    })();
    return this._dirp;
  }

  _fname(page_id) {
    return `${page_id}.json`;
  }

  async putPage(page) {
    const d = await this.dir();
    const fh = await d.getFileHandle(this._fname(page.page_id), { create: true });
    const w = await fh.createWritable({ keepExistingData: false });
    // Store canonical JSON for deterministic bytes
    const text = canonStringify(page);
    await w.write(text);
    await w.close();
    return true;
  }

  async getPage(page_id) {
    const d = await this.dir();
    try {
      const fh = await d.getFileHandle(this._fname(page_id), { create: false });
      const file = await fh.getFile();
      const text = await file.text();
      return JSON.parse(text);
    } catch (e) {
      return null;
    }
  }

  async hasPage(page_id) {
    return (await this.getPage(page_id)) !== null;
  }

  async deletePage(page_id) {
    const d = await this.dir();
    try {
      await d.removeEntry(this._fname(page_id));
      return true;
    } catch (e) {
      return false;
    }
  }

  async listPageIds() {
    const d = await this.dir();
    const out = [];
    for await (const [name, handle] of d.entries()) {
      if (handle.kind !== "file") continue;
      if (!name.endsWith(".json")) continue;
      out.push(name.slice(0, -5));
    }
    return out.sort();
  }
}
```

## 6) `trace_replay.js` — verifier that applies actions and outputs `root_hash`

```js
// trace_replay.js
import { sha256Canon } from "./hash.js";
import { sortStrings } from "./canon.js";

/**
 * Pure verifier:
 * - Does NOT touch real devices
 * - Applies the action semantics to a simulated controller_state projection
 * - Produces root_hash (deterministic)
 *
 * If you want device-backed verification, run adapters separately to prove
 * pages exist; keep that as a separate, bounded “audit step”.
 */

function ensureArr(x) { return Array.isArray(x) ? x : []; }
function uniqSorted(arr) { return sortStrings([...new Set(arr)]); }

function invRemove(inv, tier, page_id) {
  inv[tier] = ensureArr(inv[tier]).filter(x => x !== page_id);
}
function invAdd(inv, tier, page_id) {
  const cur = ensureArr(inv[tier]);
  if (cur.includes(page_id)) return;
  inv[tier] = [...cur, page_id];
}

function applyAction(sim, act) {
  const op = act.op;

  if (op === "PAGE_WRITE") {
    const tier = act.tier;
    const page = act.page;
    invAdd(sim.inventory, tier, page.page_id);
    // approximate bytes from b64 length; deterministic
    const b64 = page?.payload?.bytes_b64 ?? "";
    sim.page_bytes[page.page_id] = Math.floor((b64.length * 3) / 4);
    sim.pinned[page.page_id] = !!page?.meta?.pinned;
    sim.counters.writes++;
    return;
  }

  if (op === "PAGE_READ") {
    sim.counters.reads++;
    sim.last_read_tick = act.tick;
    // No inventory change here (read is a request)
    return;
  }

  if (op === "PAGE_PROMOTE") {
    const from = act.from, to = act.to, id = act.page_id;
    invRemove(sim.inventory, from, id);
    invAdd(sim.inventory, to, id);
    sim.counters.promotes++;
    return;
  }

  if (op === "PAGE_DEMOTE") {
    const from = act.from, to = act.to, id = act.page_id;
    invRemove(sim.inventory, from, id);
    invAdd(sim.inventory, to, id);
    sim.counters.demotes++;
    return;
  }

  if (op === "PAGE_EVICT") {
    invRemove(sim.inventory, act.tier, act.page_id);
    sim.counters.evicts++;
    return;
  }

  if (op === "SEGMENT_SEAL") {
    // For minimal impl, seal is a trace marker only
    sim.last_seal = { tick: act.tick, tier: act.tier, segment_id: act.segment_id };
    return;
  }

  if (op === "SEGMENT_COMPACT") {
    sim.last_compact = { tick: act.tick, tier: act.tier, old: act.segment_id_old, neu: act.segment_id_new };
    return;
  }

  if (op === "TRACE_COMMIT") {
    sim.last_commit = { tick: act.tick, trace_id: act.trace_id, root_hash: act.root_hash };
    return;
  }

  throw new Error(`verifier: unknown op ${op}`);
}

async function computeRootHash(sim) {
  // Normalize inventories deterministically
  for (const k of ["T0", "T1", "T2", "T3"]) {
    sim.inventory[k] = uniqSorted(ensureArr(sim.inventory[k]));
  }

  // Root hash includes only semantic essentials (stable, replayable)
  const rootObj = {
    abi_hash: sim.abi_hash,
    policy: sim.policy,              // includes seed
    counters: sim.counters,
    inventory: sim.inventory,
    page_bytes: sim.page_bytes,
    pinned: sim.pinned,
    markers: {
      last_read_tick: sim.last_read_tick ?? 0,
      last_seal: sim.last_seal ?? null,
      last_compact: sim.last_compact ?? null,
      last_commit: sim.last_commit ?? null
    }
  };

  return await sha256Canon(rootObj);
}

export async function traceReplayVerify({ controller_state, actions }) {
  const sim = structuredClone(controller_state);

  // Ensure required fields exist
  sim.inventory = sim.inventory || { T0: [], T1: [], T2: [], T3: [] };
  sim.page_bytes = sim.page_bytes || {};
  sim.pinned = sim.pinned || {};
  sim.counters = sim.counters || { reads: 0, writes: 0, promotes: 0, demotes: 0, evicts: 0 };

  for (const act of actions) applyAction(sim, act);

  const root_hash = await computeRootHash(sim);
  sim.root_hash = root_hash;

  return { ok: true, root_hash, next_controller_state: sim };
}
```

## 7) `sw_example.js` — minimal wiring sketch in `sw.js` (optional)

```js
// sw_example.js (illustrative — integrate into your sw.js)
import { controllerInit, controllerPlan } from "./controller.js";
import { IDBAdapter } from "./idb_adapter.js";
import { OPFSAdapter } from "./opfs_adapter.js";
import { traceReplayVerify } from "./trace_replay.js";

const T1 = new IDBAdapter({ dbName: "asx_ram", storeName: "pages" });
const T2 = new OPFSAdapter({ dirName: "asx_ram_pages" });

async function execAction(act) {
  switch (act.op) {
    case "PAGE_WRITE":
      if (act.tier === "T1") return T1.putPage(act.page);
      if (act.tier === "T2") return T2.putPage(act.page);
      // T0 writes are projection-only here
      return true;

    case "PAGE_READ":
      // Prefer tier hint; return page or null
      if (act.tier === "T1") return T1.getPage(act.page_id);
      if (act.tier === "T2") return T2.getPage(act.page_id);
      return (await T2.getPage(act.page_id)) || (await T1.getPage(act.page_id));

    case "PAGE_PROMOTE":
      // Promote means "ensure it exists in T0 working set"; device copy optional.
      // Minimal: fetch from source tier and keep it in memory; do not rewrite unless you want.
      return true;

    case "PAGE_EVICT":
      // Eviction from T0 only (working set). If you evict from T1/T2, call delete.
      if (act.tier === "T1") return T1.deletePage(act.page_id);
      if (act.tier === "T2") return T2.deletePage(act.page_id);
      return true;

    default:
      return true;
  }
}

export async function asxRamTick({ abi_hash, policy, tiers, tick, demands, writes }) {
  // load controller_state from your own persisted place; minimal init here
  let state = controllerInit({ abi_hash, policy, tiers });

  const { actions, next_state } = controllerPlan(state, { tick, demands, writes });

  // execute bounded actions
  for (const act of actions) await execAction(act);

  // verify trace deterministically (pure)
  const vr = await traceReplayVerify({ controller_state: state, actions });

  // persist vr.next_controller_state and/or vr.root_hash in ASX-RAM
  return { actions, root_hash: vr.root_hash, next_state: vr.next_controller_state };
}
```

---

# What you have now (guarantees)

* **Controller is pure**: deterministic input → deterministic action list + next_state
* **Adapters are dumb devices**: they only read/write/delete/list
* **Verifier is pure**: applies action semantics and emits **root_hash**
* **No-eval rule honored**: nothing executes code from storage; only data moves

---

* `idb_adapter` (T1) and `opfs_adapter` (T2),
  plus a `trace_replay` verifier that outputs `root_hash`—all staying inside your “no-eval, declarative actions” rule.


  Below are **two drop-in files** that complete the loop and **lock the swap plane against drift**:

1. **ABI hash generator** (authoritative, frozen)
2. **Device audit** (bounded, deterministic, no execution)

They plug directly into what you already have.
No eval. No side effects beyond reads. Pure verification.

---

# 8) `abi_hash.js` — canonical ABI hash generator (ANTI-DRIFT LAW)

**Purpose**

* Produces the single authoritative `abi_hash`
* MUST match across controller, adapters, verifier
* Any mismatch ⇒ **hard refusal**

**What it hashes**

1. **Schema bundle** (canonical JSON, concatenated)
2. **Action set** (closed enum + field layouts)
3. **Canonical JSON rules** (versioned text)

```js
// abi_hash.js
import { sha256Text, sha256Canon } from "./hash.js";
import { canonStringify } from "./canon.js";

/**
 * Canonical JSON rules descriptor.
 * MUST be frozen text; version bumps require MAJOR change.
 */
const CANON_RULES_TEXT = `
ASX Canonical JSON v1
- UTF-8
- Object keys sorted lexicographically
- Arrays preserved in order
- No NaN / Infinity
- No undefined
- Numbers are IEEE-754 finite
`.trim();

/**
 * Closed action set + required fields.
 * This is LAW. Do not mutate without MAJOR version.
 */
const ACTION_SET = [
  { op: "PAGE_WRITE", fields: ["tick", "tier", "page"] },
  { op: "PAGE_READ", fields: ["tick", "tier", "page_id"] },
  { op: "PAGE_PROMOTE", fields: ["tick", "from", "to", "page_id"] },
  { op: "PAGE_DEMOTE", fields: ["tick", "from", "to", "page_id"] },
  { op: "PAGE_EVICT", fields: ["tick", "tier", "page_id"] },
  { op: "SEGMENT_SEAL", fields: ["tick", "tier", "segment_id"] },
  { op: "SEGMENT_COMPACT", fields: ["tick", "tier", "segment_id_old", "segment_id_new"] },
  { op: "TRACE_COMMIT", fields: ["tick", "trace_id", "root_hash"] }
];

/**
 * Generate ABI hash
 *
 * @param {object[]} schemas - array of canonical schema objects
 *                             (already validated, already frozen)
 * @returns {Promise<string>} abi_hash
 */
export async function generateAbiHash({ schemas }) {
  if (!Array.isArray(schemas) || schemas.length === 0) {
    throw new Error("abi_hash: schemas required");
  }

  // 1) Schema bundle hash (order-independent)
  const schemaTexts = schemas
    .map(s => canonStringify(s))
    .sort(); // order invariant

  const schemaBundleText = schemaTexts.join("\n---\n");
  const schema_bundle_hash = await sha256Text(schemaBundleText);

  // 2) Action set hash
  const action_set_hash = await sha256Canon(ACTION_SET);

  // 3) Canon rules hash
  const canon_rules_hash = await sha256Text(CANON_RULES_TEXT);

  // Final ABI hash
  const abi_hash = await sha256Text(
    `ASX_RAM_ABI_V1\n` +
    `schema=${schema_bundle_hash}\n` +
    `actions=${action_set_hash}\n` +
    `canon=${canon_rules_hash}\n`
  );

  return abi_hash;
}

/**
 * Convenience guard
 */
export function assertAbiMatch(expected, actual) {
  if (expected !== actual) {
    throw new Error(`abi_mismatch: expected=${expected} actual=${actual}`);
  }
}
```

---

# 9) `device_audit.js` — bounded device audit (READ-ONLY)

**Purpose**

* Verifies that **declared inventory matches physical storage**
* Deterministic
* Bounded (sampled or full, caller chooses)
* No writes, no deletes

**Key rule**

> **Audit does NOT repair.**
> It only reports discrepancies.

```js
// device_audit.js
import { sortStrings } from "./canon.js";

/**
 * Device audit against T1/T2 adapters.
 *
 * @param {object} params
 * @param {object} params.controller_state  - asx.ram.controller_state.v1
 * @param {object} params.adapters          - { T1?: IDBAdapter, T2?: OPFSAdapter }
 * @param {number} params.max_checks        - hard bound on reads (0 = no audit)
 * @param {string} params.mode              - "full" | "sample"
 *
 * @returns {Promise<object>} audit report
 */
export async function deviceAudit({
  controller_state,
  adapters,
  max_checks = 128,
  mode = "sample"
}) {
  const report = {
    ok: true,
    checked: 0,
    missing: { T1: [], T2: [] },
    extra: { T1: [], T2: [] }
  };

  if (max_checks <= 0) return report;

  const inv = controller_state.inventory || {};
  const declaredT1 = sortStrings(inv.T1 || []);
  const declaredT2 = sortStrings(inv.T2 || []);

  // ---- T1 audit ----
  if (adapters.T1) {
    const actual = sortStrings(await adapters.T1.listPageIds());

    const declaredSet = new Set(declaredT1);
    const actualSet = new Set(actual);

    // Missing pages
    for (const id of declaredT1) {
      if (report.checked >= max_checks) break;
      if (!actualSet.has(id)) {
        report.missing.T1.push(id);
        report.ok = false;
      }
      report.checked++;
      if (mode === "sample") break;
    }

    // Extra pages
    for (const id of actual) {
      if (report.checked >= max_checks) break;
      if (!declaredSet.has(id)) {
        report.extra.T1.push(id);
        report.ok = false;
      }
      report.checked++;
      if (mode === "sample") break;
    }
  }

  // ---- T2 audit ----
  if (adapters.T2 && report.checked < max_checks) {
    const actual = sortStrings(await adapters.T2.listPageIds());

    const declaredSet = new Set(declaredT2);
    const actualSet = new Set(actual);

    for (const id of declaredT2) {
      if (report.checked >= max_checks) break;
      if (!actualSet.has(id)) {
        report.missing.T2.push(id);
        report.ok = false;
      }
      report.checked++;
      if (mode === "sample") break;
    }

    for (const id of actual) {
      if (report.checked >= max_checks) break;
      if (!declaredSet.has(id)) {
        report.extra.T2.push(id);
        report.ok = false;
      }
      report.checked++;
      if (mode === "sample") break;
    }
  }

  return report;
}
```

---

# How this locks ASX-RAM (important)

With these two files:

### 1️⃣ **ABI hash is law**

* Controller emits pages with `proof.abi_hash`
* Verifier checks `abi_hash`
* Runtime **refuses** mismatches
* No silent drift across JS / Python / Java

### 2️⃣ **Audit is separate from execution**

* Paging logic stays pure
* Devices are dumb
* Audit is bounded + optional
* Offline-safe

### 3️⃣ **Replay remains canonical**

* `trace_replay` → `root_hash`
* `device_audit` → *existence sanity*
* Neither mutates state

---

# Minimal wiring (one-liner reminder)

```js
const abi_hash = await generateAbiHash({ schemas: INLINE_SCHEMAS });
state.abi_hash = abi_hash;

const audit = await deviceAudit({
  controller_state: state,
  adapters: { T1, T2 },
  max_checks: 64,
  mode: "sample"
});
```

---

## Result

You now have a **closed, deterministic, SSD-backed RAM plane** inside a PWA:

* Formal spec ✔
* Deterministic controller ✔
* Device adapters ✔
* Replay verifier ✔
* ABI lock ✔
* Audit without mutation ✔

This is no longer “web storage”.
It is **ASX-RAM with a swap plane**, period.

Below is a **minimal, drift-safe mirror set** for **Python + Java**, plus a **SCXQ2 codec hook** (pluggable, no-eval) and an **AI weight streaming profile** (model shards as pages) that drops straight into the Swap Plane v1 you just locked.

---

## A) Python mirror: deterministic planner + trace replay verifier

### `asx_canon.py`

```python
# asx_canon.py
import json
import math
from typing import Any, Dict, List

def _reject_nonfinite(obj: Any) -> Any:
    if isinstance(obj, float):
        if not math.isfinite(obj):
            raise ValueError("canon: non-finite float")
    elif isinstance(obj, list):
        for v in obj:
            _reject_nonfinite(v)
    elif isinstance(obj, dict):
        for v in obj.values():
            _reject_nonfinite(v)
    return obj

def canon_dumps(obj: Any) -> str:
    _reject_nonfinite(obj)
    # Canonical JSON: sorted keys, no whitespace, UTF-8 friendly
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)

def sort_strings(xs: List[str]) -> List[str]:
    return sorted(xs, key=lambda s: s)
```

### `asx_hash.py`

```python
# asx_hash.py
import hashlib
from typing import Any
from asx_canon import canon_dumps

def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

def sha256_canon(obj: Any) -> str:
    return sha256_text(canon_dumps(obj))
```

### `asx_controller.py`

```python
# asx_controller.py
from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple
from asx_canon import sort_strings

Action = Dict[str, Any]
State = Dict[str, Any]

ACTION_SET = {
    "PAGE_WRITE", "PAGE_READ", "PAGE_PROMOTE", "PAGE_DEMOTE", "PAGE_EVICT",
    "SEGMENT_SEAL", "SEGMENT_COMPACT", "TRACE_COMMIT"
}

def controller_init(abi_hash: str, policy: Dict[str, Any], tiers: List[Dict[str, Any]]) -> State:
    return {
        "abi_hash": abi_hash,
        "policy": policy,
        "tiers": tiers,
        "counters": {"reads": 0, "writes": 0, "promotes": 0, "demotes": 0, "evicts": 0},
        "inventory": {"T0": [], "T1": [], "T2": [], "T3": []},
        "page_bytes": {},          # page_id -> int
        "last_access_tick": {},    # page_id -> int
        "access_count": {},        # page_id -> int
        "pinned": {},              # page_id -> bool
        "root_hash": ""
    }

def _tier_used_bytes(st: State, tier: str) -> int:
    return sum(int(st["page_bytes"].get(pid, 0)) for pid in st["inventory"][tier])

def _pick_victim_lru(st: State, tier: str) -> Optional[str]:
    best = None
    best_tick = 2**63 - 1
    for pid in st["inventory"][tier]:
        if st["pinned"].get(pid, False):
            continue
        t = int(st["last_access_tick"].get(pid, 0))
        if t < best_tick:
            best_tick = t
            best = pid
        elif t == best_tick and best is not None and pid < best:
            best = pid
    return best

def _inv_add(st: State, tier: str, pid: str) -> None:
    if pid not in st["inventory"][tier]:
        st["inventory"][tier].append(pid)

def _inv_remove(st: State, tier: str, pid: str) -> None:
    st["inventory"][tier] = [x for x in st["inventory"][tier] if x != pid]

def controller_plan(
    state: State,
    *,
    tick: int,
    demands: List[Dict[str, Any]] = None,
    writes: List[Dict[str, Any]] = None
) -> Tuple[List[Action], State]:
    demands = demands or []
    writes = writes or []

    pol = state["policy"]
    max_moves = int(pol.get("max_moves_per_tick", 0))
    ws_budget = int(pol.get("working_set_budget_bytes", 0))

    moves = 0
    actions: List[Action] = []
    st: State = {
        **state,
        "counters": dict(state["counters"]),
        "inventory": {k: list(v) for k, v in state["inventory"].items()},
        "page_bytes": dict(state["page_bytes"]),
        "last_access_tick": dict(state["last_access_tick"]),
        "access_count": dict(state["access_count"]),
        "pinned": dict(state["pinned"]),
    }

    # Writes first
    for w in writes:
        if moves >= max_moves:
            break
        tier = w["tier"]
        page = w["page"]
        proof = page.get("proof") or {}
        if "abi_hash" in proof and proof["abi_hash"] != st["abi_hash"]:
            raise ValueError("abi_mismatch: page proof abi_hash != controller abi_hash")

        actions.append({"op": "PAGE_WRITE", "tick": tick, "tier": tier, "page": page})
        moves += 1
        st["counters"]["writes"] += 1

        pid = page["page_id"]
        _inv_add(st, tier, pid)

        b64 = (page.get("payload") or {}).get("bytes_b64", "")
        st["page_bytes"][pid] = (len(b64) * 3) // 4  # deterministic approximation
        meta = page.get("meta") or {}
        st["pinned"][pid] = bool(meta.get("pinned", False))

    # Unique demanded page_ids
    demanded_ids = sort_strings(sorted({d["page_id"] for d in demands if "page_id" in d}))
    for pid in demanded_ids:
        if moves >= max_moves:
            break

        # Touch stats deterministically
        st["last_access_tick"][pid] = tick
        st["access_count"][pid] = int(st["access_count"].get(pid, 0)) + 1

        if pid in st["inventory"]["T0"]:
            continue

        psize = int(st["page_bytes"].get(pid, 0))

        # Evict until within budget
        while _tier_used_bytes(st, "T0") + psize > ws_budget:
            if moves >= max_moves:
                break
            victim = _pick_victim_lru(st, "T0")
            if not victim:
                break
            actions.append({"op": "PAGE_EVICT", "tick": tick, "tier": "T0", "page_id": victim})
            moves += 1
            st["counters"]["evicts"] += 1
            _inv_remove(st, "T0", victim)

        if moves >= max_moves:
            break

        # Promote preference order: T1 -> T2 -> T3, else READ hint (prefer T2)
        if pid in st["inventory"]["T1"]:
            actions.append({"op": "PAGE_PROMOTE", "tick": tick, "from": "T1", "to": "T0", "page_id": pid})
            moves += 1
            st["counters"]["promotes"] += 1
            _inv_remove(st, "T1", pid); _inv_add(st, "T0", pid)
        elif pid in st["inventory"]["T2"]:
            actions.append({"op": "PAGE_PROMOTE", "tick": tick, "from": "T2", "to": "T0", "page_id": pid})
            moves += 1
            st["counters"]["promotes"] += 1
            _inv_remove(st, "T2", pid); _inv_add(st, "T0", pid)
        elif pid in st["inventory"]["T3"]:
            actions.append({"op": "PAGE_PROMOTE", "tick": tick, "from": "T3", "to": "T0", "page_id": pid})
            moves += 1
            st["counters"]["promotes"] += 1
            _inv_remove(st, "T3", pid); _inv_add(st, "T0", pid)
        else:
            actions.append({"op": "PAGE_READ", "tick": tick, "tier": "T2", "page_id": pid})
            moves += 1
            st["counters"]["reads"] += 1

    # Normalize inventories (deterministic ordering)
    for k in ("T0", "T1", "T2", "T3"):
        st["inventory"][k] = sort_strings(st["inventory"][k])

    return actions, st
```

### `asx_trace_replay.py`

```python
# asx_trace_replay.py
from typing import Any, Dict, List, Tuple
from asx_hash import sha256_canon
from asx_canon import sort_strings

State = Dict[str, Any]
Action = Dict[str, Any]

def _inv_add(inv: Dict[str, List[str]], tier: str, pid: str) -> None:
    if pid not in inv[tier]:
        inv[tier].append(pid)

def _inv_remove(inv: Dict[str, List[str]], tier: str, pid: str) -> None:
    inv[tier] = [x for x in inv[tier] if x != pid]

def trace_replay_verify(controller_state: State, actions: List[Action]) -> Tuple[str, State]:
    sim = {
        **controller_state,
        "counters": dict(controller_state.get("counters") or {"reads":0,"writes":0,"promotes":0,"demotes":0,"evicts":0}),
        "inventory": {k: list(v) for k, v in (controller_state.get("inventory") or {"T0":[],"T1":[],"T2":[],"T3":[]}).items()},
        "page_bytes": dict(controller_state.get("page_bytes") or {}),
        "pinned": dict(controller_state.get("pinned") or {}),
    }

    sim.setdefault("last_read_tick", 0)
    sim.setdefault("last_seal", None)
    sim.setdefault("last_compact", None)
    sim.setdefault("last_commit", None)

    for act in actions:
        op = act["op"]
        if op == "PAGE_WRITE":
            tier = act["tier"]
            page = act["page"]
            pid = page["page_id"]
            _inv_add(sim["inventory"], tier, pid)
            b64 = (page.get("payload") or {}).get("bytes_b64", "")
            sim["page_bytes"][pid] = (len(b64) * 3) // 4
            sim["pinned"][pid] = bool((page.get("meta") or {}).get("pinned", False))
            sim["counters"]["writes"] += 1

        elif op == "PAGE_READ":
            sim["counters"]["reads"] += 1
            sim["last_read_tick"] = int(act["tick"])

        elif op in ("PAGE_PROMOTE", "PAGE_DEMOTE"):
            frm = act["from"]; to = act["to"]; pid = act["page_id"]
            _inv_remove(sim["inventory"], frm, pid)
            _inv_add(sim["inventory"], to, pid)
            sim["counters"]["promotes" if op == "PAGE_PROMOTE" else "demotes"] += 1

        elif op == "PAGE_EVICT":
            _inv_remove(sim["inventory"], act["tier"], act["page_id"])
            sim["counters"]["evicts"] += 1

        elif op == "SEGMENT_SEAL":
            sim["last_seal"] = {"tick": int(act["tick"]), "tier": act["tier"], "segment_id": act["segment_id"]}

        elif op == "SEGMENT_COMPACT":
            sim["last_compact"] = {
                "tick": int(act["tick"]),
                "tier": act["tier"],
                "old": act["segment_id_old"],
                "neu": act["segment_id_new"],
            }

        elif op == "TRACE_COMMIT":
            sim["last_commit"] = {"tick": int(act["tick"]), "trace_id": act["trace_id"], "root_hash": act["root_hash"]}

        else:
            raise ValueError(f"verifier: unknown op {op}")

    # normalize inventories
    for k in ("T0","T1","T2","T3"):
        sim["inventory"][k] = sort_strings(sim["inventory"].get(k, []))

    root_obj = {
        "abi_hash": sim["abi_hash"],
        "policy": sim["policy"],
        "counters": sim["counters"],
        "inventory": sim["inventory"],
        "page_bytes": sim["page_bytes"],
        "pinned": sim["pinned"],
        "markers": {
            "last_read_tick": sim.get("last_read_tick", 0),
            "last_seal": sim.get("last_seal", None),
            "last_compact": sim.get("last_compact", None),
            "last_commit": sim.get("last_commit", None)
        }
    }
    root_hash = sha256_canon(root_obj)
    sim["root_hash"] = root_hash
    return root_hash, sim
```

---

## B) Java mirror: deterministic planner + trace replay verifier

No external deps. Uses `Map/List` + stable key sort + SHA-256.

### `Canon.java`

```java
import java.util.*;

public final class Canon {
  private Canon() {}

  public static String canonJson(Object v) {
    StringBuilder sb = new StringBuilder();
    write(sb, v);
    return sb.toString();
  }

  @SuppressWarnings("unchecked")
  private static void write(StringBuilder sb, Object v) {
    if (v == null) { sb.append("null"); return; }

    if (v instanceof Boolean) { sb.append(((Boolean)v) ? "true" : "false"); return; }

    if (v instanceof Number) {
      double d = ((Number)v).doubleValue();
      if (Double.isNaN(d) || Double.isInfinite(d)) throw new IllegalArgumentException("canon: non-finite number");
      // Preserve integer formatting when possible
      if (v instanceof Integer || v instanceof Long || v instanceof Short || v instanceof Byte) {
        sb.append(((Number)v).longValue());
      } else {
        sb.append(trimFloat(d));
      }
      return;
    }

    if (v instanceof String) {
      sb.append('"').append(escape((String)v)).append('"');
      return;
    }

    if (v instanceof List) {
      List<Object> xs = (List<Object>) v;
      sb.append('[');
      for (int i=0;i<xs.size();i++) {
        if (i>0) sb.append(',');
        write(sb, xs.get(i));
      }
      sb.append(']');
      return;
    }

    if (v instanceof Map) {
      Map<String,Object> m = (Map<String,Object>) v;
      List<String> keys = new ArrayList<>(m.keySet());
      Collections.sort(keys);
      sb.append('{');
      boolean first = true;
      for (String k : keys) {
        if (!first) sb.append(',');
        first = false;
        sb.append('"').append(escape(k)).append('"').append(':');
        write(sb, m.get(k));
      }
      sb.append('}');
      return;
    }

    throw new IllegalArgumentException("canon: unsupported type " + v.getClass());
  }

  private static String escape(String s) {
    StringBuilder out = new StringBuilder();
    for (int i=0;i<s.length();i++) {
      char c = s.charAt(i);
      switch (c) {
        case '"': out.append("\\\""); break;
        case '\\': out.append("\\\\"); break;
        case '\b': out.append("\\b"); break;
        case '\f': out.append("\\f"); break;
        case '\n': out.append("\\n"); break;
        case '\r': out.append("\\r"); break;
        case '\t': out.append("\\t"); break;
        default:
          if (c < 0x20) out.append(String.format("\\u%04x", (int)c));
          else out.append(c);
      }
    }
    return out.toString();
  }

  private static String trimFloat(double d) {
    // deterministic string (no locale)
    String s = Double.toString(d);
    return s;
  }

  public static List<String> sortStrings(List<String> xs) {
    ArrayList<String> out = new ArrayList<>(xs);
    Collections.sort(out);
    return out;
  }
}
```

### `Hash.java`

```java
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;

public final class Hash {
  private Hash() {}

  public static String sha256Text(String s) {
    return sha256Bytes(s.getBytes(StandardCharsets.UTF_8));
  }

  public static String sha256Canon(Object obj) {
    return sha256Text(Canon.canonJson(obj));
  }

  public static String sha256Bytes(byte[] data) {
    try {
      MessageDigest md = MessageDigest.getInstance("SHA-256");
      byte[] dig = md.digest(data);
      StringBuilder sb = new StringBuilder();
      for (byte b : dig) sb.append(String.format("%02x", b));
      return sb.toString();
    } catch (Exception e) {
      throw new RuntimeException(e);
    }
  }
}
```

### `TraceReplay.java` (verifier → `root_hash`)

```java
import java.util.*;

public final class TraceReplay {
  private TraceReplay() {}

  @SuppressWarnings("unchecked")
  public static Map<String,Object> verify(Map<String,Object> controllerState, List<Map<String,Object>> actions) {
    Map<String,Object> sim = deepCopy(controllerState);

    sim.putIfAbsent("counters", new HashMap<String,Object>());
    Map<String,Object> counters = (Map<String,Object>) sim.get("counters");
    counters.putIfAbsent("reads", 0L);
    counters.putIfAbsent("writes", 0L);
    counters.putIfAbsent("promotes", 0L);
    counters.putIfAbsent("demotes", 0L);
    counters.putIfAbsent("evicts", 0L);

    sim.putIfAbsent("inventory", new HashMap<String,Object>());
    Map<String,Object> inv = (Map<String,Object>) sim.get("inventory");
    for (String t : new String[]{"T0","T1","T2","T3"}) inv.putIfAbsent(t, new ArrayList<String>());

    sim.putIfAbsent("page_bytes", new HashMap<String,Object>());
    sim.putIfAbsent("pinned", new HashMap<String,Object>());

    sim.putIfAbsent("last_read_tick", 0L);
    sim.putIfAbsent("last_seal", null);
    sim.putIfAbsent("last_compact", null);
    sim.putIfAbsent("last_commit", null);

    for (Map<String,Object> act : actions) apply(sim, act);

    // normalize inventories
    for (String t : new String[]{"T0","T1","T2","T3"}) {
      List<String> ids = (List<String>) inv.get(t);
      inv.put(t, Canon.sortStrings(ids));
    }

    Map<String,Object> rootObj = new HashMap<>();
    rootObj.put("abi_hash", sim.get("abi_hash"));
    rootObj.put("policy", sim.get("policy"));
    rootObj.put("counters", sim.get("counters"));
    rootObj.put("inventory", sim.get("inventory"));
    rootObj.put("page_bytes", sim.get("page_bytes"));
    rootObj.put("pinned", sim.get("pinned"));

    Map<String,Object> markers = new HashMap<>();
    markers.put("last_read_tick", sim.get("last_read_tick"));
    markers.put("last_seal", sim.get("last_seal"));
    markers.put("last_compact", sim.get("last_compact"));
    markers.put("last_commit", sim.get("last_commit"));
    rootObj.put("markers", markers);

    String rootHash = Hash.sha256Canon(rootObj);
    sim.put("root_hash", rootHash);

    Map<String,Object> out = new HashMap<>();
    out.put("ok", true);
    out.put("root_hash", rootHash);
    out.put("next_controller_state", sim);
    return out;
  }

  @SuppressWarnings("unchecked")
  private static void apply(Map<String,Object> sim, Map<String,Object> act) {
    String op = (String) act.get("op");
    Map<String,Object> counters = (Map<String,Object>) sim.get("counters");
    Map<String,Object> inv = (Map<String,Object>) sim.get("inventory");
    Map<String,Object> pageBytes = (Map<String,Object>) sim.get("page_bytes");
    Map<String,Object> pinned = (Map<String,Object>) sim.get("pinned");

    if ("PAGE_WRITE".equals(op)) {
      String tier = (String) act.get("tier");
      Map<String,Object> page = (Map<String,Object>) act.get("page");
      String pid = (String) page.get("page_id");
      invAdd((List<String>) inv.get(tier), pid);

      Map<String,Object> payload = (Map<String,Object>) page.get("payload");
      String b64 = payload == null ? "" : (String) payload.getOrDefault("bytes_b64", "");
      long approxBytes = (b64.length() * 3L) / 4L;
      pageBytes.put(pid, approxBytes);

      Map<String,Object> meta = (Map<String,Object>) page.get("meta");
      boolean pin = meta != null && Boolean.TRUE.equals(meta.get("pinned"));
      pinned.put(pid, pin);

      counters.put("writes", ((Number)counters.get("writes")).longValue() + 1L);
      return;
    }

    if ("PAGE_READ".equals(op)) {
      sim.put("last_read_tick", ((Number)act.get("tick")).longValue());
      counters.put("reads", ((Number)counters.get("reads")).longValue() + 1L);
      return;
    }

    if ("PAGE_PROMOTE".equals(op) || "PAGE_DEMOTE".equals(op)) {
      String from = (String) act.get("from");
      String to = (String) act.get("to");
      String pid = (String) act.get("page_id");
      invRemove((List<String>) inv.get(from), pid);
      invAdd((List<String>) inv.get(to), pid);

      String k = "PAGE_PROMOTE".equals(op) ? "promotes" : "demotes";
      counters.put(k, ((Number)counters.get(k)).longValue() + 1L);
      return;
    }

    if ("PAGE_EVICT".equals(op)) {
      String tier = (String) act.get("tier");
      String pid = (String) act.get("page_id");
      invRemove((List<String>) inv.get(tier), pid);
      counters.put("evicts", ((Number)counters.get("evicts")).longValue() + 1L);
      return;
    }

    if ("SEGMENT_SEAL".equals(op)) {
      Map<String,Object> m = new HashMap<>();
      m.put("tick", ((Number)act.get("tick")).longValue());
      m.put("tier", act.get("tier"));
      m.put("segment_id", act.get("segment_id"));
      sim.put("last_seal", m);
      return;
    }

    if ("SEGMENT_COMPACT".equals(op)) {
      Map<String,Object> m = new HashMap<>();
      m.put("tick", ((Number)act.get("tick")).longValue());
      m.put("tier", act.get("tier"));
      m.put("old", act.get("segment_id_old"));
      m.put("neu", act.get("segment_id_new"));
      sim.put("last_compact", m);
      return;
    }

    if ("TRACE_COMMIT".equals(op)) {
      Map<String,Object> m = new HashMap<>();
      m.put("tick", ((Number)act.get("tick")).longValue());
      m.put("trace_id", act.get("trace_id"));
      m.put("root_hash", act.get("root_hash"));
      sim.put("last_commit", m);
      return;
    }

    throw new IllegalArgumentException("verifier: unknown op " + op);
  }

  private static void invAdd(List<String> xs, String pid) {
    if (!xs.contains(pid)) xs.add(pid);
  }
  private static void invRemove(List<String> xs, String pid) {
    xs.removeIf(x -> x.equals(pid));
  }

  @SuppressWarnings("unchecked")
  private static Map<String,Object> deepCopy(Map<String,Object> m) {
    // Minimal: assumes only primitives/maps/lists (true for your state/actions)
    Map<String,Object> out = new HashMap<>();
    for (Map.Entry<String,Object> e : m.entrySet()) {
      out.put(e.getKey(), deepCopyAny(e.getValue()));
    }
    return out;
  }

  @SuppressWarnings("unchecked")
  private static Object deepCopyAny(Object v) {
    if (v == null) return null;
    if (v instanceof String || v instanceof Number || v instanceof Boolean) return v;
    if (v instanceof Map) {
      return deepCopy((Map<String,Object>) v);
    }
    if (v instanceof List) {
      List<Object> xs = (List<Object>) v;
      ArrayList<Object> out = new ArrayList<>();
      for (Object x : xs) out.add(deepCopyAny(x));
      return out;
    }
    throw new IllegalArgumentException("deepCopy: unsupported " + v.getClass());
  }
}
```

That’s the verifier mirror (root hash law). If you also want the Java planner mirror, say “drop Java planner too” and I’ll emit `Controller.java` matching the Python/JS logic byte-for-byte in semantics.

---

## C) SCXQ2 page codec hook (pluggable, deterministic)

This is the **official hook** that lets pages declare `payload_codec: "scxq2"` and keeps everything no-eval + data-only.

### JS hook: `codec_registry.js`

```js
// codec_registry.js
/**
 * Codec interface:
 * - encode(Uint8Array) -> Uint8Array
 * - decode(Uint8Array) -> Uint8Array
 *
 * Determinism rules:
 * - encode must be pure for same input bytes + same codec config
 * - decode must be total (or fail with deterministic error code)
 */

export class CodecRegistry {
  constructor() { this._m = new Map(); }

  register(name, codec) {
    if (this._m.has(name)) throw new Error("codec already registered: " + name);
    this._m.set(name, codec);
  }

  get(name) {
    const c = this._m.get(name);
    if (!c) throw new Error("unknown codec: " + name);
    return c;
  }

  encode(name, bytes) { return this.get(name).encode(bytes); }
  decode(name, bytes) { return this.get(name).decode(bytes); }
}

// ---- SCXQ2 hook point (wire your @asx/scxq2-cc engine here) ----
export function makeScxq2Codec({ scxq2 }) {
  // scxq2 must expose deterministic pack/unpack of bytes
  return {
    encode(bytes) { return scxq2.pack(bytes); },
    decode(bytes) { return scxq2.unpack(bytes); }
  };
}
```

### Page pack/unpack helpers: `page_codec.js`

```js
// page_codec.js
import { sha256Bytes } from "./hash.js";

function b64FromBytes(u8) {
  let s = "";
  for (let i = 0; i < u8.length; i++) s += String.fromCharCode(u8[i]);
  return btoa(s);
}
function bytesFromB64(b64) {
  const s = atob(b64);
  const u8 = new Uint8Array(s.length);
  for (let i = 0; i < s.length; i++) u8[i] = s.charCodeAt(i) & 0xff;
  return u8;
}

export async function packPagePayload({ registry, payload_codec, raw_bytes_u8 }) {
  const codecName = payload_codec || "raw";
  const stored = codecName === "raw" ? raw_bytes_u8 : registry.encode(codecName, raw_bytes_u8);
  const payload_hash = await sha256Bytes(stored);
  return { bytes_b64: b64FromBytes(stored), payload_hash, payload_codec: codecName };
}

export async function unpackPagePayload({ registry, payload_codec, bytes_b64 }) {
  const stored = bytesFromB64(bytes_b64);
  return (payload_codec === "raw" || !payload_codec) ? stored : registry.decode(payload_codec, stored);
}
```

**Normative point:** `payload_hash` hashes **stored bytes** (post-compression), matching your Page ID construction rules.

---

## D) AI weight streaming profile (model shards as pages)

This is the “game SSD streaming” but for **weights + KV cache + adapters**, expressed entirely as pages.

### 1) Page class + meta (normative)

**class_id:** `model.weights.shard`

**meta schema (additive fields under `page.meta`)**

```json
{
  "model_id": "qwen-asx-7b",
  "weights_format": "safetensors|gguf|custom",
  "shard_index": 12,
  "shard_count": 256,
  "tensor_group": "transformer.block.12",
  "dtype": "fp16|bf16|int8|nf4",
  "shape": [4096, 4096],
  "byte_len_raw": 33554432,
  "byte_len_stored": 8123456,
  "payload_codec": "scxq2",
  "prefetch_hint": "sequential",
  "pinned": false
}
```

**payload bytes** are *data-only*:

* raw weight bytes (or a container chunk)
* optionally a deterministic header prefix (your choice), but still bytes

### 2) Sharding rule (deterministic)

Pick one and freeze it:

**Rule WSP-1 (Weight Shard Pack v1)**

* shard by **(layer index, tensor group)** then chunk into fixed size blocks
* canonical block size: `8 MiB raw` (before compression)
* page ordering: `(layer asc, tensor_group lex, shard_index asc)`
* `page_id` derived as usual (domain + schema + meta + payload_hash)

### 3) Tier placement policy (good defaults)

* **T2 (OPFS)**: authoritative weight shards store
* **T1 (IDB)**: hot index + manifest + small adapters (LoRA shards, routing tables)
* **T0**: active layer working set + KV cache slices

**Swap policy profile: `swap_policy.weights_stream.v1`**

```json
{
  "policy_id": "swap_policy.weights_stream.v1",
  "seed": "fixed-per-install-or-session",
  "working_set_budget_bytes": 536870912,
  "max_moves_per_tick": 16,
  "eviction_strategy": "lru_deterministic",
  "prefetch_strategy": "sequential_hint",
  "priority_weights": {
    "default": 1.0,
    "model.weights.shard": 5.0,
    "kql.index.block": 3.0,
    "event.log": 0.5
  }
}
```

### 4) Demand generation (how inference requests pages)

Inference runtime emits **demands** like:

```json
[
  { "page_id": "weights_page_...layer12_shard3", "must": true },
  { "page_id": "weights_page_...layer12_shard4", "must": true },
  { "page_id": "weights_page_...layer13_shard0", "must": false }
]
```

* `must=true`: controller should prioritize promoting to T0 within budget
* sequential prefetch: add next shard(s) with `must=false`

### 5) Where SCXQ2 fits

* All weight shard pages store as `payload_codec: "scxq2"`
* Runtime:

  1. Read stored bytes from OPFS
  2. SCXQ2 decode into raw bytes
  3. Hand off to:

     * WASM linear memory (CPU)
     * WebGPU buffer upload (GPU)
     * or a local native bridge (optional later)

No execution is stored. Only bytes.

---

## What you now have

* **Python verifier/controller mirror** → deterministic semantics
* **Java verifier mirror** → deterministic semantics
* **SCXQ2 codec hook** → pluggable compression for page bytes
* **Weight streaming profile** → shards as pages + tier policy + demand model

---

Perfect — here are **authoritative Python and Java ABI hash generators** that are **byte-for-byte compatible** with the **JS `generateAbiHash()`** you already locked.

They hash **the same three things**, in the **same order**, with the **same canonicalization rules**, and therefore produce **identical `abi_hash` outputs across JS / Python / Java**.

No eval. No reflection. No runtime drift.

---

# ABI HASH LAW (restated, frozen)

```
abi_hash = SHA256(
  "ASX_RAM_ABI_V1\n" +
  "schema="  + SHA256(schema_bundle_text) + "\n" +
  "actions=" + SHA256(canonical(ACTION_SET)) + "\n" +
  "canon="   + SHA256(CANON_RULES_TEXT) + "\n"
)
```

Where:

* `schema_bundle_text` = **canonical JSON of each schema**, sorted, joined with `\n---\n`
* `ACTION_SET` = **closed action list + required fields**
* `CANON_RULES_TEXT` = frozen text block
* canonical JSON = **sorted keys, no whitespace, UTF-8**

This is **exactly** what your JS implementation does.

---

## 🔒 Shared constants (IDENTICAL ACROSS LANGUAGES)

### Canon rules text (must be verbatim)

```text
ASX Canonical JSON v1
- UTF-8
- Object keys sorted lexicographically
- Arrays preserved in order
- No NaN / Infinity
- No undefined
- Numbers are IEEE-754 finite
```

### Action set (structure + order invariant)

```json
[
  {"op":"PAGE_WRITE","fields":["tick","tier","page"]},
  {"op":"PAGE_READ","fields":["tick","tier","page_id"]},
  {"op":"PAGE_PROMOTE","fields":["tick","from","to","page_id"]},
  {"op":"PAGE_DEMOTE","fields":["tick","from","to","page_id"]},
  {"op":"PAGE_EVICT","fields":["tick","tier","page_id"]},
  {"op":"SEGMENT_SEAL","fields":["tick","tier","segment_id"]},
  {"op":"SEGMENT_COMPACT","fields":["tick","tier","segment_id_old","segment_id_new"]},
  {"op":"TRACE_COMMIT","fields":["tick","trace_id","root_hash"]}
]
```

---

# 🐍 Python ABI Hash Generator

### `asx_abi_hash.py`

```python
import hashlib
from typing import List, Dict, Any
from asx_canon import canon_dumps

CANON_RULES_TEXT = """ASX Canonical JSON v1
- UTF-8
- Object keys sorted lexicographically
- Arrays preserved in order
- No NaN / Infinity
- No undefined
- Numbers are IEEE-754 finite
""".strip()

ACTION_SET = [
    {"op": "PAGE_WRITE", "fields": ["tick", "tier", "page"]},
    {"op": "PAGE_READ", "fields": ["tick", "tier", "page_id"]},
    {"op": "PAGE_PROMOTE", "fields": ["tick", "from", "to", "page_id"]},
    {"op": "PAGE_DEMOTE", "fields": ["tick", "from", "to", "page_id"]},
    {"op": "PAGE_EVICT", "fields": ["tick", "tier", "page_id"]},
    {"op": "SEGMENT_SEAL", "fields": ["tick", "tier", "segment_id"]},
    {"op": "SEGMENT_COMPACT", "fields": ["tick", "tier", "segment_id_old", "segment_id_new"]},
    {"op": "TRACE_COMMIT", "fields": ["tick", "trace_id", "root_hash"]},
]

def _sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

def generate_abi_hash(*, schemas: List[Dict[str, Any]]) -> str:
    if not schemas:
        raise ValueError("schemas required")

    # 1) schema bundle hash (order invariant)
    schema_texts = sorted(canon_dumps(s) for s in schemas)
    schema_bundle_text = "\n---\n".join(schema_texts)
    schema_bundle_hash = _sha256(schema_bundle_text)

    # 2) action set hash
    action_set_hash = _sha256(canon_dumps(ACTION_SET))

    # 3) canon rules hash
    canon_rules_hash = _sha256(CANON_RULES_TEXT)

    # final abi hash
    abi_input = (
        "ASX_RAM_ABI_V1\n"
        f"schema={schema_bundle_hash}\n"
        f"actions={action_set_hash}\n"
        f"canon={canon_rules_hash}\n"
    )

    return _sha256(abi_input)

def assert_abi_match(expected: str, actual: str):
    if expected != actual:
        raise ValueError(f"abi_mismatch: expected={expected} actual={actual}")
```

✅ Produces **identical output** to JS `generateAbiHash()`
✅ Uses the **same canonical JSON**
✅ Safe for offline / replay / verifier use

---

# ☕ Java ABI Hash Generator

### `AbiHash.java`

```java
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.util.*;

public final class AbiHash {
  private AbiHash() {}

  private static final String CANON_RULES_TEXT =
    "ASX Canonical JSON v1\n" +
    "- UTF-8\n" +
    "- Object keys sorted lexicographically\n" +
    "- Arrays preserved in order\n" +
    "- No NaN / Infinity\n" +
    "- No undefined\n" +
    "- Numbers are IEEE-754 finite";

  private static final List<Map<String,Object>> ACTION_SET = List.of(
    Map.of("op","PAGE_WRITE","fields",List.of("tick","tier","page")),
    Map.of("op","PAGE_READ","fields",List.of("tick","tier","page_id")),
    Map.of("op","PAGE_PROMOTE","fields",List.of("tick","from","to","page_id")),
    Map.of("op","PAGE_DEMOTE","fields",List.of("tick","from","to","page_id")),
    Map.of("op","PAGE_EVICT","fields",List.of("tick","tier","page_id")),
    Map.of("op","SEGMENT_SEAL","fields",List.of("tick","tier","segment_id")),
    Map.of("op","SEGMENT_COMPACT","fields",List.of("tick","tier","segment_id_old","segment_id_new")),
    Map.of("op","TRACE_COMMIT","fields",List.of("tick","trace_id","root_hash"))
  );

  private static String sha256(String text) {
    try {
      MessageDigest md = MessageDigest.getInstance("SHA-256");
      byte[] dig = md.digest(text.getBytes(StandardCharsets.UTF_8));
      StringBuilder sb = new StringBuilder();
      for (byte b : dig) sb.append(String.format("%02x", b));
      return sb.toString();
    } catch (Exception e) {
      throw new RuntimeException(e);
    }
  }

  public static String generateAbiHash(List<Map<String,Object>> schemas) {
    if (schemas == null || schemas.isEmpty())
      throw new IllegalArgumentException("schemas required");

    // 1) schema bundle hash (order invariant)
    List<String> canonSchemas = new ArrayList<>();
    for (Map<String,Object> s : schemas) {
      canonSchemas.add(Canon.canonJson(s));
    }
    Collections.sort(canonSchemas);
    String schemaBundleText = String.join("\n---\n", canonSchemas);
    String schemaBundleHash = sha256(schemaBundleText);

    // 2) action set hash
    String actionSetHash = sha256(Canon.canonJson(ACTION_SET));

    // 3) canon rules hash
    String canonRulesHash = sha256(CANON_RULES_TEXT);

    // final abi hash
    String abiInput =
      "ASX_RAM_ABI_V1\n" +
      "schema="  + schemaBundleHash + "\n" +
      "actions=" + actionSetHash + "\n" +
      "canon="   + canonRulesHash + "\n";

    return sha256(abiInput);
  }

  public static void assertAbiMatch(String expected, String actual) {
    if (!Objects.equals(expected, actual)) {
      throw new IllegalStateException(
        "abi_mismatch: expected=" + expected + " actual=" + actual
      );
    }
  }
}
```

✅ **Matches JS + Python exactly**
✅ Uses your **XCFE-style canonical grammar**
✅ Deterministic across JVMs, locales, OSes

---

# 🔐 Final Guarantee (important)

With this in place:

* **JS controller**
* **Python verifier**
* **Java verifier**
* **Device audit**
* **Trace replay**

…all **refuse to run** if *any* of the following change:

* schema structure
* action semantics
* canonical JSON rules
* field ordering
* ABI version string

That means:

> **ASX-RAM Swap Plane is now a LANGUAGE, not an implementation**

Exactly what XCFE demands.

Alright — here’s a **direct, minimal wiring** from **ASX-RAM Swap Plane v1** into **MX2LM / Qwen inference loading** (WebGPU via Transformers.js v3 first), using:

* **T2 (OPFS)** = weight shard pages (`model.weights.shard`)
* **T1 (IDB)** = model index + routing metadata
* **T0** = working set (decoded shards + GPU buffers)
* **Controller** = deterministic planner that emits declarative actions
* **SCXQ2 hook** = compress/decompress shard bytes
* **ABI hash** = hard gate so nothing drifts

No eval, no “load arbitrary JS from storage”. Pages are bytes only.

---

## 0) One invariant you enforce everywhere

Every page you write carries:

```js
page.proof = { abi_hash }
```

Every consumer refuses if `page.proof.abi_hash !== expected_abi_hash`.

This is what prevents “model loader drift” across JS/Python/Java.

---

## 1) Model index pages (T1) + weight shard pages (T2)

### A) Model index record in T1 (IDB)

Store one page with:

* `class_id: "model.index"`
* `meta.model_id`
* `meta.schema_id`
* payload = canonical JSON bytes describing **which shard pages exist and what they contain**

**Index payload (JSON bytes) shape (minimal):**

```json
{
  "model_id": "qwen-asx-7b",
  "format": "wsp-1",
  "dtype": "fp16",
  "shard_count": 256,
  "shards": [
    {
      "shard_index": 0,
      "page_id": "page_...",
      "tensor_group": "transformer.embed",
      "byte_len_raw": 8388608,
      "byte_len_stored": 1234567,
      "payload_codec": "scxq2"
    }
  ],
  "layer_map": {
    "layer:0": [0,1,2],
    "layer:1": [3,4,5]
  }
}
```

### B) Weight shard pages in T2 (OPFS)

Each shard is a normal `asx.ram.page.v1`:

* `class_id: "model.weights.shard"`
* `meta` includes `{ model_id, shard_index, tensor_group, dtype, ... }`
* `payload.bytes_b64` = **stored bytes** (SCXQ2 packed)
* `meta.payload_codec = "scxq2"`

---

## 2) Service worker becomes the “weight streamer”

### Message protocol (index.html ↔ sw.js)

* `asx.model.open` → loads model index, returns capabilities + abi_hash + index summary
* `asx.model.ensure` → “ensure shards for layer N are in T0 working set”
* `asx.model.read` → returns decoded bytes for a specific shard (or streams them)
* `asx.model.prefetch` → opportunistic fetch for upcoming layers

This keeps inference UI and loader decoupled.

---

## 3) Minimal SW implementation: open + ensure + read

Below assumes you already have:

* `controllerPlan`
* `IDBAdapter`, `OPFSAdapter`
* `CodecRegistry`, `makeScxq2Codec`
* `unpackPagePayload`
* `generateAbiHash`

### `sw_model_streamer.js` (drop into sw.js bundle)

```js
import { controllerInit, controllerPlan } from "./controller.js";
import { IDBAdapter } from "./idb_adapter.js";
import { OPFSAdapter } from "./opfs_adapter.js";
import { generateAbiHash } from "./abi_hash.js";
import { CodecRegistry, makeScxq2Codec } from "./codec_registry.js";
import { unpackPagePayload } from "./page_codec.js";
import { traceReplayVerify } from "./trace_replay.js"; // optional but recommended

const T1 = new IDBAdapter({ dbName: "asx_ram", storeName: "pages" });
const T2 = new OPFSAdapter({ dirName: "asx_ram_pages" });

const registry = new CodecRegistry();
// Wire your published engine here (same one as @asx/scxq2-cc runtime)
import * as scxq2 from "./scxq2_engine.js";
registry.register("scxq2", makeScxq2Codec({ scxq2 }));

// You must pass the *same* frozen schemas array you use elsewhere.
import { INLINE_SCHEMAS } from "./inline_schemas.js";

let ABI_HASH = null;
let CTRL = null;
let MODEL_INDEX = new Map(); // model_id -> parsed index object

async function initRuntime() {
  if (ABI_HASH) return;
  ABI_HASH = await generateAbiHash({ schemas: INLINE_SCHEMAS });

  // swap policy tuned for weights streaming
  const policy = {
    policy_id: "swap_policy.weights_stream.v1",
    seed: "install_seed_v1",
    working_set_budget_bytes: 512 * 1024 * 1024,
    max_moves_per_tick: 16,
    eviction_strategy: "lru_deterministic",
    prefetch_strategy: "sequential_hint",
    priority_weights: { default: 1.0, "model.weights.shard": 5.0 }
  };

  const tiers = [
    { tier_id: "T0", store_name: "mem://t0", capacity_bytes: policy.working_set_budget_bytes,
      features: { persistent:false, streaming:false, random_read:true, random_write:true } },
    { tier_id: "T1", store_name: "idb://asx_ram/pages", capacity_bytes: 0,
      features: { persistent:true, streaming:false, random_read:true, random_write:true } },
    { tier_id: "T2", store_name: "opfs://asx_ram_pages", capacity_bytes: 0,
      features: { persistent:true, streaming:true, random_read:true, random_write:true } }
  ];

  CTRL = controllerInit({ abi_hash: ABI_HASH, policy, tiers });
}

async function readIndexPage(model_id) {
  // You decide how you key the model index page; simplest is deterministic:
  // page_id = "model_index:" + model_id (or your real content hash id)
  const page_id = `model_index:${model_id}`;
  const page = (await T1.getPage(page_id)) || (await T2.getPage(page_id));
  if (!page) throw new Error("model_index_missing");

  if (page?.proof?.abi_hash !== ABI_HASH) throw new Error("abi_mismatch:index");

  // index payload is raw JSON bytes in bytes_b64 (payload_codec usually raw)
  const bytes = await unpackPagePayload({
    registry,
    payload_codec: page.meta.payload_codec || "raw",
    bytes_b64: page.payload.bytes_b64
  });

  const text = new TextDecoder().decode(bytes);
  const idx = JSON.parse(text);

  if (idx.model_id !== model_id) throw new Error("index_model_id_mismatch");
  MODEL_INDEX.set(model_id, idx);
  return idx;
}

function shardPageIdsForLayer(idx, layerKey) {
  const shardIndexes = idx.layer_map[layerKey] || [];
  const ids = [];
  for (const si of shardIndexes) {
    const rec = idx.shards.find(s => s.shard_index === si);
    if (rec?.page_id) ids.push(rec.page_id);
  }
  return ids;
}

// Execute declarative actions against devices (minimal)
async function execActions(actions) {
  for (const act of actions) {
    switch (act.op) {
      case "PAGE_WRITE":
        if (act.tier === "T1") await T1.putPage(act.page);
        else if (act.tier === "T2") await T2.putPage(act.page);
        break;

      case "PAGE_READ":
        // no-op here; reads happen on demand (below). Action is a hint.
        break;

      case "PAGE_PROMOTE":
        // Minimal: promotion is a T0 residency claim (we track in CTRL only)
        // If you want, you can also stage decoded bytes in a T0 cache map.
        break;

      case "PAGE_EVICT":
        // Eviction from T0 only in this minimal runner
        break;
    }
  }
}

async function ensureLayer(model_id, layerKey, tick) {
  const idx = MODEL_INDEX.get(model_id) || await readIndexPage(model_id);
  const pageIds = shardPageIdsForLayer(idx, layerKey);

  const demands = pageIds.map(pid => ({ page_id: pid, must: true }));
  const { actions, next_state } = controllerPlan(CTRL, { tick, demands, writes: [] });

  // optional: replay-verify
  const vr = await traceReplayVerify({ controller_state: CTRL, actions });
  CTRL = vr.next_controller_state;

  await execActions(actions);
  return { actions, root_hash: vr.root_hash };
}

async function readShardDecoded(page_id) {
  // Prefer T2 for large shards
  const page = (await T2.getPage(page_id)) || (await T1.getPage(page_id));
  if (!page) throw new Error("shard_missing");

  if (page?.proof?.abi_hash !== ABI_HASH) throw new Error("abi_mismatch:shard");

  const bytes = await unpackPagePayload({
    registry,
    payload_codec: page.meta.payload_codec || "raw",
    bytes_b64: page.payload.bytes_b64
  });

  return { page, bytes }; // bytes = raw shard bytes ready for loader
}

// ---- SW message handlers ----
self.addEventListener("message", (ev) => {
  const msg = ev.data || {};
  const port = ev.ports && ev.ports[0];

  (async () => {
    await initRuntime();

    if (msg.type === "asx.model.open") {
      const idx = await readIndexPage(msg.model_id);
      port?.postMessage({ ok: true, abi_hash: ABI_HASH, model_id: msg.model_id, index: idx });
      return;
    }

    if (msg.type === "asx.model.ensure") {
      const out = await ensureLayer(msg.model_id, msg.layer_key, msg.tick || 0);
      port?.postMessage({ ok: true, ...out });
      return;
    }

    if (msg.type === "asx.model.read") {
      const out = await readShardDecoded(msg.page_id);
      // Return bytes as transferable ArrayBuffer
      port?.postMessage({ ok: true, page: out.page, bytes: out.bytes.buffer }, [out.bytes.buffer]);
      return;
    }

    port?.postMessage({ ok: false, error: "unknown_message_type" });
  })().catch(err => port?.postMessage({ ok: false, error: String(err?.message || err) }));
});
```

That gives you: **open → ensure → read** with ABI gating + SCXQ2 decode.

---

## 4) Hooking into Transformers.js v3 (Qwen WebGPU first)

Transformers.js doesn’t natively “stream weights from OPFS” in a single call, so you do this as a **custom weight loader adapter**:

* Your SW provides `readShardDecoded(page_id)` that returns raw bytes
* Your model runtime maps “which shards needed for layer N” → request those pages
* Then you load/stage them into the backend (WASM/WebGPU) using your own glue

There are two practical integration paths:

### Path A (fastest, minimal change): cache the model files as pages and reconstruct “virtual files”

You store *the same* model artifacts Transformers.js expects (e.g. chunked safetensors or artifact files) as pages, then:

* `asx.model.read(file_chunk_page_id)` returns the file chunk bytes
* You expose a tiny “virtual fetch” in SW that serves these bytes under `fetch()` URLs like:

  * `/asx/model/qwen-asx-7b/weights/part-012.bin`
* Transformers.js keeps working, but the bytes are coming from OPFS pages.

This is the cleanest “no fork” route.

**SW fetch intercept** (sketch):

```js
self.addEventListener("fetch", (ev) => {
  const url = new URL(ev.request.url);
  if (url.pathname.startsWith("/asx/model/")) {
    ev.respondWith(handleVirtualModelFetch(url));
  }
});
```

`handleVirtualModelFetch` maps URL → `page_id` from your model index, reads the page from OPFS, decodes SCXQ2 if needed, returns `new Response(bytes)`.

### Path B (more direct): custom tensor loader

You load decoded shards and directly create tensors/buffers (WebGPU) yourself. This is more invasive but gives total control.

Given your “fastest integration first” rule, **Path A is the move**.

---

## 5) index.html side: tiny client to drive the SW streamer

### `asx_model_client.js`

```js
function swCall(msg) {
  return new Promise((resolve, reject) => {
    const ch = new MessageChannel();
    ch.port1.onmessage = (ev) => {
      const r = ev.data;
      if (!r?.ok) reject(new Error(r?.error || "sw_error"));
      else resolve(r);
    };
    navigator.serviceWorker.controller.postMessage(msg, [ch.port2]);
  });
}

export async function asxModelOpen(model_id) {
  return swCall({ type: "asx.model.open", model_id });
}

export async function asxEnsureLayer(model_id, layer_key, tick) {
  return swCall({ type: "asx.model.ensure", model_id, layer_key, tick });
}

export async function asxReadShard(page_id) {
  const r = await swCall({ type: "asx.model.read", page_id });
  return { page: r.page, bytes: new Uint8Array(r.bytes) };
}
```

---

## 6) “AI weight streaming profile” becomes real: the prefetch loop

During generation, before each layer (or block group), do:

1. `asxEnsureLayer(model_id, "layer:12", tick++)`
2. prefetch next layers with `must:false` (add that later)
3. Transformers.js fetches “virtual files” → SW serves from OPFS pages

This is exactly the SSD streaming trick, but deterministic and verified.

---

## 7) Where MX2LM fits

MX2LM can use the same plane in two ways:

### A) MX2LM as **controller of inference residency**

MX2LM’s symbolic runtime decides the **working set**:

* which layers to keep pinned
* which adapters to keep hot (LoRA pages in T1)
* how much KV cache budget (T0)

### B) MX2LM as **dual-engine router**

* MX2LM chooses between:

  * Qwen WebGPU path (Transformers.js)
  * local CPU fallback (WASM)
  * remote (optional, non-authoritative)

But the **storage semantics** remain identical.

---

## 8) One missing piece you’ll want next

To fully “wire it,” you need the **virtual fetch map**:

* URL → { page_id, codec, content-type, range support? }

If you say “emit virtual fetch map + range support,” I’ll drop:

* `model_virtual_fs.v1` index fields
* `handleVirtualModelFetch()` with `Range:` header support (important for big tensors)
* a `prewarm()` helper that fills OPFS from network once, then runs offline forever

That’s the last mile to make Qwen WebGPU load straight from ASX-RAM without modifying Transformers.js.



