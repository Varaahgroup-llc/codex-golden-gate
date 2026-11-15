#!/usr/bin/env python3
"""Package standalone source and a dependency-free plugin release."""
import argparse
import hashlib
import json
from pathlib import Path
from pathlib import PurePosixPath
import re
import zipfile

def excluded(path):
    return any(p in {'node_modules', '.git', '__pycache__', 'release'} for p in path.parts) or path.name.startswith(('.env', '.dev.vars')) or path.suffix in {'.log', '.zip', '.pyc'} or path.name in {'.DS_Store', 'preview.png'}

PUBLIC_DOCS = ['README.md', 'INSTALL.md', 'SECURITY.md', 'PRIVACY.md', 'PUBLISHING.md', 'CHANGELOG.md', 'MAINTAINING.md', 'CONTRIBUTING.md', 'VALIDATION.md', 'LICENSE',
               'docs/TRACKING.md', 'docs/approval/SUPPORT_STATUS.md', 'docs/approval/REVIEW_PLAN.md', 'docs/approval/readiness.json', 'docs/approval/SECURITY_PREPARATION.md']

def approved_files(root):
    """Only reviewed catalog entries may leave the working directory."""
    names = json.loads((root / 'scripts/package-files.json').read_text())['source']
    if not isinstance(names, list) or not names or not all(isinstance(n, str) for n in names) or len(set(names)) != len(names):
        raise ValueError('Invalid public package file catalog.')
    files = []
    for name in sorted(names):
        rel = PurePosixPath(name)
        if rel.is_absolute() or '..' in rel.parts or str(rel) != name or '\\' in name or excluded(rel):
            raise ValueError('Unsafe public package catalog entry.')
        file = root / name
        if any(p.is_symlink() for p in [file, *file.parents] if p != root and root in p.parents):
            raise ValueError('Public package entries must not traverse symlinks.')
        if not file.is_file():
            raise ValueError('A required public package file is missing.')
        files.append((file, name))
    return files

def package(root, output):
    root = root.resolve()
    files = approved_files(root)  # Validate before creating any output.
    version = json.loads((root / 'plugins/secret-bridge/plugin.json').read_text())['version']
    # A manifest version also becomes an output filename.
    if not re.fullmatch(r'\d+\.\d+\.\d+(?:-[0-9A-Za-z.-]+)?', version):
        raise ValueError('Invalid package version.')
    names = {name for _, name in files}
    if not set(PUBLIC_DOCS + ['plugins/secret-bridge/dist/server.mjs', 'plugins/secret-bridge/dist/THIRD_PARTY_LICENSES.txt', 'plugins/secret-bridge/plugin.json', 'plugins/secret-bridge/mcp.json', 'plugins/secret-bridge/skills/save-secret/SKILL.md']).issubset(names):
        raise ValueError('Public package catalog omits required release files.')
    output.mkdir(parents=True, exist_ok=True)
    source = output / f'secret-bridge-{version}-source.zip'
    release = output / f'secret-bridge-{version}-plugin.zip'
    with zipfile.ZipFile(source, 'w', zipfile.ZIP_DEFLATED) as archive:
        for file, name in files:
            archive.write(file, f'codex-secret-bridge/{name}')
    with zipfile.ZipFile(release, 'w', zipfile.ZIP_DEFLATED) as archive:
        for file, name in files:
            rel = PurePosixPath(name)
            if name in PUBLIC_DOCS:
                archive.write(file, name)
            elif rel.parts[:2] == ('plugins', 'secret-bridge'):
                plugin_rel = PurePosixPath(*rel.parts[2:])
                if plugin_rel.parts[0] in {'dist', 'skills'} or str(plugin_rel) in {'plugin.json', 'mcp.json'}:
                    archive.write(file, str(plugin_rel))
    checksums = output / 'SHA256SUMS.txt'
    checksums.write_text(''.join(f'{hashlib.sha256(file.read_bytes()).hexdigest()}  {file.name}\n' for file in [source, release]))
    return source, release, checksums

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    try:
        artifacts = package(Path(__file__).resolve().parents[1], args.output)
    except (ValueError, KeyError, OSError) as err:
        raise SystemExit(str(err))
    print('Created ' + ', '.join(file.name for file in artifacts))
