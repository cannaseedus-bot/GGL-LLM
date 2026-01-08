import java.util.List;
import java.util.Map;

public final class GglTokenizeAbi {
    public static final class Err {
        public final String code;
        public final String msg;
        public final int line;
        public final int col;

        public Err(String code, String msg, int line, int col) {
            this.code = code;
            this.msg = msg;
            this.line = line;
            this.col = col;
        }
    }

    @SuppressWarnings("unchecked")
    public static Err check(String text, Object abiObj) {
        if (!(abiObj instanceof Map)) {
            return null;
        }
        Map<String, Object> abi = (Map<String, Object>) abiObj;
        List<Object> allowedRanges = (List<Object>) abi.getOrDefault("allowed_codepoint_ranges", List.of());
        List<Object> forbiddenRanges = (List<Object>) abi.getOrDefault("forbidden_codepoint_ranges", List.of());
        List<Object> allowedPoints = (List<Object>) abi.getOrDefault("allowed_codepoints", List.of());
        List<Object> forbiddenPoints = (List<Object>) abi.getOrDefault("forbidden_codepoints", List.of());

        for (int i = 0; i < text.length(); i++) {
            int cp = text.codePointAt(i);
            int[] lc = lineCol(text, i);
            if (contains(forbiddenPoints, cp) || inRanges(cp, forbiddenRanges)) {
                return new Err("E_TOK_FORBIDDEN", String.format("forbidden codepoint: U+%04X", cp), lc[0], lc[1]);
            }
            if (!allowedPoints.isEmpty() || !allowedRanges.isEmpty()) {
                if (!contains(allowedPoints, cp) && !inRanges(cp, allowedRanges)) {
                    return new Err("E_TOK_DISALLOWED", String.format("disallowed codepoint: U+%04X", cp), lc[0], lc[1]);
                }
            }
            if (Character.charCount(cp) > 1) {
                i++;
            }
        }
        return null;
    }

    private static boolean contains(List<Object> list, int cp) {
        for (Object item : list) {
            if (item instanceof Number && ((Number) item).intValue() == cp) {
                return true;
            }
        }
        return false;
    }

    private static boolean inRanges(int cp, List<Object> ranges) {
        for (Object item : ranges) {
            if (!(item instanceof List)) continue;
            List<?> pair = (List<?>) item;
            if (pair.size() != 2) continue;
            Object startObj = pair.get(0);
            Object endObj = pair.get(1);
            if (startObj instanceof Number && endObj instanceof Number) {
                int start = ((Number) startObj).intValue();
                int end = ((Number) endObj).intValue();
                if (start <= cp && cp <= end) return true;
            }
        }
        return false;
    }

    private static int[] lineCol(String text, int idx) {
        int line = 1;
        int col = 1;
        for (int i = 0; i < idx; i++) {
            if (text.charAt(i) == '\n') {
                line++;
                col = 1;
            } else {
                col++;
            }
        }
        return new int[]{line, col};
    }
}
