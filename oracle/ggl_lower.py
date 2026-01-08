from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict


@dataclass
class LowerError(Exception):
    code: str
    msg: str


def lower_ast_to_scene_xjson(ast: Dict[str, Any], grammar_abi: Dict[str, Any]) -> Dict[str, Any]:
    """Lower AST into scene XJSON.

    Placeholder implementation produces a minimal envelope.
    """
    if not isinstance(ast, dict):
        raise LowerError(code="E_LOWER_AST", msg="invalid AST")
    return {
        "@scene": "asx://schema/scene.ir.v1",
        "grammar": grammar_abi.get("id"),
        "body": ast,
    }
