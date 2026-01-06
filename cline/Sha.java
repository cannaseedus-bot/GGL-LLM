import java.security.MessageDigest;
import java.util.HexFormat;

public final class Sha {
    private static final HexFormat HEX = HexFormat.of();

    public static String sha256Hex(byte[] data) {
        return hex(digest("SHA-256", data));
    }

    public static String sha512Hex(byte[] data) {
        return hex(digest("SHA-512", data));
    }

    private static byte[] digest(String alg, byte[] data) {
        try {
            MessageDigest md = MessageDigest.getInstance(alg);
            return md.digest(data);
        } catch (Exception e) {
            throw new RuntimeException(e);
        }
    }

    private static String hex(byte[] b) {
        return HEX.formatHex(b);
    }
}
