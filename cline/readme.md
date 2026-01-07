## MX2CLI (Cline Java CLI + model registry)

`MX2CLI` wraps the Cline Java conformance runner and adds a small model registry so you can swap the CLINE model for other builds without changing code.

### Build/Run

```bash
# From repo root
javac -d out cline/*.java
java -cp out MX2CLI help
```

### Canonicalization / conformance check

```bash
java -cp out MX2CLI canon ./path/to/test_vectors --model cline
```

If `--model` is omitted, the default registry entry is used. `canon` runs the existing `ConformanceRunner` to generate `canon.json` and validate hashes.

### Model registry commands

```bash
java -cp out MX2CLI models list
java -cp out MX2CLI models add qwen ./models/qwen "Qwen-based MX2 build"
java -cp out MX2CLI models default qwen
```

The registry is stored at `~/.mx2cli/models.json` using canonical JSON. A `cline` entry is pre-seeded with the repository `cline/` path; update it to your actual weights or swap in other models.
