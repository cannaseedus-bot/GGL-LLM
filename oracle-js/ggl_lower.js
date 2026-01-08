export class LowerError extends Error {
  constructor(code, msg) {
    super(msg);
    this.code = code;
    this.msg = msg;
  }
}

export function lowerAstToSceneXjson(ast, grammarAbi) {
  if (!ast || typeof ast !== "object") {
    throw new LowerError("E_LOWER_AST", "invalid AST");
  }
  return {
    "@scene": "asx://schema/scene.ir.v1",
    grammar: grammarAbi?.id,
    body: ast,
  };
}
