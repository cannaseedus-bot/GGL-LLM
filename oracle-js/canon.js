export function canonJsonBytesV1(value) {
  const chunks = [];
  writeCanon(value, chunks);
  return Uint8Array.from(Buffer.concat(chunks));
}

function writeCanon(value, chunks) {
  if (value === null) {
    chunks.push(Buffer.from("null"));
    return;
  }
  if (typeof value === "boolean") {
    chunks.push(Buffer.from(value ? "true" : "false"));
    return;
  }
  if (typeof value === "number") {
    if (!Number.isInteger(value)) {
      throw new Error("non-canonical number: floats are not allowed");
    }
    chunks.push(Buffer.from(String(value)));
    return;
  }
  if (typeof value === "string") {
    writeString(value, chunks);
    return;
  }
  if (Array.isArray(value)) {
    chunks.push(Buffer.from("["));
    value.forEach((item, idx) => {
      if (idx > 0) chunks.push(Buffer.from(","));
      writeCanon(item, chunks);
    });
    chunks.push(Buffer.from("]"));
    return;
  }
  if (typeof value === "object") {
    chunks.push(Buffer.from("{"));
    const keys = Object.keys(value).sort(codepointCompare);
    keys.forEach((key, idx) => {
      if (idx > 0) chunks.push(Buffer.from(","));
      writeString(key, chunks);
      chunks.push(Buffer.from(":"));
      writeCanon(value[key], chunks);
    });
    chunks.push(Buffer.from("}"));
    return;
  }
  throw new Error(`unsupported json node: ${typeof value}`);
}

function codepointCompare(a, b) {
  const alen = a.length;
  const blen = b.length;
  let ia = 0;
  let ib = 0;
  while (ia < alen && ib < blen) {
    const ca = a.codePointAt(ia);
    const cb = b.codePointAt(ib);
    if (ca !== cb) return ca - cb;
    ia += ca > 0xffff ? 2 : 1;
    ib += cb > 0xffff ? 2 : 1;
  }
  return alen - blen;
}

function writeString(value, chunks) {
  chunks.push(Buffer.from('"'));
  for (let i = 0; i < value.length; i += 1) {
    const ch = value[i];
    const code = value.charCodeAt(i);
    switch (ch) {
      case '"':
        chunks.push(Buffer.from("\\\""));
        break;
      case "\\":
        chunks.push(Buffer.from("\\\\"));
        break;
      case "\b":
        chunks.push(Buffer.from("\\b"));
        break;
      case "\f":
        chunks.push(Buffer.from("\\f"));
        break;
      case "\n":
        chunks.push(Buffer.from("\\n"));
        break;
      case "\r":
        chunks.push(Buffer.from("\\r"));
        break;
      case "\t":
        chunks.push(Buffer.from("\\t"));
        break;
      default:
        if (code < 0x20) {
          chunks.push(Buffer.from(`\\u${code.toString(16).padStart(4, "0")}`));
        } else {
          chunks.push(Buffer.from(ch));
        }
    }
  }
  chunks.push(Buffer.from('"'));
}
