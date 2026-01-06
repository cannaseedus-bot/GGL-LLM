import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.Map;

public final class ConformanceRunner {

    public static void main(String[] args) throws Exception {
        if (args.length != 1) {
            System.err.println("Usage: java ConformanceRunner <test_vector_dir>");
            System.exit(2);
        }
        run(args[0]);
    }

    public static void run(String dirPath) throws IOException {
        Path dir = Paths.get(dirPath);
        Path input = dir.resolve("input.json");
        Path hashes = dir.resolve("hashes.json");
        Path canonOut = dir.resolve("canon.json");

        byte[] inputBytes = Files.readAllBytes(input);
        Object parsed = CanonJson.parse(inputBytes);
        byte[] canonBytes = CanonJson.canonicalize(parsed);

        Files.write(canonOut, canonBytes);

        String got256 = Sha.sha256Hex(canonBytes);
        String got512 = Sha.sha512Hex(canonBytes);

        Object hParsed = CanonJson.parse(Files.readAllBytes(hashes));
        if (!(hParsed instanceof Map)) fail("hashes.json must be object");
        @SuppressWarnings("unchecked")
        Map<String, Object> hm = (Map<String, Object>) hParsed;

        String exp256 = stringField(hm, "sha256");
        String exp512 = stringField(hm, "sha512");

        boolean ok = true;
        if (!got256.equalsIgnoreCase(exp256)) {
            ok = false;
            System.err.println("FAIL sha256");
            System.err.println(" expected: " + exp256);
            System.err.println(" got     : " + got256);
        }
        if (!got512.equalsIgnoreCase(exp512)) {
            ok = false;
            System.err.println("FAIL sha512");
            System.err.println(" expected: " + exp512);
            System.err.println(" got     : " + got512);
        }

        if (!ok) System.exit(1);

        System.out.println("OK");
        System.out.println("canon.json bytes: " + canonBytes.length);
        System.out.println("sha256: " + got256);
        System.out.println("sha512: " + got512);
    }

    private static String stringField(Map<String, Object> m, String k) {
        Object v = m.get(k);
        if (!(v instanceof String)) fail("hashes.json field must be string: " + k);
        return (String) v;
    }

    private static void fail(String msg) {
        throw new IllegalArgumentException(msg);
    }
}
