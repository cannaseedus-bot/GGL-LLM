import java.util.Map;

public final class GglLegal {
    public static final class LegalityError extends RuntimeException {
        public final String code;

        public LegalityError(String code, String msg) {
            super(msg);
            this.code = code;
        }
    }

    @SuppressWarnings("unchecked")
    public static void check(Object ast, Object grammarAbi) {
        if (!(ast instanceof Map)) {
            throw new LegalityError("E_LEGAL_AST", "invalid AST root");
        }
        Map<String, Object> map = (Map<String, Object>) ast;
        if (!"GGLDocument".equals(map.get("type"))) {
            throw new LegalityError("E_LEGAL_AST", "invalid AST root");
        }
    }
}
