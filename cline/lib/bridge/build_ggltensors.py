#!/usr/bin/env python3
"""
K'UHUL Safe.GGLTensor Builder
=============================
Builds the GGL tensor format for SVG-3D inference bridge.

This script creates:
- safe.ggltensors (tensor weight references)
- vocab.ggl.json (GGL vocabulary mapping)
- tokenizer.schema.ggl (tokenizer schema)
- Other supporting bridge files

Usage:
    python build_ggltensors.py [--output-dir ./bridge]
"""

import json
import hashlib
import struct
import os
import argparse
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path

# ============================================================
# GGL GLYPH DEFINITIONS
# ============================================================

GGL_PRIMITIVES = {
    "◯": {"id": 0, "name": "circle", "type": "primitive", "dim": 2},
    "□": {"id": 1, "name": "square", "type": "primitive", "dim": 2},
    "△": {"id": 2, "name": "triangle", "type": "primitive", "dim": 2},
    "◇": {"id": 3, "name": "diamond", "type": "primitive", "dim": 2},
    "⬡": {"id": 4, "name": "hexagon", "type": "primitive", "dim": 2},
    "⬢": {"id": 5, "name": "filled_hexagon", "type": "primitive", "dim": 2},
}

GGL_OPERATORS = {
    "⍯": {"id": 100, "name": "union", "type": "boolean", "arity": 2},
    "⍰": {"id": 101, "name": "difference", "type": "boolean", "arity": 2},
    "⍭": {"id": 102, "name": "intersection", "type": "boolean", "arity": 2},
    "⍸": {"id": 103, "name": "radial_array", "type": "array", "arity": 2},
    "⍼": {"id": 104, "name": "linear_array", "type": "array", "arity": 2},
    "⍻": {"id": 105, "name": "grid_array", "type": "array", "arity": 2},
    "↻": {"id": 106, "name": "rotate", "type": "transform", "arity": 2},
    "↔": {"id": 107, "name": "mirror", "type": "transform", "arity": 2},
    "↕": {"id": 108, "name": "scale", "type": "transform", "arity": 2},
    "→": {"id": 109, "name": "translate", "type": "transform", "arity": 2},
    "⟳": {"id": 110, "name": "sweep", "type": "generator", "arity": 2},
    "⟰": {"id": 111, "name": "extrude", "type": "generator", "arity": 2},
    "⟱": {"id": 112, "name": "revolve", "type": "generator", "arity": 2},
}

SVG3D_OPERATORS = {
    "(⤍)": {"id": 200, "name": "encrypt", "type": "cipher", "maps_to": "encrypt"},
    "(⤎)": {"id": 201, "name": "decrypt", "type": "cipher", "maps_to": "decrypt"},
    "(↻)": {"id": 202, "name": "rotate_3d", "type": "transform", "maps_to": "rotate"},
    "(↔)": {"id": 203, "name": "mirror_3d", "type": "transform", "maps_to": "mirror"},
    "(⟲)": {"id": 204, "name": "spherical_grid", "type": "generator", "maps_to": "spherical_grid"},
    "(⤦)": {"id": 205, "name": "conditional", "type": "control", "maps_to": "conditional"},
    "(⟿)": {"id": 206, "name": "generate_path", "type": "neural", "maps_to": "generate_path"},
    "(⤂)": {"id": 207, "name": "apply_weights", "type": "neural", "maps_to": "apply_weights"},
}

KUHUL_PHASES = {
    "[Pop]": {"id": 300, "type": "phase", "action": "existence"},
    "[Wo]": {"id": 301, "type": "phase", "action": "source"},
    "[Sek]": {"id": 302, "type": "phase", "action": "transform"},
    "[Ch'en]": {"id": 303, "type": "phase", "action": "completion"},
    "[Yax]": {"id": 304, "type": "phase", "action": "reference"},
    "[Xul]": {"id": 305, "type": "phase", "action": "closure"},
}

SPECIAL_TOKENS = {
    "<|begin|>": {"id": 0, "type": "special"},
    "<|end|>": {"id": 1, "type": "special"},
    "<|pad|>": {"id": 2, "type": "special"},
    "<|unk|>": {"id": 3, "type": "special"},
    "<|svg|>": {"id": 4, "type": "special"},
    "<|ggl|>": {"id": 5, "type": "special"},
    "<|kuhul|>": {"id": 6, "type": "special"},
    "<|phase|>": {"id": 7, "type": "special"},
    "<|geometry|>": {"id": 8, "type": "special"},
    "<|transform|>": {"id": 9, "type": "special"},
}


# ============================================================
# GGLTENSOR FORMAT
# ============================================================

class GGLTensorBuilder:
    """Builds the safe.ggltensors format for K'UHUL SVG-3D bridge."""

    MAGIC = b'GGLT'  # GGL Tensor magic bytes
    VERSION = 1

    def __init__(self, output_dir: str = "./bridge"):
        self.output_dir = Path(output_dir)
        self.tensors: Dict[str, Dict] = {}
        self.metadata: Dict[str, Any] = {}

    def add_tensor(self, name: str, shape: List[int], dtype: str = "float32",
                   data: Optional[bytes] = None) -> None:
        """Add a tensor reference to the bundle."""
        tensor_hash = self._compute_hash(name, shape, dtype)

        self.tensors[name] = {
            "shape": shape,
            "dtype": dtype,
            "hash": tensor_hash,
            "size": self._compute_size(shape, dtype),
            "offset": len(self.tensors) * 1024,  # Placeholder offset
        }

    def _compute_hash(self, name: str, shape: List[int], dtype: str) -> str:
        """Compute deterministic hash for tensor."""
        content = f"{name}:{shape}:{dtype}"
        return hashlib.blake2b(content.encode(), digest_size=32).hexdigest()

    def _compute_size(self, shape: List[int], dtype: str) -> int:
        """Compute tensor size in bytes."""
        dtype_sizes = {
            "float32": 4, "float16": 2, "bfloat16": 2,
            "int32": 4, "int64": 8, "int8": 1, "uint8": 1
        }
        elements = 1
        for dim in shape:
            elements *= dim
        return elements * dtype_sizes.get(dtype, 4)

    def set_metadata(self, **kwargs) -> None:
        """Set bundle metadata."""
        self.metadata.update(kwargs)

    def build(self) -> bytes:
        """Build the ggltensors binary format."""
        # Header
        header = {
            "magic": self.MAGIC.decode(),
            "version": self.VERSION,
            "created": datetime.utcnow().isoformat(),
            "tensor_count": len(self.tensors),
            "metadata": self.metadata,
            "tensors": self.tensors
        }

        # Serialize header as JSON
        header_json = json.dumps(header, indent=2, ensure_ascii=False)
        header_bytes = header_json.encode('utf-8')

        # Build binary: magic + version + header_size + header + padding
        result = bytearray()
        result.extend(self.MAGIC)
        result.extend(struct.pack('<I', self.VERSION))
        result.extend(struct.pack('<Q', len(header_bytes)))
        result.extend(header_bytes)

        # Align to 64-byte boundary
        while len(result) % 64 != 0:
            result.append(0)

        return bytes(result)

    def save(self, filename: str = "safe.ggltensors") -> Path:
        """Save the ggltensors file."""
        output_path = self.output_dir / "weights" / filename
        output_path.parent.mkdir(parents=True, exist_ok=True)

        data = self.build()
        with open(output_path, 'wb') as f:
            f.write(data)

        print(f"Saved: {output_path} ({len(data)} bytes)")
        return output_path


# ============================================================
# VOCABULARY BUILDER
# ============================================================

class VocabBuilder:
    """Builds vocab.ggl.json for the K'UHUL SVG-3D bridge."""

    def __init__(self):
        self.vocab: Dict[str, int] = {}
        self.reverse_vocab: Dict[int, str] = {}
        self.token_types: Dict[str, str] = {}
        self.next_id = 1000  # Start regular tokens after special ranges

    def add_special_tokens(self) -> None:
        """Add special control tokens."""
        for token, info in SPECIAL_TOKENS.items():
            self.vocab[token] = info["id"]
            self.reverse_vocab[info["id"]] = token
            self.token_types[token] = "special"

    def add_ggl_primitives(self) -> None:
        """Add GGL primitive glyphs."""
        for glyph, info in GGL_PRIMITIVES.items():
            self.vocab[glyph] = info["id"] + 10  # Offset from special tokens
            self.reverse_vocab[info["id"] + 10] = glyph
            self.token_types[glyph] = "ggl_primitive"

    def add_ggl_operators(self) -> None:
        """Add GGL operators."""
        for op, info in GGL_OPERATORS.items():
            self.vocab[op] = info["id"]
            self.reverse_vocab[info["id"]] = op
            self.token_types[op] = f"ggl_{info['type']}"

    def add_svg3d_operators(self) -> None:
        """Add SVG-3D operators."""
        for op, info in SVG3D_OPERATORS.items():
            self.vocab[op] = info["id"]
            self.reverse_vocab[info["id"]] = op
            self.token_types[op] = f"svg3d_{info['type']}"

    def add_kuhul_phases(self) -> None:
        """Add K'UHUL phase markers."""
        for phase, info in KUHUL_PHASES.items():
            self.vocab[phase] = info["id"]
            self.reverse_vocab[info["id"]] = phase
            self.token_types[phase] = "kuhul_phase"

    def add_base_vocabulary(self, size: int = 32000) -> None:
        """Add base vocabulary tokens."""
        # Add common subword tokens (placeholder - would come from BPE training)
        common_tokens = [
            # Numbers
            "0", "1", "2", "3", "4", "5", "6", "7", "8", "9",
            # Basic punctuation
            ".", ",", ":", ";", "(", ")", "[", "]", "{", "}",
            # Common words/subwords for geometry
            "path", "rect", "circle", "line", "poly", "gon",
            "transform", "rotate", "scale", "translate", "matrix",
            "fill", "stroke", "color", "width", "height",
            "x", "y", "z", "r", "cx", "cy", "rx", "ry",
            "M", "L", "C", "S", "Q", "T", "A", "Z",  # SVG path commands
            "d=", "id=", "class=", "style=",
            # GGL keywords
            "at", "in", "from", "to", "with", "by",
            # Common prefixes/suffixes
            "ing", "ed", "er", "est", "tion", "ness",
        ]

        for token in common_tokens:
            if token not in self.vocab:
                self.vocab[token] = self.next_id
                self.reverse_vocab[self.next_id] = token
                self.token_types[token] = "subword"
                self.next_id += 1

    def build(self) -> Dict[str, Any]:
        """Build the complete vocabulary."""
        self.add_special_tokens()
        self.add_ggl_primitives()
        self.add_ggl_operators()
        self.add_svg3d_operators()
        self.add_kuhul_phases()
        self.add_base_vocabulary()

        return {
            "vocab": self.vocab,
            "reverse_vocab": {str(k): v for k, v in self.reverse_vocab.items()},
            "token_types": self.token_types,
            "vocab_size": len(self.vocab),
            "special_tokens": list(SPECIAL_TOKENS.keys()),
            "ggl_glyphs": list(GGL_PRIMITIVES.keys()) + list(GGL_OPERATORS.keys()),
            "svg3d_operators": list(SVG3D_OPERATORS.keys()),
            "kuhul_phases": list(KUHUL_PHASES.keys()),
        }

    def save(self, output_dir: Path) -> Path:
        """Save vocab.ggl.json."""
        vocab_data = self.build()
        output_path = output_dir / "grammar" / "vocab.ggl.json"
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(vocab_data, f, indent=2, ensure_ascii=False)

        print(f"Saved: {output_path}")
        return output_path


# ============================================================
# TOKENIZER SCHEMA BUILDER
# ============================================================

class TokenizerSchemaBuilder:
    """Builds tokenizer.schema.ggl for the K'UHUL SVG-3D bridge."""

    def build(self) -> Dict[str, Any]:
        return {
            "$schema": "ggl://schema/tokenizer.v1",
            "@id": "kuhul://tokenizer/svg3d-ggl-bridge",
            "@version": "1.0.0",
            "@type": "bpe",

            "config": {
                "vocab_size": 32000,
                "max_length": 8192,
                "pad_token": "<|pad|>",
                "unk_token": "<|unk|>",
                "bos_token": "<|begin|>",
                "eos_token": "<|end|>",
                "add_prefix_space": False,
                "trim_offsets": True,
            },

            "special_tokens": {
                "control": ["<|begin|>", "<|end|>", "<|pad|>", "<|unk|>"],
                "mode": ["<|svg|>", "<|ggl|>", "<|kuhul|>"],
                "semantic": ["<|phase|>", "<|geometry|>", "<|transform|>"],
            },

            "glyph_tokens": {
                "primitives": list(GGL_PRIMITIVES.keys()),
                "boolean_ops": ["⍯", "⍰", "⍭"],
                "array_ops": ["⍸", "⍼", "⍻"],
                "transform_ops": ["↻", "↔", "↕", "→"],
                "generator_ops": ["⟳", "⟰", "⟱"],
            },

            "svg3d_tokens": {
                "cipher": ["(⤍)", "(⤎)"],
                "transform": ["(↻)", "(↔)"],
                "generator": ["(⟲)"],
                "control": ["(⤦)"],
                "neural": ["(⟿)", "(⤂)"],
            },

            "kuhul_tokens": {
                "phases": ["[Pop]", "[Wo]", "[Sek]", "[Ch'en]", "[Yax]", "[Xul]"],
                "transition": "→",
            },

            "normalizer": {
                "type": "sequence",
                "normalizers": [
                    {"type": "nfc"},
                    {"type": "strip"},
                    {"type": "lowercase", "apply_to": "keywords_only"},
                ]
            },

            "pre_tokenizer": {
                "type": "sequence",
                "pretokenizers": [
                    {"type": "whitespace"},
                    {"type": "punctuation"},
                    {"type": "glyph_split", "glyphs": "◯□△◇⬡⬢⍯⍰⍭⍸⍼⍻↻↔↕→⟳⟰⟱"},
                ]
            },

            "decoder": {
                "type": "bpe",
                "suffix": "",
            }
        }

    def save(self, output_dir: Path) -> Path:
        """Save tokenizer.schema.ggl."""
        schema = self.build()
        output_path = output_dir / "grammar" / "tokenizer.schema.ggl.json"
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(schema, f, indent=2, ensure_ascii=False)

        print(f"Saved: {output_path}")
        return output_path


# ============================================================
# POLICY CONFIG BUILDER
# ============================================================

class PolicyBuilder:
    """Builds policy configuration files."""

    def build_generation_config(self) -> Dict[str, Any]:
        return {
            "$schema": "ggl://schema/generation.v1",
            "@id": "kuhul://policy/generation",
            "@version": "1.0.0",

            "defaults": {
                "max_new_tokens": 2048,
                "temperature": 0.7,
                "top_p": 0.9,
                "top_k": 50,
                "repetition_penalty": 1.1,
                "do_sample": True,
            },

            "geometry_mode": {
                "temperature": 0.3,
                "top_p": 0.95,
                "repetition_penalty": 1.0,
                "description": "Precise geometry generation",
            },

            "creative_mode": {
                "temperature": 1.0,
                "top_p": 0.9,
                "top_k": 100,
                "description": "Creative/exploratory generation",
            },

            "deterministic_mode": {
                "temperature": 0.0,
                "do_sample": False,
                "description": "Fully deterministic output",
            },

            "stop_sequences": [
                "[Xul]",
                "<|end|>",
                "\n\n---\n",
            ],

            "ggl_constraints": {
                "balanced_brackets": True,
                "valid_glyphs_only": True,
                "max_nesting_depth": 10,
            }
        }

    def build_model_constraints(self) -> Dict[str, Any]:
        return {
            "$schema": "ggl://schema/constraints.v1",
            "@id": "kuhul://policy/constraints",
            "@version": "1.0.0",

            "safety": {
                "max_geometry_complexity": 10000,
                "max_boolean_depth": 5,
                "max_array_size": 1000,
                "timeout_ms": 30000,
            },

            "memory": {
                "max_tensor_size_mb": 1024,
                "max_batch_size": 32,
                "cache_size_mb": 512,
            },

            "execution": {
                "allow_eval": False,
                "deterministic": True,
                "reproducible_seed": True,
            },

            "bridge": {
                "svg_output": True,
                "ggl_output": True,
                "threejs_output": True,
                "preserve_topology": True,
            }
        }

    def save(self, output_dir: Path) -> List[Path]:
        """Save policy files."""
        policy_dir = output_dir / "policy"
        policy_dir.mkdir(parents=True, exist_ok=True)

        paths = []

        # Generation config
        gen_path = policy_dir / "generation.ggl.json"
        with open(gen_path, 'w', encoding='utf-8') as f:
            json.dump(self.build_generation_config(), f, indent=2, ensure_ascii=False)
        print(f"Saved: {gen_path}")
        paths.append(gen_path)

        # Model constraints
        constraints_path = policy_dir / "model_constraints.ggl.json"
        with open(constraints_path, 'w', encoding='utf-8') as f:
            json.dump(self.build_model_constraints(), f, indent=2, ensure_ascii=False)
        print(f"Saved: {constraints_path}")
        paths.append(constraints_path)

        return paths


# ============================================================
# BRIDGE MANIFEST BUILDER
# ============================================================

class BridgeManifestBuilder:
    """Builds the bridge manifest."""

    def build(self) -> Dict[str, Any]:
        return {
            "$schema": "ggl://schema/bridge.v1",
            "@id": "kuhul://bridge/svg3d-ggl",
            "@version": "1.0.0",
            "@status": "frozen",
            "@description": "K'UHUL SVG-3D ↔ GGL Inference Bridge",

            "architecture": {
                "principle": "SVG is not output — it is the ABI",
                "layers": {
                    "inference_core": "opaque - weights only",
                    "tokenization": "symbolic - structure mirrored",
                    "policy": "lightweight - boundary constraints",
                    "projection": "spatial - SVG/3D output",
                },
            },

            "files": {
                "grammar": {
                    "vocab": "grammar/vocab.ggl.json",
                    "tokenizer": "grammar/tokenizer.schema.ggl.json",
                    "merges": "grammar/merges.ggl.txt",
                    "tokens_map": "grammar/tokens.map.ggl.json",
                },
                "policy": {
                    "generation": "policy/generation.ggl.json",
                    "constraints": "policy/model_constraints.ggl.json",
                },
                "weights": {
                    "tensors": "weights/safe.ggltensors",
                    "index": "weights/tensor.index.json",
                },
                "templates": {
                    "chat": "templates/chat_template.ggl.svg",
                    "geometry": "templates/geometry_template.ggl.svg",
                },
                "projection": {
                    "svg_runtime": "projection/svg_runtime.js",
                    "threejs_bridge": "projection/threejs_bridge.js",
                },
            },

            "execution_flow": [
                "1. Tokens from MX2LM",
                "2. Normalization in bridge",
                "3. GGL semantic layer",
                "4. Inference execution",
                "5. SVG/3D projection mouth",
            ],

            "invariants": [
                "no_eval_from_state",
                "deterministic_replay",
                "existence_precedes_execution",
                "nothing_executes_everything_describes",
            ],
        }

    def save(self, output_dir: Path) -> Path:
        """Save bridge manifest."""
        manifest_path = output_dir / "bridge.manifest.json"

        with open(manifest_path, 'w', encoding='utf-8') as f:
            json.dump(self.build(), f, indent=2, ensure_ascii=False)

        print(f"Saved: {manifest_path}")
        return manifest_path


# ============================================================
# ADDITIONAL FILES
# ============================================================

def create_merges_file(output_dir: Path) -> Path:
    """Create merges.ggl.txt for BPE tokenizer."""
    merges_path = output_dir / "grammar" / "merges.ggl.txt"
    merges_path.parent.mkdir(parents=True, exist_ok=True)

    # Basic BPE merges (placeholder - would come from actual training)
    merges = [
        "# K'UHUL SVG-3D GGL Merges v1.0",
        "# Format: token1 token2 -> merged",
        "",
        "# SVG path merges",
        "M 0 -> M0",
        "L 0 -> L0",
        "C 0 -> C0",
        "",
        "# Common subword merges",
        "tr ans -> trans",
        "trans form -> transform",
        "ro tate -> rotate",
        "sc ale -> scale",
        "ge om -> geom",
        "geom etry -> geometry",
        "",
        "# GGL operator context",
        "{ r -> {r",
        "{r : -> {r:",
        "{ s -> {s",
        "{s : -> {s:",
    ]

    with open(merges_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(merges))

    print(f"Saved: {merges_path}")
    return merges_path


def create_tokens_map(output_dir: Path) -> Path:
    """Create unified tokens.map.ggl.json."""
    tokens_map = {
        "$schema": "ggl://schema/tokens_map.v1",
        "@version": "1.0.0",

        "special_tokens_map": {
            "bos_token": "<|begin|>",
            "eos_token": "<|end|>",
            "unk_token": "<|unk|>",
            "pad_token": "<|pad|>",
            "sep_token": None,
            "cls_token": None,
            "mask_token": None,
        },

        "added_tokens": [
            {"content": "<|svg|>", "lstrip": False, "rstrip": False, "single_word": True, "normalized": False},
            {"content": "<|ggl|>", "lstrip": False, "rstrip": False, "single_word": True, "normalized": False},
            {"content": "<|kuhul|>", "lstrip": False, "rstrip": False, "single_word": True, "normalized": False},
            {"content": "<|phase|>", "lstrip": False, "rstrip": False, "single_word": True, "normalized": False},
            {"content": "<|geometry|>", "lstrip": False, "rstrip": False, "single_word": True, "normalized": False},
            {"content": "<|transform|>", "lstrip": False, "rstrip": False, "single_word": True, "normalized": False},
        ],

        "glyph_tokens": {
            "primitives": ["◯", "□", "△", "◇", "⬡", "⬢"],
            "operators": ["⍯", "⍰", "⍭", "⍸", "⍼", "⍻", "↻", "↔", "↕", "→", "⟳", "⟰", "⟱"],
        },

        "svg3d_tokens": ["(⤍)", "(⤎)", "(↻)", "(↔)", "(⟲)", "(⤦)", "(⟿)", "(⤂)"],

        "kuhul_tokens": ["[Pop]", "[Wo]", "[Sek]", "[Ch'en]", "[Yax]", "[Xul]"],
    }

    tokens_path = output_dir / "grammar" / "tokens.map.ggl.json"
    with open(tokens_path, 'w', encoding='utf-8') as f:
        json.dump(tokens_map, f, indent=2, ensure_ascii=False)

    print(f"Saved: {tokens_path}")
    return tokens_path


def create_chat_template(output_dir: Path) -> Path:
    """Create chat_template.ggl.svg."""
    template = '''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg"
     xmlns:ggl="ggl://namespace/v1"
     xmlns:kuhul="kuhul://namespace/v1"
     viewBox="0 0 800 600">

  <title>K'UHUL Chat Template</title>

  <metadata>
    <ggl:template version="1.0">
      <ggl:format>
        <![CDATA[
{%- for message in messages %}
{%- if message.role == 'system' %}
<|kuhul|>[Pop system]
  [Wo content]→[Ch'en "{{ message.content }}"]
[Xul]
{%- elif message.role == 'user' %}
<|kuhul|>[Pop user]
  [Wo query]→[Ch'en "{{ message.content }}"]
[Xul]
{%- elif message.role == 'assistant' %}
<|kuhul|>[Pop assistant]
  [Wo response]→[Ch'en "{{ message.content }}"]
[Xul]
{%- endif %}
{%- endfor %}
{%- if add_generation_prompt %}
<|kuhul|>[Pop assistant]
  [Wo response]→
{%- endif %}
        ]]>
      </ggl:format>
    </ggl:template>
  </metadata>

  <defs>
    <g id="message-frame">
      <rect x="0" y="0" width="100%" height="auto" rx="8"
            fill="rgba(22,242,170,0.1)" stroke="#16f2aa"/>
    </g>
  </defs>

  <g id="chat-container" ggl:role="chat" kuhul:phase="projection">
    <!-- Messages rendered here -->
  </g>

</svg>
'''

    template_path = output_dir / "templates" / "chat_template.ggl.svg"
    template_path.parent.mkdir(parents=True, exist_ok=True)

    with open(template_path, 'w', encoding='utf-8') as f:
        f.write(template)

    print(f"Saved: {template_path}")
    return template_path


def create_tensor_index(output_dir: Path, tensors: Dict) -> Path:
    """Create tensor.index.json for weight references."""
    index = {
        "$schema": "ggl://schema/tensor_index.v1",
        "@version": "1.0.0",
        "@type": "weight_reference",
        "@description": "Tensor index for safe.ggltensors - references only, no data",

        "format": "ggltensor",
        "dtype_default": "float32",
        "total_size": sum(t.get("size", 0) for t in tensors.values()),

        "tensors": tensors,

        "layers": {
            "embedding": ["embed.weight"],
            "attention": [f"layer.{i}.attn" for i in range(32)],
            "mlp": [f"layer.{i}.mlp" for i in range(32)],
            "norm": ["norm.weight", "norm.bias"],
            "output": ["lm_head.weight"],
        },
    }

    index_path = output_dir / "weights" / "tensor.index.json"
    with open(index_path, 'w', encoding='utf-8') as f:
        json.dump(index, f, indent=2, ensure_ascii=False)

    print(f"Saved: {index_path}")
    return index_path


# ============================================================
# MAIN BUILD FUNCTION
# ============================================================

def build_bridge(output_dir: str = "./bridge") -> None:
    """Build all bridge files."""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print("K'UHUL SVG-3D ↔ GGL Bridge Builder")
    print("=" * 60)
    print()

    # 1. Build safe.ggltensors
    print("Building safe.ggltensors...")
    tensor_builder = GGLTensorBuilder(output_dir)

    # Add reference tensors (these are structure only, not actual weights)
    tensor_builder.add_tensor("embed.weight", [32000, 4096], "float16")
    for i in range(32):
        tensor_builder.add_tensor(f"layer.{i}.attn.q", [4096, 4096], "float16")
        tensor_builder.add_tensor(f"layer.{i}.attn.k", [4096, 4096], "float16")
        tensor_builder.add_tensor(f"layer.{i}.attn.v", [4096, 4096], "float16")
        tensor_builder.add_tensor(f"layer.{i}.attn.o", [4096, 4096], "float16")
        tensor_builder.add_tensor(f"layer.{i}.mlp.gate", [4096, 11008], "float16")
        tensor_builder.add_tensor(f"layer.{i}.mlp.up", [4096, 11008], "float16")
        tensor_builder.add_tensor(f"layer.{i}.mlp.down", [11008, 4096], "float16")
    tensor_builder.add_tensor("norm.weight", [4096], "float16")
    tensor_builder.add_tensor("lm_head.weight", [32000, 4096], "float16")

    tensor_builder.set_metadata(
        model_type="kuhul-svg3d-ggl",
        architecture="transformer",
        hidden_size=4096,
        num_layers=32,
        num_heads=32,
        vocab_size=32000,
    )
    tensor_builder.save()
    print()

    # 2. Build vocab.ggl.json
    print("Building vocab.ggl.json...")
    vocab_builder = VocabBuilder()
    vocab_builder.save(output_path)
    print()

    # 3. Build tokenizer.schema.ggl
    print("Building tokenizer.schema.ggl...")
    tokenizer_builder = TokenizerSchemaBuilder()
    tokenizer_builder.save(output_path)
    print()

    # 4. Build policy files
    print("Building policy files...")
    policy_builder = PolicyBuilder()
    policy_builder.save(output_path)
    print()

    # 5. Build additional files
    print("Building additional files...")
    create_merges_file(output_path)
    create_tokens_map(output_path)
    create_chat_template(output_path)
    create_tensor_index(output_path, tensor_builder.tensors)
    print()

    # 6. Build bridge manifest
    print("Building bridge manifest...")
    manifest_builder = BridgeManifestBuilder()
    manifest_builder.save(output_path)
    print()

    print("=" * 60)
    print("Bridge build complete!")
    print(f"Output directory: {output_path.absolute()}")
    print("=" * 60)


# ============================================================
# CLI ENTRY POINT
# ============================================================

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Build K'UHUL SVG-3D ↔ GGL Bridge files"
    )
    parser.add_argument(
        "--output-dir", "-o",
        default="./bridge",
        help="Output directory for bridge files (default: ./bridge)"
    )

    args = parser.parse_args()
    build_bridge(args.output_dir)
