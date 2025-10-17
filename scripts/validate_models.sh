#!/usr/bin/env bash
set -euo pipefail

SCHEMA_PATH="./.schema/threat-dragon-schema.json"

if [ ! -f "${SCHEMA_PATH}" ]; then
  echo "Error: Threat Dragon schema not found at ${SCHEMA_PATH}"
  echo "Make sure the .schema folder exists and contains threat-dragon-schema.json"
  exit 1
fi

echo "Validating threat models against local schema..."
shopt -s globstar || true
files=( threat-models/**/*.json threat-models/*.json )
valid=true

for f in "${files[@]}"; do
  if [ -f "$f" ]; then
    echo "Validating $f ..."
    npx ajv validate -s "${SCHEMA_PATH}" -d "$f" || valid=false
  fi
done

if [ "${valid}" = false ]; then
  echo "❌ One or more models failed validation."
  exit 2
fi

echo "✅ All threat models validated successfully."
