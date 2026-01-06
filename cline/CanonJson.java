import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.io.OutputStream;
import java.io.UncheckedIOException;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

/**
 * CanonJson — parse JSON into Java primitives and write canonical bytes.
 * Dependency-free.
 *
 * Canon rules:
 * - UTF-8
 * - object keys sorted
 * - no whitespace
 * - integers only as JSON numbers (no decimal/exponent)
 * - decimals should be strings (enforced by schema/usage)
 */
public final class CanonJson {

    public static Object parse(byte[] utf8) {
        return new Parser(new String(utf8, StandardCharsets.UTF_8)).parseAny();
    }

    public static byte[] canonicalize(Object value) {
        ByteArrayOutputStream out = new ByteArrayOutputStream();
        try {
            writeCanonical(value, out);
        } catch (IOException e) {
            throw new UncheckedIOException(e);
        }
        return out.toByteArray();
    }

    public static void writeCanonical(Object v, OutputStream out) throws IOException {
        if (v == null) {
            out.write("null".getBytes(StandardCharsets.UTF_8));
            return;
        }
        if (v instanceof String) {
            writeString((String) v, out);
            return;
        }
        if (v instanceof Boolean) {
            out.write(((Boolean) v) ? "true".getBytes(StandardCharsets.UTF_8) : "false".getBytes(StandardCharsets.UTF_8));
            return;
        }
        if (v instanceof Number) {
            String s = v.toString();
            if (!isCanonicalInteger(s)) throw new IllegalArgumentException("non-canonical integer: " + s);
            out.write(s.getBytes(StandardCharsets.UTF_8));
            return;
        }
        if (v instanceof List) {
            out.write('[');
            List<?> a = (List<?>) v;
            for (int i = 0; i < a.size(); i++) {
                if (i > 0) out.write(',');
                writeCanonical(a.get(i), out);
            }
            out.write(']');
            return;
        }
        if (v instanceof Map) {
            out.write('{');
            @SuppressWarnings("unchecked")
            Map<String, Object> m = (Map<String, Object>) v;
            ArrayList<String> keys = new ArrayList<>(m.keySet());
            keys.sort(CanonJson::codepointCompare);
            for (int i = 0; i < keys.size(); i++) {
                if (i > 0) out.write(',');
                String k = keys.get(i);
                writeString(k, out);
                out.write(':');
                writeCanonical(m.get(k), out);
            }
            out.write('}');
            return;
        }
        throw new IllegalArgumentException("unsupported json node: " + v.getClass());
    }

    private static int codepointCompare(String a, String b) {
        int ia = 0, ib = 0;
        int na = a.length(), nb = b.length();
        while (ia < na && ib < nb) {
            int ca = a.codePointAt(ia);
            int cb = b.codePointAt(ib);
            if (ca != cb) return Integer.compare(ca, cb);
            ia += Character.charCount(ca);
            ib += Character.charCount(cb);
        }
        return Integer.compare(na, nb);
    }

    private static boolean isCanonicalInteger(String s) {
        if (s.isEmpty()) return false;
        int i = 0;
        if (s.charAt(0) == '-') {
            if (s.length() == 1) return false;
            i = 1;
        }
        if (s.charAt(i) == '0') return (i == s.length() - 1);
        for (; i < s.length(); i++) {
            char c = s.charAt(i);
            if (c < '0' || c > '9') return false;
        }
        return true;
    }

    private static void writeString(String s, OutputStream out) throws IOException {
        out.write('"');
        for (int i = 0; i < s.length(); i++) {
            char c = s.charAt(i);
            switch (c) {
                case '"':
                    out.write("\\\"".getBytes(StandardCharsets.UTF_8));
                    break;
                case '\\':
                    out.write("\\\\".getBytes(StandardCharsets.UTF_8));
                    break;
                case '\b':
                    out.write("\\b".getBytes(StandardCharsets.UTF_8));
                    break;
                case '\f':
                    out.write("\\f".getBytes(StandardCharsets.UTF_8));
                    break;
                case '\n':
                    out.write("\\n".getBytes(StandardCharsets.UTF_8));
                    break;
                case '\r':
                    out.write("\\r".getBytes(StandardCharsets.UTF_8));
                    break;
                case '\t':
                    out.write("\\t".getBytes(StandardCharsets.UTF_8));
                    break;
                default:
                    if (c < 0x20) {
                        String hex = Integer.toHexString(c);
                        String esc = "\\u" + "0000".substring(hex.length()) + hex;
                        out.write(esc.getBytes(StandardCharsets.UTF_8));
                    } else {
                        out.write(new String(new char[]{c}).getBytes(StandardCharsets.UTF_8));
                    }
            }
        }
        out.write('"');
    }

    private static final class Parser {
        private final String s;
        private int i = 0;

        Parser(String s) {
            this.s = s;
        }

        Object parseAny() {
            skipWs();
            Object v = parseValue();
            skipWs();
            if (i != s.length()) throw err("trailing data");
            return v;
        }

        private Object parseValue() {
            skipWs();
            if (i >= s.length()) throw err("eof");
            char c = s.charAt(i);
            if (c == '"') return parseString();
            if (c == '{') return parseObject();
            if (c == '[') return parseArray();
            if (c == 't') return literal("true", Boolean.TRUE);
            if (c == 'f') return literal("false", Boolean.FALSE);
            if (c == 'n') return literal("null", null);
            if (c == '-' || (c >= '0' && c <= '9')) return parseNumber();
            throw err("bad value");
        }

        private Object literal(String lit, Object val) {
            if (s.startsWith(lit, i)) {
                i += lit.length();
                return val;
            }
            throw err("bad literal");
        }

        private Map<String, Object> parseObject() {
            expect('{');
            skipWs();
            LinkedHashMap<String, Object> m = new LinkedHashMap<>();
            if (peek('}')) {
                i++;
                return m;
            }
            while (true) {
                skipWs();
                String k = parseString();
                skipWs();
                expect(':');
                Object v = parseValue();
                if (m.put(k, v) != null) throw err("dup key: " + k);
                skipWs();
                if (peek('}')) {
                    i++;
                    break;
                }
                expect(',');
            }
            return m;
        }

        private List<Object> parseArray() {
            expect('[');
            skipWs();
            ArrayList<Object> a = new ArrayList<>();
            if (peek(']')) {
                i++;
                return a;
            }
            while (true) {
                a.add(parseValue());
                skipWs();
                if (peek(']')) {
                    i++;
                    break;
                }
                expect(',');
            }
            return a;
        }

        private String parseString() {
            expect('"');
            StringBuilder sb = new StringBuilder();
            while (true) {
                if (i >= s.length()) throw err("eof in string");
                char c = s.charAt(i++);
                if (c == '"') break;
                if (c == '\\') {
                    if (i >= s.length()) throw err("eof in escape");
                    char e = s.charAt(i++);
                    switch (e) {
                        case '"':
                            sb.append('"');
                            break;
                        case '\\':
                            sb.append('\\');
                            break;
                        case '/':
                            sb.append('/');
                            break;
                        case 'b':
                            sb.append('\b');
                            break;
                        case 'f':
                            sb.append('\f');
                            break;
                        case 'n':
                            sb.append('\n');
                            break;
                        case 'r':
                            sb.append('\r');
                            break;
                        case 't':
                            sb.append('\t');
                            break;
                        case 'u':
                            if (i + 4 > s.length()) throw err("bad unicode escape");
                            int cp = Integer.parseInt(s.substring(i, i + 4), 16);
                            sb.append((char) cp);
                            i += 4;
                            break;
                        default:
                            throw err("bad escape");
                    }
                } else {
                    sb.append(c);
                }
            }
            return sb.toString();
        }

        private Number parseNumber() {
            int start = i;
            if (s.charAt(i) == '-') i++;
            if (i >= s.length()) throw err("bad number");
            char c = s.charAt(i);
            if (c == '0') {
                i++;
            } else if (c >= '1' && c <= '9') {
                i++;
                while (i < s.length()) {
                    char d = s.charAt(i);
                    if (d < '0' || d > '9') break;
                    i++;
                }
            } else throw err("bad number");

            if (i < s.length()) {
                char x = s.charAt(i);
                if (x == '.' || x == 'e' || x == 'E') throw err("non-integer number forbidden");
            }

            String num = s.substring(start, i);
            if (num.equals("-0")) throw err("negative zero forbidden");
            try {
                return Long.parseLong(num);
            } catch (NumberFormatException nfe) {
                throw err("integer out of range; encode as string: " + num);
            }
        }

        private void skipWs() {
            while (i < s.length()) {
                char c = s.charAt(i);
                if (c == ' ' || c == '\n' || c == '\r' || c == '\t') i++;
                else break;
            }
        }

        private void expect(char c) {
            if (i >= s.length() || s.charAt(i) != c) throw err("expected " + c);
            i++;
        }

        private boolean peek(char c) {
            return i < s.length() && s.charAt(i) == c;
        }

        private RuntimeException err(String msg) {
            return new IllegalArgumentException(msg + " @ " + i);
        }
    }
}
