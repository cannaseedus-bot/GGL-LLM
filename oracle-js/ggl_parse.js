export class ParseError extends Error {
  constructor(code, msg, line = 0, col = 0) {
    super(msg);
    this.code = code;
    this.msg = msg;
    this.line = line;
    this.col = col;
  }
}

export function parseGglToAst(text, grammarAbi) {
  if (!text) {
    throw new ParseError("E_PARSE_EMPTY", "empty GGL payload", 1, 1);
  }
  return { type: "GGLDocument", body: text, grammar: grammarAbi?.id };
}
