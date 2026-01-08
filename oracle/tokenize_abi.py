from __future__ import annotations

from typing import Any, Dict, Iterable, Optional


class TokenizeError(RuntimeError):
    def __init__(self, code: str, msg: str, line: int = 0, col: int = 0) -> None:
        super().__init__(msg)
        self.code = code
        self.msg = msg
        self.line = line
        self.col = col


def abi_tokenize_ok(text: str, tokenizer_abi: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Validate text against a tokenizer ABI.

    Returns None when valid, otherwise an error dict with code/msg/line/col.
    """
    allowed_ranges = tokenizer_abi.get("allowed_codepoint_ranges") or []
    forbidden_ranges = tokenizer_abi.get("forbidden_codepoint_ranges") or []
    allowed_set = set(tokenizer_abi.get("allowed_codepoints") or [])
    forbidden_set = set(tokenizer_abi.get("forbidden_codepoints") or [])

    for idx, ch in enumerate(text):
        cp = ord(ch)
        line, col = _line_col(text, idx)

        if cp in forbidden_set or _in_ranges(cp, forbidden_ranges):
            return {
                "code": "E_TOK_FORBIDDEN",
                "msg": f"forbidden codepoint: U+{cp:04X}",
                "line": line,
                "col": col,
            }
        if allowed_set or allowed_ranges:
            if cp not in allowed_set and not _in_ranges(cp, allowed_ranges):
                return {
                    "code": "E_TOK_DISALLOWED",
                    "msg": f"disallowed codepoint: U+{cp:04X}",
                    "line": line,
                    "col": col,
                }

    return None


def _in_ranges(cp: int, ranges: Iterable[Iterable[int]]) -> bool:
    for pair in ranges:
        if len(pair) != 2:
            continue
        start, end = pair
        if start <= cp <= end:
            return True
    return False


def _line_col(text: str, idx: int) -> tuple[int, int]:
    line = text.count("\n", 0, idx) + 1
    last_nl = text.rfind("\n", 0, idx)
    col = idx + 1 if last_nl == -1 else idx - last_nl
    return line, col
