#!/usr/bin/env python3
"""Set one release version across the plugin and npm metadata."""
import argparse
import json
from pathlib import Path
import re
from release_policy import VERSION
parser = argparse.ArgumentParser()
parser.add_argument('version')
args = parser.parse_args()
if not re.fullmatch(VERSION, args.version):
    raise SystemExit('Use a semantic version such as 0.1.1 or 0.2.0-beta.1.')
plugin = Path(__file__).resolve().parents[1] / 'plugins/golden-gate'
for name in ['plugin.json', 'package.json', 'package-lock.json']:
    file = plugin / name
    data = json.loads(file.read_text())
    data['version'] = args.version
    if name == 'package-lock.json':
        data['packages']['']['version'] = args.version
    file.write_text(json.dumps(data, indent=2, ensure_ascii=False) + '\n')
print(f'Version set to {args.version}. Update the changelog, rebuild and test before committing.')
