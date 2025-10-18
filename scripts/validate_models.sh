# ...existing code...
#!/usr/bin/env bash
set -euo pipefail

SCHEMA_PATH="./.schema/threat-dragon-schema.json"

if [ ! -f "${SCHEMA_PATH}" ]; then
  echo "Error: Threat Dragon schema not found at ${SCHEMA_PATH}"
  echo "Make sure the .schema folder exists and contains threat-dragon-schema.json"
  exit 1
fi

echo "Validating threat models against local schema..."

# Use globstar only on Bash 4+. Fallback to find + while-read for older bash (macOS bash 3.x).
files=()
if [ -n "${BASH_VERSINFO:-}" ] && [ "${BASH_VERSINFO[0]}" -ge 4 ]; then
  shopt -s globstar nullglob 2>/dev/null || true
  files=( threat-models/**/*.json threat-models/*.json )
else
  # Collect files using find; use NUL-separated output to handle spaces/newlines safely.
  while IFS= read -r -d '' f; do
    files+=("$f")
  done < <(find threat-models -type f -name '*.json' -print0 2>/dev/null || true)
fi

if [ "${#files[@]}" -eq 0 ]; then
  echo "No threat-model JSON files found in threat-models/"
  exit 0
fi

valid=true

for f in "${files[@]}"; do
  if [ -f "$f" ]; then
    echo "Validating $f ..."
    if ! npx ajv validate -s "${SCHEMA_PATH}" -d "$f"; then
      valid=false
    fi
  fi
done

if [ "${valid}" = false ]; then
  echo "❌ One or more models failed validation."
  exit 2
fi

echo "✅ All threat models validated successfully."
# ...existing code...