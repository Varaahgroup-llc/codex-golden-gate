#!/usr/bin/env python3
"""Check release identity, versions and required runtime files."""
import argparse
import json
from pathlib import Path
import re
parser = argparse.ArgumentParser()
parser.add_argument('--tag')
args = parser.parse_args()
root = Path(__file__).resolve().parents[1]
plugin = root / 'plugins/secret-bridge'
manifest = json.loads((plugin / 'plugin.json').read_text())
package = json.loads((plugin / 'package.json').read_text())
lock = json.loads((plugin / 'package-lock.json').read_text())
version = manifest['version']
assert re.fullmatch(r'\d+\.\d+\.\d+(?:-[0-9A-Za-z.-]+)?', version), 'Invalid version'
assert package['version'] == lock['version'] == lock['packages']['']['version'] == version, 'Versions differ'
assert manifest['repository'] == 'https://github.com/Varaahgroup-llc/codex-secret-bridge'
assert not args.tag or args.tag == f'v{version}', 'Tag and plugin version differ'
marketplace = json.loads((root / '.agents/plugins/marketplace.json').read_text())
assert marketplace['name'] == 'varaahgroup-secret-bridge'
assert marketplace['plugins'][0]['source']['path'] == './plugins/secret-bridge'
mcp = json.loads((plugin / 'mcp.json').read_text())['mcpServers']['secret-bridge']
assert mcp['type'] == 'stdio' and mcp['args'] == ['${PLUGIN_ROOT}/dist/server.mjs']
for file in ['dist/server.mjs', 'dist/THIRD_PARTY_LICENSES.txt', 'skills/save-secret/SKILL.md']:
    assert (plugin / file).is_file(), f'Missing runtime file: {file}'
for file in ['LICENSE', 'PRIVACY.md', 'SECURITY.md', 'CONTRIBUTING.md', 'MAINTAINING.md', 'CHANGELOG.md']:
    assert (root / file).is_file(), f'Missing project file: {file}'
print(f'Release metadata and runtime files validated for v{version}')
