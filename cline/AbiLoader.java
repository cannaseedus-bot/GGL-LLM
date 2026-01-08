import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;

public final class AbiLoader {
    public final String abiHashHex;
    public final Object tokenizerAbi;
    public final Object grammarAbi;

    private AbiLoader(String abiHashHex, Object tokenizerAbi, Object grammarAbi) {
        this.abiHashHex = abiHashHex;
        this.tokenizerAbi = tokenizerAbi;
        this.grammarAbi = grammarAbi;
    }

    public static AbiLoader load(Path tokPath, Path grPath) throws Exception {
        byte[] tokRaw = Files.readAllBytes(tokPath);
        byte[] grRaw = Files.readAllBytes(grPath);

        Object tokObj = CanonJson.parse(tokRaw);
        Object grObj = CanonJson.parse(grRaw);

        byte[] tokCanon = CanonJson.canonicalize(tokObj);
        byte[] grCanon = CanonJson.canonicalize(grObj);

        byte[] joined = new byte[tokCanon.length + 1 + grCanon.length];
        System.arraycopy(tokCanon, 0, joined, 0, tokCanon.length);
        joined[tokCanon.length] = (byte) 0x0A;
        System.arraycopy(grCanon, 0, joined, tokCanon.length + 1, grCanon.length);

        String h = Sha.sha256Hex(joined);
        return new AbiLoader(h, tokObj, grObj);
    }
}
