from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict


@dataclass
class ParseError(Exception):
    code: str
    msg: str
    line: int = 0
    col: int = 0


def parse_ggl_to_ast(text: str, grammar_abi: Dict[str, Any]) -> Dict[str, Any]:
    """Parse GGL source into an AST.

    This is a placeholder implementation. Replace with the real parser.
    """
    if not text:
        raise ParseError(code="E_PARSE_EMPTY", msg="empty GGL payload", line=1, col=1)
    return {"type": "GGLDocument", "body": text, "grammar": grammar_abi.get("id")}
