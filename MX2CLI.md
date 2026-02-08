# MX2CLI

MX2CLI is a small wrapper around the `powershell/` Java CLI artifacts plus the PowerShell model JAR. It keeps the canonicalization runner (`Main` → `ConformanceRunner`) you already have and layers a model registry so you can swap in additional model JARs without rewriting scripts.

## Layout

* `mx2cli.sh` — entrypoint for building and running the Java CLI.
* `mx2cli-models.json` — model registry (default: `powershell`).
* `powershell/` — existing Java sources + dependency jars.

## Quickstart

```bash
# 1) Compile the Java CLI sources into powershell/.mx2cli/classes
./mx2cli.sh build

# 2) Run the canonicalization harness against a test vector directory
#    (requires input.json + hashes.json inside the directory).
./mx2cli.sh canon /path/to/test_vector_dir
```

The default model is `powershell`. If the `powershell/lib/powershell-1.0.9.jar` file is missing, MX2CLI will call `powershell/lib/fetch-powershell-lib.sh` automatically.

## Selecting models

Use `--model` to target a specific registered model:

```bash
./mx2cli.sh canon --model powershell /path/to/test_vector_dir
```

To see the registry:

```bash
./mx2cli.sh models
```

## Adding models

Extend `mx2cli-models.json` with new entries. Each model can declare:

```json
{
  "models": {
    "my-model": {
      "description": "What this model jar does",
      "classpath": [
        "path/to/model.jar",
        "extra/dependency/dir/*"
      ],
      "fetch": "optional fetch command to pull the jar",
      "main": "Java entrypoint (default: Main)"
    }
  }
}
```

The CLI automatically appends the compiled `powershell/.mx2cli/classes` directory to the classpath so you can re-use `Main`/`ConformanceRunner` with any registered model bundle.
