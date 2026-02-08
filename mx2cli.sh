#!/usr/bin/env bash
# MX2CLI – wrapper around the PowerShell Java CLI + model jars with pluggable model slots.
# Uses the existing `powershell/` sources (Main.java/ConformanceRunner.java/etc.) and lets
# you register additional models via mx2cli-models.json.

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SRC_DIR="${ROOT}/powershell"
CLASS_DIR="${SRC_DIR}/.mx2cli/classes"
MODELS_JSON="${ROOT}/mx2cli-models.json"

usage() {
  cat <<'EOF'
MX2CLI
  build                 Compile the powershell Java CLI sources into .mx2cli/classes
  canon [--model NAME] <test_vector_dir>
                        Run ConformanceRunner against a test vector directory
                        (input.json + hashes.json). Defaults to --model powershell.
  models                List registered models from mx2cli-models.json
EOF
}

require_models_file() {
  if [[ ! -f "${MODELS_JSON}" ]]; then
    echo "Missing ${MODELS_JSON}. Add a model entry (see MX2CLI.md)." >&2
    exit 1
  fi
}

ensure_classes() {
  mkdir -p "${CLASS_DIR}"
  # Rebuild if classes are missing or sources are newer.
  local rebuild=false
  if [[ -z "$(find "${CLASS_DIR}" -type f -name '*.class' -print -quit)" ]]; then
    rebuild=true
  else
    if find "${SRC_DIR}" -maxdepth 1 -name '*.java' -newer "${CLASS_DIR}" -print -quit | grep -q .; then
      rebuild=true
    fi
  fi

  if [[ "${rebuild}" == true ]]; then
    echo "Compiling PowerShell Java CLI sources into ${CLASS_DIR}..."
    javac -d "${CLASS_DIR}" "${SRC_DIR}"/*.java
  fi
}

read_model_json() {
  local model="$1"
  python - "$MODELS_JSON" "$model" <<'PY'
import json, os, sys
path, model = sys.argv[1], sys.argv[2]
data = json.load(open(path, "r", encoding="utf-8"))
models = data.get("models", {})
m = models.get(model)
if not m:
    print(f"ERROR: unknown model '{model}'", file=sys.stderr)
    sys.exit(2)

def expand(p):
    return os.path.expandvars(os.path.expanduser(p))

cp = [expand(p) for p in m.get("classpath", [])]
main = m.get("main", "Main")
fetch = m.get("fetch", "")
print(json.dumps({"classpath": cp, "main": main, "fetch": fetch}))
PY
}

ensure_model_assets() {
  local model="$1"
  local info_json
  info_json="$(read_model_json "${model}")" || exit $?

  local fetch main classpath
  fetch="$(python - <<PY
import json,sys
info=json.loads('''${info_json}''')
print(info.get("fetch",""))
PY
)"
  classpath=()
  while IFS= read -r entry; do
    [[ -z "${entry}" ]] && continue
    classpath+=("${entry}")
  done < <(python - <<PY
import json
info=json.loads('''${info_json}''')
for entry in info.get("classpath", []):
    print(entry)
PY
)

  local missing=0
  for cp_entry in "${classpath[@]}"; do
    # Skip wildcard entries; they are handled by the JVM.
    if [[ "${cp_entry}" == *"*"* ]]; then
      continue
    fi
    if [[ ! -e "${cp_entry}" ]]; then
      missing=1
      break
    fi
  done

  if [[ "${missing}" -eq 1 && -n "${fetch}" ]]; then
    echo "Model assets missing for '${model}'. Running fetch script: ${fetch}"
    (cd "${ROOT}" && bash -c "${fetch}")
  fi

  echo "${info_json}"
}

build_classpath() {
  local model="$1"
  local info_json
  info_json="$(ensure_model_assets "${model}")"
  local cp_entries
  cp_entries="$(python - <<PY
import json
info=json.loads('''${info_json}''')
print(":".join(info.get("classpath", [])))
PY
)"
  if [[ -n "${cp_entries}" ]]; then
    echo "${CLASS_DIR}:${cp_entries}"
  else
    echo "${CLASS_DIR}"
  fi
}

model_main_class() {
  local info_json="$1"
  python - <<PY
import json
info=json.loads('''${info_json}''')
print(info.get("main", "Main"))
PY
}

cmd_build() {
  ensure_classes
  echo "Done."
}

cmd_models() {
  require_models_file
  python - "$MODELS_JSON" <<'PY'
import json, sys
data = json.load(open(sys.argv[1], "r", encoding="utf-8"))
models = data.get("models", {})
if not models:
    print("No models registered.")
    sys.exit(0)
for name, info in models.items():
    desc = info.get("description", "")
    cp = info.get("classpath", [])
    fetch = info.get("fetch")
    main = info.get("main", "Main")
    print(f"{name}")
    if desc:
        print(f"  desc : {desc}")
    if cp:
        print(f"  cp   : {', '.join(cp)}")
    print(f"  main : {main}")
    if fetch:
        print(f"  fetch: {fetch}")
PY
}

cmd_canon() {
  require_models_file
  ensure_classes

  local model="powershell"
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --model)
        model="$2"; shift 2;;
      --help|-h)
        usage; exit 0;;
      --)
        shift; break;;
      *)
        break;;
    esac
  done

  if [[ $# -lt 1 ]]; then
    echo "Usage: $0 canon [--model NAME] <test_vector_dir>" >&2
    exit 2
  fi
  local dir="$1"
  if [[ ! -d "${dir}" ]]; then
    echo "Test vector dir not found: ${dir}" >&2
    exit 1
  fi

  local info_json
  info_json="$(ensure_model_assets "${model}")"
  local cp
  cp="$(build_classpath "${model}")"
  local main_class
  main_class="$(model_main_class "${info_json}")"

  echo "Running ${main_class} with model '${model}'..."
  java -cp "${cp}" "${main_class}" "${dir}"
}

if [[ $# -lt 1 ]]; then
  usage
  exit 0
fi

case "$1" in
  build) shift; cmd_build "$@";;
  canon) shift; cmd_canon "$@";;
  models) shift; cmd_models "$@";;
  *) usage; exit 1;;
esac
