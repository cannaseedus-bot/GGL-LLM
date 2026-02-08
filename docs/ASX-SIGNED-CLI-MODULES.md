# ASX Signed CLI Modules (Canonical)

## Goals (Invariant)

* Scripts are **immutable artifacts**
* Signatures are **verifiable offline**
* Shells **host only**
* Verification happens **before execution**
* Failure to verify = **hard stop**

---

## I. PowerShell (Signed Modules)

### I.1 Packaging

```
asx-decision/
├─ AsxDecision.psm1
├─ AsxDecision.psd1
├─ AsxDecision.ps1
├─ signatures/
│  └─ AsxDecision.ps1.sig
```

---

### I.2 Authenticode Signing

```powershell
$cert = Get-ChildItem Cert:\CurrentUser\My -CodeSigningCert |
        Select-Object -First 1

Set-AuthenticodeSignature `
  -FilePath .\AsxDecision.ps1 `
  -Certificate $cert `
  -TimestampServer http://timestamp.digicert.com
```

**Policy requirement (canonical):**

```powershell
Set-ExecutionPolicy AllSigned -Scope Process
```

---

### I.3 Verification Gate

```powershell
$sig = Get-AuthenticodeSignature .\AsxDecision.ps1

if ($sig.Status -ne 'Valid') {
  Write-Error "ILLEGAL: invalid signature"
  exit 1
}
```

Execution **must not proceed** unless status is `Valid`.

---

## II. Bash (Detached Signature, POSIX)

### II.1 Packaging

```
asx-decision/
├─ asx-decision.sh
├─ asx-decision.sh.sig
├─ asx.pub
```

---

### II.2 Signing (GPG)

```bash
gpg --armor --detach-sign asx-decision.sh
```

---

### II.3 Verification Gate

```bash
gpg --verify asx-decision.sh.sig asx-decision.sh
if [ $? -ne 0 ]; then
  echo "ILLEGAL: signature verification failed"
  exit 1
fi
```

Only after verification may the script be sourced or executed.

---

### II.4 Canonical Shebang

```bash
#!/usr/bin/env bash
set -euo pipefail
```

No dynamic sourcing. No eval.

---

## III. Batch (Windows CMD)

Batch cannot self-verify cryptographically, so **external verification is mandatory**.

### III.1 Packaging

```
asx-decision/
├─ asx-decision.bat
├─ asx-decision.bat.sig
├─ asx.pub
```

---

### III.2 Signing (GPG)

```bash
gpg --armor --detach-sign asx-decision.bat
```

---

### III.3 Verification Wrapper (PowerShell)

**`verify-and-run.ps1`**

```powershell
gpg --verify asx-decision.bat.sig asx-decision.bat
if ($LASTEXITCODE -ne 0) {
  Write-Error "ILLEGAL: signature verification failed"
  exit 1
}

cmd /c asx-decision.bat %*
```

**Law:** `.bat` files must never be executed directly.

---

## IV. Unified Signature Manifest (Optional but Canonical)

```json
{
  "artifact": "asx-decision",
  "version": "1.2",
  "hash": "blake3:…",
  "signed_by": "ASX Root Key",
  "algorithms": ["Authenticode", "Ed25519"],
  "timestamp": "2026-02-08T03:01:00Z"
}
```

This manifest itself may be signed and distributed.

---

## V. Key Management (Frozen Rules)

* **One root key per registry**
* Public keys are **append-only**
* Revocation requires **new version**
* Old artifacts remain verifiable forever

---

## VI. Execution Law (Hard)

| Condition         | Result  |
| ----------------- | ------- |
| Signature valid   | MAY run |
| Signature missing | ILLEGAL |
| Signature invalid | ILLEGAL |
| Modified file     | ILLEGAL |
| Unknown key       | ILLEGAL |

No warnings. No prompts. No overrides.

---

## VII. Cross-Shell UX (Consistent)

```text
ASX DECISION ENGINE CLI
Status: VERIFIED
Signature: VALID
Mode: READ-ONLY
Authority: NONE
```

Anything else is non-conformant.

---

## VIII. Why This Works

* PowerShell → native trust chain
* Bash → portable cryptographic proof
* Batch → wrapper-enforced verification
* CI → same signatures, same rules

> **Scripts are artifacts.
> Artifacts are law.
> Law must be signed.**

---

## Closure

You now have **fully signed**, **cross-platform**, **cryptographically enforced** CLI modules that:

* cannot drift
* cannot self-authorize
* cannot mutate law
* can be verified forever

If you want the final layer, the only lawful continuations are:

* offline mirror bundles
* key rotation + transparency anchoring
* notarized releases
* air-gapped verifier images
