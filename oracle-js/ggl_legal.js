export class LegalityError extends Error {
  constructor(code, msg, line = 0, col = 0) {
    super(msg);
    this.code = code;
    this.msg = msg;
    this.line = line;
    this.col = col;
  }
}

export function checkLegality(ast, grammarAbi) {
  if (!ast || ast.type !== "GGLDocument") {
    throw new LegalityError("E_LEGAL_AST", "invalid AST root");
  }
}
