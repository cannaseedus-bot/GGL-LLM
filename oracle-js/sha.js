import { createHash } from "crypto";

export function sha256Hex(data) {
  const hash = createHash("sha256");
  hash.update(data);
  return hash.digest("hex");
}
