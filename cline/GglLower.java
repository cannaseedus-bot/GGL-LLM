import java.util.LinkedHashMap;
import java.util.Map;

public final class GglLower {
    public static final class LowerError extends RuntimeException {
        public final String code;

        public LowerError(String code, String msg) {
            super(msg);
            this.code = code;
        }
    }

    public static Map<String, Object> lower(Object ast, Object grammarAbi) {
        if (!(ast instanceof Map)) {
            throw new LowerError("E_LOWER_AST", "invalid AST");
        }
        Map<String, Object> out = new LinkedHashMap<>();
        out.put("@scene", "asx://schema/scene.ir.v1");
        out.put("grammar", grammarAbi);
        out.put("body", ast);
        return out;
    }
}
