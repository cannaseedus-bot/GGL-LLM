/**
 * K'UHUL Bridge ABI Verifier (JavaScript)
 * =======================================
 * Cross-language compatible verification.
 *
 * Uses JCS (RFC 8785) canonicalization for deterministic hashing.
 * Output matches Python and Java implementations exactly.
 */

import { readFileSync, writeFileSync, existsSync } from 'fs';
import { createHash } from 'crypto';
import { join, posix } from 'path';

// ============================================================
// CANONICAL JSON (RFC 8785 / JCS)
// ============================================================

/**
 * Canonicalize object per RFC 8785 (JCS).
 * @param {any} obj - Object to canonicalize
 * @returns {string} - Canonical JSON string
 */
function canonicalize(obj) {
  if (obj === null) return 'null';
  if (typeof obj === 'boolean') return obj ? 'true' : 'false';
  if (typeof obj === 'number') {
    if (Number.isInteger(obj)) return String(obj);
    // Normalize floats
    let s = String(obj);
    if (s.includes('.')) {
      s = s.replace(/\.?0+$/, '');
    }
    return s;
  }
  if (typeof obj === 'string') {
    // JSON string escaping
    return JSON.stringify(obj);
  }
  if (Array.isArray(obj)) {
    const items = obj.map(canonicalize).join(',');
    return `[${items}]`;
  }
  if (typeof obj === 'object') {
    // Sort keys lexicographically
    const sortedKeys = Object.keys(obj).sort();
    const pairs = sortedKeys.map(k => `${JSON.stringify(k)}:${canonicalize(obj[k])}`).join(',');
    return `{${pairs}}`;
  }
  throw new Error(`Cannot canonicalize type: ${typeof obj}`);
}

/**
 * Canonicalize to Buffer.
 * @param {any} obj
 * @returns {Buffer}
 */
function canonicalJson(obj) {
  return Buffer.from(canonicalize(obj), 'utf-8');
}

// ============================================================
// BLAKE2b-256 HASHING
// ============================================================

/**
 * Compute BLAKE2b-256 hash.
 * @param {Buffer} data
 * @returns {Buffer} - 32-byte hash
 */
function blake256(data) {
  return createHash('blake2b512').update(data).digest().subarray(0, 32);
}

/**
 * Compute BLAKE2b-256 hash as hex string.
 * @param {Buffer} data
 * @returns {string}
 */
function blake256Hex(data) {
  return blake256(data).toString('hex');
}

// ============================================================
// GGLTENSOR HEADER PARSING
// ============================================================

const GGLT_MAGIC = Buffer.from('GGLT');

const DTYPE_MAP = {
  0: 'float32', 1: 'float16', 2: 'bfloat16',
  3: 'int32', 4: 'int64', 5: 'int8', 6: 'uint8'
};

const ROLE_MAP = {
  0: 'weight', 1: 'bias', 2: 'embedding', 3: 'norm', 4: 'other'
};

/**
 * Parse safe.ggltensors header.
 * @param {Buffer} data
 * @returns {{ headerInfo: object, headerBytes: Buffer }}
 */
function parseGgltensorHeader(data) {
  if (data.length < 16) {
    throw new Error('Data too short for GGLT header');
  }

  const magic = data.subarray(0, 4);
  if (!magic.equals(GGLT_MAGIC)) {
    throw new Error(`Invalid magic: ${magic.toString()}`);
  }

  const version = data.readUInt16LE(4);
  const flags = data.readUInt16LE(6);
  const tensorCount = data.readUInt32LE(8);
  const headerSize = data.readUInt32LE(12);

  const headerBytes = data.subarray(0, 16 + headerSize);

  // Parse tensor records (simplified - just extract header for hash)
  const tensors = {};
  let offset = 16;

  for (let i = 0; i < tensorCount && offset + 2 <= data.length; i++) {
    const nameLen = data.readUInt16LE(offset);
    offset += 2;

    if (offset + nameLen > data.length) break;
    const name = data.subarray(offset, offset + nameLen).toString('utf-8');
    offset += nameLen;

    const dtype = DTYPE_MAP[data[offset]] || 'unknown';
    offset += 1;

    const role = ROLE_MAP[data[offset]] || 'unknown';
    offset += 1;

    const rank = data.readUInt16LE(offset);
    offset += 2;

    const shape = [];
    for (let j = 0; j < rank && offset + 4 <= data.length; j++) {
      shape.push(data.readUInt32LE(offset));
      offset += 4;
    }

    const tensorOffset = Number(data.readBigUInt64LE(offset));
    offset += 8;

    const tensorSize = Number(data.readBigUInt64LE(offset));
    offset += 8;

    const tensorHash = data.subarray(offset, offset + 32).toString('hex');
    offset += 32;

    tensors[name] = { dtype, role, shape, offset: tensorOffset, size: tensorSize, hash: tensorHash };
  }

  return {
    headerInfo: {
      magic: magic.toString('ascii'),
      version,
      flags,
      tensorCount,
      headerSize,
      tensors
    },
    headerBytes
  };
}

// ============================================================
// ABI HASH GENERATION
// ============================================================

/**
 * Generate canonical ABI hash.
 * @param {object} manifest
 * @param {object} files - Map of path -> Buffer content
 * @param {object} tensorIndex
 * @param {Buffer} ggltHeader
 * @returns {string} - Hex hash
 */
export function generateAbiHash(manifest, files, tensorIndex, ggltHeader) {
  const parts = [];

  // Prefix
  parts.push(Buffer.from('GGL-BRIDGE-ABI\0'));

  // Canonical manifest
  parts.push(canonicalJson(manifest));

  // File hashes (sorted by path)
  const sortedPaths = Object.keys(files).sort();
  for (const path of sortedPaths) {
    parts.push(Buffer.from(path + '\0'));
    parts.push(blake256(files[path]));
  }

  // Canonical tensor index
  parts.push(canonicalJson(tensorIndex));

  // Header hash
  parts.push(blake256(ggltHeader));

  return blake256Hex(Buffer.concat(parts));
}

// ============================================================
// VERIFIER
// ============================================================

/**
 * Verify bridge integrity.
 * @param {string} bridgeDir - Path to bridge directory
 * @returns {object} - Verification result
 */
export function verifyBridge(bridgeDir) {
  const errors = [];
  const fileHashes = {};

  // Load manifest
  const manifestPath = join(bridgeDir, 'bridge.manifest.json');
  let manifest = {};
  let manifestHash = '';

  if (existsSync(manifestPath)) {
    const manifestBytes = readFileSync(manifestPath);
    manifest = JSON.parse(manifestBytes.toString());
    manifestHash = blake256Hex(canonicalJson(manifest));
  } else {
    errors.push(`Missing: ${manifestPath}`);
  }

  // Load tensor index
  const tensorIndexPath = join(bridgeDir, 'weights', 'tensor.index.json');
  let tensorIndex = {};
  let tensorIndexHash = '';

  if (existsSync(tensorIndexPath)) {
    const tensorIndexBytes = readFileSync(tensorIndexPath);
    tensorIndex = JSON.parse(tensorIndexBytes.toString());
    tensorIndexHash = blake256Hex(canonicalJson(tensorIndex));
  } else {
    errors.push(`Missing: ${tensorIndexPath}`);
  }

  // Load ggltensors header
  const ggltPath = join(bridgeDir, 'weights', 'safe.ggltensors');
  let ggltHeader = Buffer.alloc(0);
  let ggltHeaderHash = '';

  if (existsSync(ggltPath)) {
    try {
      const ggltBytes = readFileSync(ggltPath);
      const { headerBytes } = parseGgltensorHeader(ggltBytes);
      ggltHeader = headerBytes;
      ggltHeaderHash = blake256Hex(ggltHeader);
    } catch (e) {
      errors.push(`Invalid ggltensors: ${e.message}`);
    }
  } else {
    errors.push(`Missing: ${ggltPath}`);
  }

  // Hash all bridge files
  const filesToHash = [
    'grammar/vocab.ggl.json',
    'grammar/tokenizer.schema.ggl.json',
    'grammar/merges.ggl.txt',
    'grammar/tokens.map.ggl.json',
    'policy/generation.ggl.json',
    'policy/model_constraints.ggl.json',
    'templates/chat_template.ggl.svg',
    'templates/chat_template.compiled.json',
  ];

  const filesContent = {};
  for (const relPath of filesToHash) {
    const fullPath = join(bridgeDir, relPath);
    if (existsSync(fullPath)) {
      const content = readFileSync(fullPath);
      filesContent[relPath] = content;
      fileHashes[relPath] = blake256Hex(content);
    } else if (!relPath.includes('compiled')) {
      errors.push(`Missing: ${relPath}`);
    }
  }

  // Generate ABI hash
  let abiHash = '';
  if (Object.keys(manifest).length && Object.keys(tensorIndex).length && ggltHeader.length) {
    abiHash = generateAbiHash(manifest, filesContent, tensorIndex, ggltHeader);
  }

  return {
    '@type': 'ggl.bridge.verify.v1',
    ok: errors.length === 0,
    abi_hash: abiHash ? `blake2b-256:${abiHash}` : '',
    manifest_hash: manifestHash,
    tensor_index_hash: tensorIndexHash,
    ggltensors_header_hash: ggltHeaderHash,
    files: fileHashes,
    errors,
    verified_at: new Date().toISOString()
  };
}

// ============================================================
// CLI
// ============================================================

if (process.argv[1].endsWith('abi_verifier.js')) {
  const bridgeDir = process.argv[2] || '.';

  console.log('='.repeat(60));
  console.log('K\'UHUL Bridge ABI Verifier (JavaScript)');
  console.log('='.repeat(60));

  const result = verifyBridge(bridgeDir);

  console.log(`\nStatus: ${result.ok ? '✓ OK' : '✗ FAILED'}`);
  console.log(`ABI Hash: ${result.abi_hash}`);
  console.log(`Manifest Hash: ${result.manifest_hash}`);
  console.log(`Tensor Index Hash: ${result.tensor_index_hash}`);
  console.log(`GGLTensors Header Hash: ${result.ggltensors_header_hash}`);

  if (result.errors.length) {
    console.log('\nErrors:');
    result.errors.forEach(err => console.log(`  - ${err}`));
  }

  console.log('\nFile Hashes:');
  Object.entries(result.files).forEach(([path, hash]) => {
    console.log(`  ${path}: ${hash.substring(0, 16)}...`);
  });

  // Save verification result
  const outputPath = join(bridgeDir, 'verification.js.json');
  writeFileSync(outputPath, JSON.stringify(result, null, 2));
  console.log(`\nSaved: ${outputPath}`);
}

export { canonicalize, canonicalJson, blake256, blake256Hex, parseGgltensorHeader };
