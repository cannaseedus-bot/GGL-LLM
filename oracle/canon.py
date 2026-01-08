from __future__ import annotations

from io import BytesIO
from typing import Any, Iterable, Mapping


def canon_json_bytes_v1(value: Any) -> bytes:
    """Serialize JSON-like data to canonical UTF-8 bytes (asx://canon/json.bytes.v1)."""
    out = BytesIO()
    _write_canon(value, out)
    return out.getvalue()


def _write_canon(value: Any, out: BytesIO) -> None:
    if value is None:
        out.write(b"null")
        return
    if isinstance(value, bool):
        out.write(b"true" if value else b"false")
        return
    if isinstance(value, int):
        out.write(str(value).encode("utf-8"))
        return
    if isinstance(value, float):
        raise ValueError("non-canonical number: floats are not allowed")
    if isinstance(value, str):
        _write_string(value, out)
        return
    if isinstance(value, Mapping):
        _write_object(value, out)
        return
    if isinstance(value, Iterable) and not isinstance(value, (bytes, bytearray)):
        _write_array(value, out)
        return
    raise TypeError(f"unsupported json node: {type(value)!r}")


def _write_array(values: Iterable[Any], out: BytesIO) -> None:
    out.write(b"[")
    first = True
    for item in values:
        if not first:
            out.write(b",")
        first = False
        _write_canon(item, out)
    out.write(b"]")


def _write_object(values: Mapping[str, Any], out: BytesIO) -> None:
    out.write(b"{")
    keys = sorted(values.keys(), key=_codepoint_key)
    for idx, key in enumerate(keys):
        if idx:
            out.write(b",")
        _write_string(str(key), out)
        out.write(b":")
        _write_canon(values[key], out)
    out.write(b"}")


def _codepoint_key(value: str) -> list[int]:
    return [ord(ch) for ch in value]


def _write_string(value: str, out: BytesIO) -> None:
    out.write(b'"')
    for ch in value:
        code = ord(ch)
        if ch == '"':
            out.write(b"\\\"")
        elif ch == "\\":
            out.write(b"\\\\")
        elif ch == "\b":
            out.write(b"\\b")
        elif ch == "\f":
            out.write(b"\\f")
        elif ch == "\n":
            out.write(b"\\n")
        elif ch == "\r":
            out.write(b"\\r")
        elif ch == "\t":
            out.write(b"\\t")
        elif code < 0x20:
            out.write(f"\\u{code:04x}".encode("utf-8"))
        else:
            out.write(ch.encode("utf-8"))
    out.write(b'"')
