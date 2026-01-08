export function abiTokenizeOk(text, tokenizerAbi) {
  const allowedRanges = tokenizerAbi.allowed_codepoint_ranges || [];
  const forbiddenRanges = tokenizerAbi.forbidden_codepoint_ranges || [];
  const allowedSet = new Set(tokenizerAbi.allowed_codepoints || []);
  const forbiddenSet = new Set(tokenizerAbi.forbidden_codepoints || []);

  for (let idx = 0; idx < text.length; idx += 1) {
    const cp = text.codePointAt(idx);
    const { line, col } = lineCol(text, idx);

    if (forbiddenSet.has(cp) || inRanges(cp, forbiddenRanges)) {
      return {
        code: "E_TOK_FORBIDDEN",
        msg: `forbidden codepoint: U+${cp.toString(16).toUpperCase().padStart(4, "0")}`,
        line,
        col,
      };
    }
    if (allowedSet.size || allowedRanges.length) {
      if (!allowedSet.has(cp) && !inRanges(cp, allowedRanges)) {
        return {
          code: "E_TOK_DISALLOWED",
          msg: `disallowed codepoint: U+${cp.toString(16).toUpperCase().padStart(4, "0")}`,
          line,
          col,
        };
      }
    }
    if (cp > 0xffff) idx += 1;
  }

  return null;
}

function inRanges(cp, ranges) {
  for (const pair of ranges) {
    if (!Array.isArray(pair) || pair.length !== 2) continue;
    const [start, end] = pair;
    if (start <= cp && cp <= end) return true;
  }
  return false;
}

function lineCol(text, idx) {
  const before = text.slice(0, idx);
  const line = before.split("\n").length;
  const lastNl = before.lastIndexOf("\n");
  const col = lastNl === -1 ? idx + 1 : idx - lastNl;
  return { line, col };
}
