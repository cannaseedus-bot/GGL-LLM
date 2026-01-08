import java.util.LinkedHashMap;
import java.util.Map;

public final class GglParse {
    public static final class ParseError extends RuntimeException {
        public final String code;
        public final int line;
        public final int col;

        public ParseError(String code, String msg, int line, int col) {
            super(msg);
            this.code = code;
            this.line = line;
            this.col = col;
        }
    }

    public static Map<String, Object> parseToAst(String text, Object grammarAbi) {
        if (text == null || text.isEmpty()) {
            throw new ParseError("E_PARSE_EMPTY", "empty GGL payload", 1, 1);
        }
        Map<String, Object> ast = new LinkedHashMap<>();
        ast.put("type", "GGLDocument");
        ast.put("body", text);
        ast.put("grammar", grammarAbi);
        return ast;
    }
}
