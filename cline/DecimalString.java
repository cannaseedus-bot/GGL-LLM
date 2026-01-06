import java.math.BigInteger;
import java.util.Objects;

/**
 * DecimalString — exact decimal parser/ops for MFA-1
 * - No float/double.
 * - No exponent.
 * - Decimal-as-string only.
 *
 * Grammar: [-] DIGITS [ "." DIGITS ]
 */
public final class DecimalString implements Comparable<DecimalString> {
    public final int sign;              // -1, 0, +1
    public final BigInteger unscaled;   // non-negative
    public final int scale;             // >= 0 (digits after decimal)

    private DecimalString(int sign, BigInteger unscaled, int scale) {
        if (scale < 0) throw new IllegalArgumentException("scale<0");
        if (unscaled.signum() < 0) throw new IllegalArgumentException("unscaled<0");
        if (unscaled.signum() == 0) {
            this.sign = 0;
            this.unscaled = BigInteger.ZERO;
            this.scale = 0; // canonical zero
        } else {
            this.sign = sign;
            this.unscaled = unscaled;
            this.scale = scale;
        }
    }

    public static DecimalString parse(String s) {
        if (s == null) throw new IllegalArgumentException("decimal null");
        s = s.trim();
        if (s.isEmpty()) throw new IllegalArgumentException("decimal empty");

        // forbid exponent
        for (int i = 0; i < s.length(); i++) {
            char c = s.charAt(i);
            if (c == 'e' || c == 'E') throw new IllegalArgumentException("exponent forbidden: " + s);
            if (c == '+') throw new IllegalArgumentException("plus sign forbidden: " + s);
        }

        int idx = 0;
        int sign = 1;
        if (s.charAt(0) == '-') {
            sign = -1;
            idx = 1;
        }
        if (idx >= s.length()) throw new IllegalArgumentException("decimal sign only: " + s);

        int dot = s.indexOf('.', idx);
        String intPart;
        String fracPart;
        if (dot < 0) {
            intPart = s.substring(idx);
            fracPart = "";
        } else {
            intPart = s.substring(idx, dot);
            fracPart = s.substring(dot + 1);
            if (fracPart.isEmpty()) throw new IllegalArgumentException("decimal trailing dot: " + s);
        }

        if (intPart.isEmpty()) throw new IllegalArgumentException("decimal missing int: " + s);
        if (!allDigits(intPart) || !allDigits(fracPart)) throw new IllegalArgumentException("decimal non-digit: " + s);

        int scale = fracPart.length();
        String combined = intPart + fracPart;

        int nz = 0;
        while (nz < combined.length() && combined.charAt(nz) == '0') nz++;
        if (nz == combined.length()) return new DecimalString(0, BigInteger.ZERO, 0);

        BigInteger unscaled = new BigInteger(combined.substring(nz));
        return normalize(new DecimalString(sign, unscaled, scale));
    }

    private static boolean allDigits(String s) {
        for (int i = 0; i < s.length(); i++) {
            char c = s.charAt(i);
            if (c < '0' || c > '9') return false;
        }
        return true;
    }

    /**
     * Normalize by removing trailing zeros in unscaled (i.e., reduce scale) without changing value.
     * This is critical so compare/add behave deterministically.
     */
    public static DecimalString normalize(DecimalString d) {
        if (d.sign == 0) return d;

        BigInteger u = d.unscaled;
        int sc = d.scale;

        BigInteger TEN = BigInteger.TEN;
        while (sc > 0) {
            BigInteger[] divRem = u.divideAndRemainder(TEN);
            if (divRem[1].signum() != 0) break;
            u = divRem[0];
            sc--;
        }
        return new DecimalString(d.sign, u, sc);
    }

    public DecimalString abs() {
        if (sign >= 0) return this;
        return new DecimalString(1, unscaled, scale);
    }

    @Override
    public int compareTo(DecimalString other) {
        Objects.requireNonNull(other, "other");
        if (this.sign != other.sign) return Integer.compare(this.sign, other.sign);
        if (this.sign == 0) return 0;

        int maxScale = Math.max(this.scale, other.scale);
        BigInteger a = this.unscaled.multiply(pow10(maxScale - this.scale));
        BigInteger b = other.unscaled.multiply(pow10(maxScale - other.scale));

        int cmp = a.compareTo(b);
        return this.sign > 0 ? cmp : -cmp;
    }

    public DecimalString add(DecimalString other) {
        Objects.requireNonNull(other, "other");
        if (this.sign == 0) return other;
        if (other.sign == 0) return this;

        int maxScale = Math.max(this.scale, other.scale);
        BigInteger a = this.unscaled.multiply(pow10(maxScale - this.scale));
        BigInteger b = other.unscaled.multiply(pow10(maxScale - other.scale));
        BigInteger sum = (this.sign > 0 ? a : a.negate()).add(other.sign > 0 ? b : b.negate());

        int sgn = sum.signum();
        if (sgn == 0) return new DecimalString(0, BigInteger.ZERO, 0);
        return normalize(new DecimalString(sgn, sum.abs(), maxScale));
    }

    public DecimalString sub(DecimalString other) {
        Objects.requireNonNull(other, "other");
        return this.add(new DecimalString(-other.sign, other.unscaled, other.scale));
    }

    public DecimalString mul(DecimalString other) {
        Objects.requireNonNull(other, "other");
        if (this.sign == 0 || other.sign == 0) return new DecimalString(0, BigInteger.ZERO, 0);
        int sgn = this.sign * other.sign;
        BigInteger prod = this.unscaled.multiply(other.unscaled);
        int sc = this.scale + other.scale;
        return normalize(new DecimalString(sgn, prod, sc));
    }

    private static BigInteger pow10(int n) {
        if (n < 0) throw new IllegalArgumentException("pow10 negative");
        if (n == 0) return BigInteger.ONE;
        BigInteger p = BigInteger.ONE;
        BigInteger ten = BigInteger.TEN;
        for (int i = 0; i < n; i++) p = p.multiply(ten);
        return p;
    }

    /**
     * Canonical decimal string:
     * - "0" for zero
     * - otherwise: optional "-" + digits + optional "." + digits (no trailing zeros in fractional)
     */
    public String toCanonicalString() {
        if (sign == 0) return "0";

        String digits = unscaled.toString();
        if (scale == 0) return (sign < 0 ? "-" : "") + digits;

        int len = digits.length();
        int intLen = len - scale;
        StringBuilder sb = new StringBuilder();
        if (sign < 0) sb.append('-');

        if (intLen <= 0) {
            sb.append('0').append('.');
            for (int i = 0; i < -intLen; i++) sb.append('0');
            sb.append(digits);
        } else {
            sb.append(digits, 0, intLen);
            sb.append('.');
            sb.append(digits.substring(intLen));
        }
        return sb.toString();
    }

    @Override
    public String toString() {
        return toCanonicalString();
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (!(o instanceof DecimalString)) return false;
        DecimalString d = (DecimalString) o;
        DecimalString a = normalize(this);
        DecimalString b = normalize(d);
        return a.sign == b.sign && a.scale == b.scale && a.unscaled.equals(b.unscaled);
    }

    @Override
    public int hashCode() {
        DecimalString a = normalize(this);
        return Objects.hash(a.sign, a.unscaled, a.scale);
    }
}
