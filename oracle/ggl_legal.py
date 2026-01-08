from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict


@dataclass
class LegalityError(Exception):
    code: str
    msg: str
    line: int = 0
    col: int = 0


def check_legality(ast: Dict[str, Any], grammar_abi: Dict[str, Any]) -> None:
    """Validate AST legality against the grammar ABI.

    This placeholder enforces the presence of a document node.
    """
    if not isinstance(ast, dict) or ast.get("type") != "GGLDocument":
        raise LegalityError(code="E_LEGAL_AST", msg="invalid AST root")
