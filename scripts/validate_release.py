#!/usr/bin/env python3
"""Check release identity, versions and required runtime files."""
import argparse
import json
from pathlib import Path
import re
import struct
parser = argparse.ArgumentParser()
parser.add_argument('--tag')
args = parser.parse_args()
root = Path(__file__).resolve().parents[1]
plugin = root / 'plugins/golden-gate'
manifest = json.loads((plugin / 'plugin.json').read_text())
package = json.loads((plugin / 'package.json').read_text())
lock = json.loads((plugin / 'package-lock.json').read_text())
version = manifest['version']
assert re.fullmatch(r'\d+\.\d+\.\d+(?:-[0-9A-Za-z.-]+)?', version), 'Invalid version'
assert package['version'] == lock['version'] == lock['packages']['']['version'] == version, 'Versions differ'
assert manifest['repository'] == 'https://github.com/Varaahgroup-llc/codex-golden-gate'
assert not args.tag or args.tag == f'v{version}', 'Tag and plugin version differ'
marketplace = json.loads((root / '.agents/plugins/marketplace.json').read_text())
assert marketplace['name'] == 'varaahgroup-golden-gate'
assert marketplace['plugins'][0]['source']['path'] == './plugins/golden-gate'
mcp = json.loads((plugin / 'mcp.json').read_text())['mcpServers']['golden-gate']
assert mcp['type'] == 'stdio' and mcp['args'] == ['${PLUGIN_ROOT}/dist/server.mjs']
for file in ['dist/server.mjs', 'dist/THIRD_PARTY_LICENSES.txt', 'skills/save-secret/SKILL.md']:
    assert (plugin / file).is_file(), f'Missing runtime file: {file}'
for file in ['LICENSE', 'PRIVACY.md', 'SECURITY.md', 'CONTRIBUTING.md', 'MAINTAINING.md', 'CHANGELOG.md']:
    assert (root / file).is_file(), f'Missing project file: {file}'
interface = manifest['extensions']['com.openai']['interface']
for field, minimum in [('logo', 256), ('composerIcon', 48), ('composerIconDark', 48)]:
    value = interface.get(field)
    if field.endswith('Dark') and value is None:
        continue
    assert isinstance(value, str) and value.startswith('./'), f'Missing contained icon path: {field}'
    icon = plugin / value
    assert icon.resolve().is_relative_to(plugin.resolve()) and icon.is_file(), f'Missing or unsafe icon: {field}'
    data = icon.read_bytes()
    assert len(data) <= 5 * 1024 * 1024 and data[:8] == b'\x89PNG\r\n\x1a\n' and data[12:16] == b'IHDR', f'Expected a small PNG: {field}'
    width, height = struct.unpack('>II', data[16:24])
    assert width == height and minimum <= width <= 4096, f'Invalid icon dimensions: {field}'
print(f'Release metadata and runtime files validated for v{version}')
