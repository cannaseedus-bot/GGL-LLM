"""
K'UHUL Bridge ABI Verifier
==========================
Canonical ABI hashing and cross-language verification.

Uses JCS (RFC 8785) canonicalization:
- UTF-8
- No insignificant whitespace
- Lexicographic key ordering
- Arrays preserved in order
- Numbers normalized
- No comments, no trailing zeros
"""

import json
import hashlib
import struct
from pathlib import Path
from typing import Dict, List, Any, Tuple, Optional
from datetime import datetime


# ============================================================
# CANONICAL JSON (RFC 8785 / JCS)
# ============================================================

def canonical_json(obj: Any) -> bytes:
    """
    Encode object as canonical JSON per RFC 8785.

    Rules:
    - UTF-8 encoding
    - No whitespace between tokens
    - Object keys sorted lexicographically
    - Arrays preserve order
    - Numbers: no leading zeros, no trailing zeros after decimal
    - No comments
    """
    def _encode(o):
        if o is None:
            return 'null'
        elif isinstance(o, bool):
            return 'true' if o else 'false'
        elif isinstance(o, int):
            return str(o)
        elif isinstance(o, float):
            # Normalize: remove trailing zeros, handle special cases
            if o == int(o):
                return str(int(o))
            s = repr(o)
            # Remove trailing zeros after decimal
            if '.' in s:
                s = s.rstrip('0').rstrip('.')
            return s
        elif isinstance(o, str):
            # JSON string escaping
            escaped = o.replace('\\', '\\\\').replace('"', '\\"')
            escaped = escaped.replace('\n', '\\n').replace('\r', '\\r')
            escaped = escaped.replace('\t', '\\t')
            return f'"{escaped}"'
        elif isinstance(o, list):
            items = ','.join(_encode(item) for item in o)
            return f'[{items}]'
        elif isinstance(o, dict):
            # Sort keys lexicographically
            sorted_keys = sorted(o.keys())
            pairs = ','.join(f'{_encode(k)}:{_encode(o[k])}' for k in sorted_keys)
            return f'{{{pairs}}}'
        else:
            raise TypeError(f"Cannot canonicalize type: {type(o)}")

    return _encode(obj).encode('utf-8')


# ============================================================
# BLAKE2b-256 HASHING
# ============================================================

def blake256(data: bytes) -> bytes:
    """Compute BLAKE2b-256 hash."""
    return hashlib.blake2b(data, digest_size=32).digest()


def blake256_hex(data: bytes) -> str:
    """Compute BLAKE2b-256 hash as hex string."""
    return blake256(data).hex()


# ============================================================
# GGLTENSOR HEADER PARSING
# ============================================================

GGLT_MAGIC = b'GGLT'
GGLT_VERSION = 1

# Dtype enum
DTYPE_MAP = {
    0: 'float32',
    1: 'float16',
    2: 'bfloat16',
    3: 'int32',
    4: 'int64',
    5: 'int8',
    6: 'uint8',
}

# Role enum
ROLE_MAP = {
    0: 'weight',
    1: 'bias',
    2: 'embedding',
    3: 'norm',
    4: 'other',
}


def parse_ggltensor_header(data: bytes) -> Tuple[Dict[str, Any], bytes]:
    """
    Parse safe.ggltensors header and return (header_info, header_bytes).

    Header layout:
    Offset  Size  Field
    0       4     Magic = "GGLT"
    4       2     Version = 0x0001
    6       2     Flags (must be 0)
    8       4     Tensor count (u32 LE)
    12      4     Header size (bytes, u32 LE)
    16      …     Tensor records (ordered)
    """
    if len(data) < 16:
        raise ValueError("Data too short for GGLT header")

    # Parse fixed header
    magic = data[0:4]
    if magic != GGLT_MAGIC:
        raise ValueError(f"Invalid magic: {magic}")

    version = struct.unpack('<H', data[4:6])[0]
    flags = struct.unpack('<H', data[6:8])[0]
    tensor_count = struct.unpack('<I', data[8:12])[0]
    header_size = struct.unpack('<I', data[12:16])[0]

    # Extract header bytes (for hashing)
    header_bytes = data[0:16 + header_size]

    # Parse tensor records
    tensors = {}
    offset = 16

    for _ in range(tensor_count):
        if offset + 2 > len(data):
            break

        name_len = struct.unpack('<H', data[offset:offset+2])[0]
        offset += 2

        name = data[offset:offset+name_len].decode('utf-8')
        offset += name_len

        dtype = DTYPE_MAP.get(data[offset], 'unknown')
        offset += 1

        role = ROLE_MAP.get(data[offset], 'unknown')
        offset += 1

        rank = struct.unpack('<H', data[offset:offset+2])[0]
        offset += 2

        shape = []
        for _ in range(rank):
            dim = struct.unpack('<I', data[offset:offset+4])[0]
            shape.append(dim)
            offset += 4

        tensor_offset = struct.unpack('<Q', data[offset:offset+8])[0]
        offset += 8

        tensor_size = struct.unpack('<Q', data[offset:offset+8])[0]
        offset += 8

        tensor_hash = data[offset:offset+32].hex()
        offset += 32

        tensors[name] = {
            'dtype': dtype,
            'role': role,
            'shape': shape,
            'offset': tensor_offset,
            'size': tensor_size,
            'hash': tensor_hash,
        }

    header_info = {
        'magic': magic.decode('ascii'),
        'version': version,
        'flags': flags,
        'tensor_count': tensor_count,
        'header_size': header_size,
        'tensors': tensors,
    }

    return header_info, header_bytes


# ============================================================
# ABI HASH GENERATION
# ============================================================

def generate_abi_hash(
    manifest: Dict[str, Any],
    files: Dict[str, bytes],
    tensor_index: Dict[str, Any],
    gglt_header: bytes
) -> str:
    """
    Generate canonical ABI hash.

    abi_hash = BLAKE2b-256(
      "GGL-BRIDGE-ABI\0" +
      canon(manifest.json) +
      for file in sorted(files):
        file_path + "\0" + file_hash +
      canon(tensor.index.json) +
      ggltensors_header_hash
    )
    """
    parts = []

    # Prefix
    parts.append(b"GGL-BRIDGE-ABI\0")

    # Canonical manifest
    parts.append(canonical_json(manifest))

    # File hashes (sorted by path)
    for path in sorted(files.keys()):
        parts.append(path.encode('utf-8') + b"\0")
        parts.append(blake256(files[path]))

    # Canonical tensor index
    parts.append(canonical_json(tensor_index))

    # Header hash
    parts.append(blake256(gglt_header))

    return blake256_hex(b"".join(parts))


# ============================================================
# VERIFIER
# ============================================================

class BridgeVerifier:
    """
    Cross-language compatible bridge verifier.

    Outputs identical verification result across JS/Python/Java.
    """

    def __init__(self, bridge_dir: Path):
        self.bridge_dir = Path(bridge_dir)
        self.errors: List[str] = []

    def verify(self) -> Dict[str, Any]:
        """
        Verify bridge integrity and return verification result.

        Returns object matching:
        {
          "@type": "ggl.bridge.verify.v1",
          "ok": true/false,
          "abi_hash": "blake2b-256:…",
          "manifest_hash": "…",
          "tensor_index_hash": "…",
          "ggltensors_header_hash": "…",
          "files": { "path": "hash", ... },
          "errors": []
        }
        """
        self.errors = []
        file_hashes = {}

        # Load manifest
        manifest_path = self.bridge_dir / "bridge.manifest.json"
        if not manifest_path.exists():
            self.errors.append(f"Missing: {manifest_path}")
            manifest = {}
            manifest_hash = ""
        else:
            manifest_bytes = manifest_path.read_bytes()
            manifest = json.loads(manifest_bytes)
            manifest_hash = blake256_hex(canonical_json(manifest))

        # Load tensor index
        tensor_index_path = self.bridge_dir / "weights" / "tensor.index.json"
        if not tensor_index_path.exists():
            self.errors.append(f"Missing: {tensor_index_path}")
            tensor_index = {}
            tensor_index_hash = ""
        else:
            tensor_index_bytes = tensor_index_path.read_bytes()
            tensor_index = json.loads(tensor_index_bytes)
            tensor_index_hash = blake256_hex(canonical_json(tensor_index))

        # Load ggltensors header
        gglt_path = self.bridge_dir / "weights" / "safe.ggltensors"
        if not gglt_path.exists():
            self.errors.append(f"Missing: {gglt_path}")
            gglt_header = b""
            gglt_header_hash = ""
        else:
            gglt_bytes = gglt_path.read_bytes()
            try:
                _, gglt_header = parse_ggltensor_header(gglt_bytes)
                gglt_header_hash = blake256_hex(gglt_header)
            except Exception as e:
                self.errors.append(f"Invalid ggltensors: {e}")
                gglt_header = b""
                gglt_header_hash = ""

        # Hash all bridge files
        files_to_hash = [
            "grammar/vocab.ggl.json",
            "grammar/tokenizer.schema.ggl.json",
            "grammar/merges.ggl.txt",
            "grammar/tokens.map.ggl.json",
            "policy/generation.ggl.json",
            "policy/model_constraints.ggl.json",
            "templates/chat_template.ggl.svg",
            "templates/chat_template.compiled.json",
        ]

        files_content = {}
        for rel_path in files_to_hash:
            full_path = self.bridge_dir / rel_path
            if full_path.exists():
                content = full_path.read_bytes()
                files_content[rel_path] = content
                file_hashes[rel_path] = blake256_hex(content)
            else:
                # Optional files don't cause errors
                if "compiled" not in rel_path:
                    self.errors.append(f"Missing: {rel_path}")

        # Generate ABI hash
        if manifest and tensor_index and gglt_header:
            abi_hash = generate_abi_hash(
                manifest, files_content, tensor_index, gglt_header
            )
        else:
            abi_hash = ""

        return {
            "@type": "ggl.bridge.verify.v1",
            "ok": len(self.errors) == 0,
            "abi_hash": f"blake2b-256:{abi_hash}" if abi_hash else "",
            "manifest_hash": manifest_hash,
            "tensor_index_hash": tensor_index_hash,
            "ggltensors_header_hash": gglt_header_hash,
            "files": file_hashes,
            "errors": self.errors,
            "verified_at": datetime.utcnow().isoformat() + "Z",
        }

    def save_verification(self, output_path: Optional[Path] = None) -> Path:
        """Run verification and save result."""
        result = self.verify()

        if output_path is None:
            output_path = self.bridge_dir / "verification.json"

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)

        return output_path


# ============================================================
# CLI
# ============================================================

if __name__ == "__main__":
    import sys

    bridge_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")

    print("=" * 60)
    print("K'UHUL Bridge ABI Verifier")
    print("=" * 60)

    verifier = BridgeVerifier(bridge_dir)
    result = verifier.verify()

    print(f"\nStatus: {'✓ OK' if result['ok'] else '✗ FAILED'}")
    print(f"ABI Hash: {result['abi_hash']}")
    print(f"Manifest Hash: {result['manifest_hash']}")
    print(f"Tensor Index Hash: {result['tensor_index_hash']}")
    print(f"GGLTensors Header Hash: {result['ggltensors_header_hash']}")

    if result['errors']:
        print("\nErrors:")
        for err in result['errors']:
            print(f"  - {err}")

    print("\nFile Hashes:")
    for path, hash_val in result['files'].items():
        print(f"  {path}: {hash_val[:16]}...")

    # Save verification result
    output = verifier.save_verification()
    print(f"\nSaved: {output}")
