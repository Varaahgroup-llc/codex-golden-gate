"""Exercise two reviewed marketplace archives in an isolated, credential-free Codex CLI profile."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import stat
import subprocess
import tempfile
import zipfile

MARKET = 'varaahgroup-golden-gate'
PLUGIN = 'golden-gate@' + MARKET


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def unpack(path, checksum, target):
    if digest(path) != checksum:
        raise ValueError('Source ZIP differs from its reviewed SHA-256')
    with zipfile.ZipFile(path) as archive:
        seen = set()
        for entry in archive.infolist():
            parts = Path(entry.filename).parts
            if (not parts or parts[0] != 'codex-golden-gate' or '..' in parts
                    or '\\' in entry.filename or stat.S_ISLNK(entry.external_attr >> 16)
                    or entry.filename in seen):
                raise ValueError('Unsafe marketplace archive')
            seen.add(entry.filename)
        archive.extractall(target)
    return target / 'codex-golden-gate'


def smoke(server):
    # Exercise stdio discovery from the installed cache without opening a form.
    messages = [
        {'id': 1, 'method': 'initialize', 'params': {'protocolVersion': '2025-03-26',
         'capabilities': {}, 'clientInfo': {'name': 'gg-recovery', 'version': '1'}}},
        {'method': 'notifications/initialized'},
        {'id': 2, 'method': 'tools/list', 'params': {}},
    ]
    payload = ''.join(json.dumps({'jsonrpc': '2.0', **m}) + '\n' for m in messages)
    result = subprocess.run(['node', server], input=payload, text=True, capture_output=True,
                            cwd=server.parent, check=True, timeout=30,
                            env={'PATH': os.environ['PATH']})
    replies = {r['id']: r['result'] for r in map(json.loads, result.stdout.splitlines())}
    names = sorted(tool['name'] for tool in replies[2]['tools'])
    if not {'open_secret_entry', 'secret_entry_status', 'submit_secret'}.issubset(names):
        raise ValueError('Required tools missing from installed bundle')
    return replies[1]['serverInfo']['version'], names


def rehearse(directory, prior, current):
    profile = directory / 'profile'
    profile.mkdir(mode=0o700)
    env = {'PATH': os.environ['PATH'], 'HOME': str(directory), 'CODEX_HOME': str(profile),
           'TMPDIR': str(directory)}
    def cli(*args):
        result = subprocess.run(['codex', 'plugin', *args, '--json'], env=env, cwd=directory,
                                capture_output=True, text=True, timeout=60)
        if result.returncode:
            raise RuntimeError('Codex CLI failed at ' + ' '.join(args[:2]))
        return json.loads(result.stdout)

    sentinel = directory / '.env.local'
    sentinel.write_text('GG_TEST=synthetic-recovery-fixture\n')
    before = digest(sentinel)
    results = []
    for stage, source in [('baseline', prior), ('candidate', current), ('rollback', prior)]:
        if results:
            cli('remove', PLUGIN)
            cli('marketplace', 'remove', MARKET)
        cli('marketplace', 'add', str(source))
        installation = cli('add', PLUGIN)
        listing = cli('list', '--marketplace', MARKET)
        entries = listing['installed']
        if not any(p.get('pluginId') == PLUGIN and p.get('installed') is True and p.get('enabled') is True for p in entries):
            raise ValueError('Codex did not report an enabled installation')
        plugin = source / 'plugins/golden-gate'
        version = json.loads((plugin / 'plugin.json').read_text())['version']
        cached = Path(installation['installedPath']).resolve() / 'dist/server.mjs'
        if not cached.is_relative_to(profile.resolve()) or installation['version'] != version:
            raise ValueError('Unexpected installation path or version')
        if digest(cached) != digest(plugin / 'dist/server.mjs'):
            raise ValueError('Installed bundle differs from archive')
        running_version, names = smoke(cached)
        if running_version != version or digest(sentinel) != before:
            raise ValueError('Installed version or synthetic destination integrity failed')
        results.append({'stage': stage, 'version': version, 'serverSHA256': digest(cached),
                        'enabled': True, 'tools': names, 'destinationPreserved': True})
    if results[0]['version'] == results[1]['version']:
        raise ValueError('Recovery needs two different versions')
    return results


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    for label in ('previous', 'candidate'):
        parser.add_argument('--' + label, required=True, type=Path)
        parser.add_argument('--' + label + '-sha256', required=True)
    args = parser.parse_args()
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp)
        prior = unpack(args.previous, args.previous_sha256, root / 'previous')
        current = unpack(args.candidate, args.candidate_sha256, root / 'candidate')
        results = rehearse(root, prior, current)
    print(json.dumps({'codex': subprocess.check_output(['codex', '--version'], text=True).strip(),
                      'sourceArchives': {'previous': args.previous_sha256, 'candidate': args.candidate_sha256},
                      'results': results, 'desktopUAT': 'NOT_RUN', 'liveProviders': 'NOT_RUN'}, indent=2))
