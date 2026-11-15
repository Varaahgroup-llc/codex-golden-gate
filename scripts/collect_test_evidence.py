#!/usr/bin/env python3
"""Run synthetic-data suites and retain bounded, hash-verifiable evidence. No UAT claim."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import platform
import subprocess
import sys
import time


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    plugin = root / 'plugins/golden-gate'
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    if any(output.iterdir()):
        raise SystemExit('Use an empty evidence directory to avoid mixing runs.')
    def git(*args):
        return subprocess.check_output(['git', *args], cwd=root, text=True).strip()
    commit = git('rev-parse', 'HEAD')
    diff = subprocess.check_output(['git', 'diff', 'HEAD', '--'], cwd=root)
    untracked = git('ls-files', '--others', '--exclude-standard').splitlines()
    # Exact approved-file hashes identify dirty source too, without publishing diff contents.
    names = json.loads((root / 'scripts/package-files.json').read_text())['source']
    source_hashes = {name: hashlib.sha256((root / name).read_bytes()).hexdigest() for name in sorted(names)}
    commands = [
        ('build', ['npm', 'run', 'build'], plugin, {0}),
        ('bundle', ['git', 'diff', '--exit-code', '--', 'plugins/golden-gate/dist'], root, {0}),
        ('node', ['node', '--test', '--test-reporter=junit', 'test/core.test.mjs', 'test/adapters.test.mjs', 'test/protocol.test.mjs'], plugin, {0}),
        ('browser', ['node', '--test', '--test-reporter=junit', 'test/browser.test.mjs'], plugin, {0}),
        ('python', [sys.executable, '-m', 'unittest', 'discover', '-s', 'tests', '-v'], root, {0}),
        ('metadata', [sys.executable, 'scripts/validate_release.py'], root, {0}),
        ('preflight', [sys.executable, 'scripts/preflight_submission.py', '--json'], root, {0, 1}),
    ]
    results = []
    for name, command, cwd, expected in commands:
        start = time.monotonic()
        try:
            result = subprocess.run(command, cwd=cwd, capture_output=True, timeout=300, check=False)
            code, stdout, stderr = result.returncode, result.stdout, result.stderr
        except (subprocess.TimeoutExpired, OSError):
            code, stdout, stderr = -1, b'', b'Command unavailable or exceeded five-minute test limit.\n'
        suffix = '.xml' if name in {'node', 'browser'} else '.json' if name == 'preflight' else '.log'
        (output / (name + suffix)).write_bytes(stdout)
        (output / (name + '.stderr.log')).write_bytes(stderr)
        accepted = code in expected
        if name == 'preflight' and accepted:
            try:
                readiness = json.loads(stdout)
                accepted = readiness.get('localChecksOnly') is True and readiness.get('readyForMaintainerPortalReview') is (code == 0)
            except (ValueError, AttributeError):
                accepted = False
        results.append({'suite': name, 'exitCode': code, 'command': command, 'passed': accepted, 'seconds': round(time.monotonic() - start, 3)})
        print(f'{name}: exit {code}' + (' (readiness findings recorded separately)' if name == 'preflight' else ''))
    technical_passed = all(r['passed'] for r in results)
    report = {'schemaVersion': 1, 'recordedAtUTC': datetime.now(timezone.utc).isoformat(), 'commit': commit,
              'trackedDiffSHA256': hashlib.sha256(diff).hexdigest(), 'dirty': bool(diff or untracked),
              'sourceSHA256': source_hashes, 'os': platform.system(), 'machine': platform.machine(),
              'python': platform.python_version(), 'node': subprocess.check_output(['node', '--version'], text=True).strip(),
              'technicalChecksPassed': technical_passed, 'nativeUATExecuted': False, 'liveProviderTestsExecuted': False,
              'openAIApproval': 'not established', 'results': results}
    (output / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    files = sorted(p for p in output.iterdir() if p.is_file())
    (output / 'SHA256SUMS.txt').write_text(''.join(f'{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.name}\n' for p in files))
    print('Technical checks: ' + ('PASS' if technical_passed else 'FAIL') + '; no native UAT or OpenAI approval is asserted.')
    return not technical_passed


if __name__ == '__main__':
    raise SystemExit(main())
