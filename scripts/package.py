#!/usr/bin/env python3
"""Package standalone source and a dependency-free plugin release."""
import argparse
import hashlib
import json
from pathlib import Path
import zipfile

root = Path(__file__).resolve().parents[1]
plugin = root / 'plugins' / 'secret-bridge'
parser = argparse.ArgumentParser()
parser.add_argument('--output', required=True, type=Path)
args = parser.parse_args()
args.output.mkdir(parents=True, exist_ok=True)
version = json.loads((plugin / 'plugin.json').read_text())['version']
if not (plugin / 'dist/server.mjs').is_file():
    raise SystemExit('Build the server before packaging.')

def excluded(path):
    return any(p in {'node_modules', '.git', '__pycache__', 'release'} for p in path.parts) or path.name.startswith(('.env', '.dev.vars')) or path.suffix in {'.log', '.zip', '.pyc'} or path.name in {'.DS_Store', 'preview.png'}

source = args.output / f'secret-bridge-{version}-source.zip'
with zipfile.ZipFile(source, 'w', zipfile.ZIP_DEFLATED) as archive:
    for file in sorted(root.rglob('*')):
        if file.is_file() and not file.is_symlink() and not excluded(file.relative_to(root)):
            archive.write(file, Path('codex-secret-bridge') / file.relative_to(root))

release = args.output / f'secret-bridge-{version}-plugin.zip'
with zipfile.ZipFile(release, 'w', zipfile.ZIP_DEFLATED) as archive:
    for file in sorted(plugin.rglob('*')):
        rel = file.relative_to(plugin)
        if file.is_file() and not file.is_symlink() and not excluded(rel) and (rel.parts[0] in {'dist', 'skills'} or rel.name in {'plugin.json', 'mcp.json'}):
            archive.write(file, rel)
    for name in ['README.md', 'INSTALL.md', 'SECURITY.md', 'PRIVACY.md', 'PUBLISHING.md', 'CHANGELOG.md', 'MAINTAINING.md', 'CONTRIBUTING.md', 'VALIDATION.md', 'LICENSE']:
        archive.write(root / name, name)
    # Include only explicitly public preparation records, never private support/account evidence.
    for name in ['docs/TRACKING.md', 'docs/approval/SUPPORT_STATUS.md', 'docs/approval/REVIEW_PLAN.md', 'docs/approval/readiness.json']:
        if (root / name).is_file():
            archive.write(root / name, name)

checksums = args.output / 'SHA256SUMS.txt'
checksums.write_text(''.join(f'{hashlib.sha256(file.read_bytes()).hexdigest()}  {file.name}\n' for file in [source, release]))
print(f'Created {source.name}, {release.name}, and {checksums.name}')
