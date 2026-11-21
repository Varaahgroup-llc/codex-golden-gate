#!/usr/bin/env bash
# Linux x64 GitHub runner. Never install into the user's system.
set -euo pipefail
dir="$(mktemp -d)"
file=gitleaks_8.24.3_linux_x64.tar.gz
curl --fail --silent --show-error --location --retry 3 "https://github.com/gitleaks/gitleaks/releases/download/v8.24.3/$file" -o "$dir/$file"
(cd "$dir" && echo "9991e0b2903da4c8f6122b5c3186448b927a5da4deef1fe45271c3793f4ee29c  $file" | sha256sum -c - && tar xzf "$file" gitleaks)
echo "GG_GITLEAKS=$dir/gitleaks" >> "$GITHUB_ENV"
