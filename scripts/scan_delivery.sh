#!/usr/bin/env bash
set -euo pipefail
target=${1:?Pass the evidence or release directory}
[[ -d "$target" ]]
# Avoid printing even redacted excerpts or filenames from a rejected artifact.
if ! "${GG_GITLEAKS:?Install the pinned scanner first}" dir --no-banner --redact=100 --ignore-gitleaks-allow \
     --max-archive-depth=3 "$target" > /dev/null 2>&1; then
  echo 'Artifact secret scan failed. Inspect the files privately before any upload.' >&2
  exit 1
fi
echo 'Artifact secret scan passed (Gitleaks 8.28.0).'
