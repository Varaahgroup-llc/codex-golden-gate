#!/usr/bin/env bash
# Install a checksum-pinned scanner into a job-specific temporary directory.
set -euo pipefail
case "$(uname -s)-$(uname -m)" in
  Linux-x86_64) platform=linux_x64; digest=a65b5253807a68ac0cafa4414031fd740aeb55f54fb7e55f386acb52e6a840eb ;;
  Darwin-arm64) platform=darwin_arm64; digest=d942f3ad147250c9edbaab3fed9e482f98d3b59ba10ae97b8d75647e3ade492c ;;
  Darwin-x86_64) platform=darwin_x64; digest=edf5a507008b0d2ef4959575772772770586409c1f6f74dabf19cbe7ec341ced ;;
  *) echo 'Unsupported scanner platform' >&2; exit 1 ;;
esac
work=$(mktemp -d)
asset="gitleaks_8.28.0_${platform}.tar.gz"
curl -fsSL --retry 3 "https://github.com/gitleaks/gitleaks/releases/download/v8.28.0/$asset" -o "$work/scanner.tar.gz"
(cd "$work" && echo "$digest  scanner.tar.gz" | shasum -a 256 -c - && tar xzf scanner.tar.gz gitleaks)
echo "GG_GITLEAKS=$work/gitleaks" >> "${GITHUB_ENV:?Missing environment output file}"
