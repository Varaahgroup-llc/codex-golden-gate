"""Prepare exact-source candidate assets and a readiness report without publishing."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile
import zipfile

from package import approved_files, package
from release_policy import ROOT, bundle, git, read, require

REPO = 'https://github.com/Varaahgroup-llc/codex-golden-gate'
JIRA = 'https://varaahgroup.atlassian.net/browse/'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def checked_evidence(directory, sha):
    report = json.loads((directory / 'report.json').read_text())
    require(report['commit'] == sha and report['dirty'] is False, 'Evidence must describe the clean candidate commit')
    required = {'build', 'bundle', 'node', 'browser', 'python', 'metadata', 'preflight'}
    require(report['technicalChecksPassed'] is True and {r['suite'] for r in report['results']} == required
            and all(r['passed'] is True for r in report['results']), 'Incomplete or failed test evidence')
    hashes = {name: digest(path) for path, name in approved_files(ROOT)}
    require(report['sourceSHA256'] == hashes, 'Tested source hashes differ from packaged inputs')
    checksums = (directory / 'SHA256SUMS.txt').read_text().splitlines()
    expected = [f'{digest(p)}  {p.name}' for p in sorted(directory.iterdir()) if p.name != 'SHA256SUMS.txt']
    require(checksums == expected, 'Evidence checksum mismatch')
    return report


def security():
    # Suppress scanner payloads. Only counts, tool version and pass/fail enter evidence.
    scanner = os.environ.get('GG_GITLEAKS', 'gitleaks')
    version = subprocess.check_output([scanner, 'version'], text=True).strip()
    require(version.lstrip('v') == '8.24.3', 'Use the checksum-pinned Gitleaks 8.24.3')
    subprocess.run([scanner, 'git', '--redact=100', '--no-banner', '--log-level=error',
                    '--log-opts=HEAD', '.'], cwd=ROOT, stdout=subprocess.DEVNULL, check=True)
    audit = subprocess.run(['npm', 'audit', '--json', '--audit-level=low'], cwd=ROOT / 'plugins/golden-gate',
                           capture_output=True, check=False)
    require(audit.returncode == 0, 'Dependency audit failed or reported vulnerabilities. Inspect npm audit separately.')
    counts = json.loads(audit.stdout)['metadata']['vulnerabilities']
    require(counts['total'] == 0, 'Dependency audit reported findings')
    return {'secretScan': {'tool': 'Gitleaks ' + version, 'historyThrough': git('rev-parse', 'HEAD'), 'findings': 0},
            'npmAudit': counts}


def prepare(output, evidence):
    sha = git('rev-parse', 'HEAD')
    require(not git('status', '--porcelain'), 'Candidate requires a clean checkout')
    plan, records = bundle()
    report = checked_evidence(evidence, sha)
    scans = security()
    output.mkdir(parents=True, exist_ok=True)
    require(not any(output.iterdir()), 'Use an empty candidate output directory')
    source, plugin, sums = package(ROOT, output)
    with tempfile.TemporaryDirectory() as tmp:
        restored = Path(tmp)
        with zipfile.ZipFile(source) as archive:
            archive.extractall(restored)
        copies = package(restored / 'codex-golden-gate', restored / 'rebuilt')
        for original, copy in zip((source, plugin, sums), copies):
            require(digest(original) == digest(copy), 'Recovered package differs from original')
    preflight = json.loads((evidence / 'preflight.json').read_text())
    manifest = {
        'version': plan['version'], 'commit': sha, 'sourceTree': git('rev-parse', 'HEAD^{tree}'),
        'baselineTag': plan['previousTag'], 'versionProposal': plan['proposalReason'],
        'history': plan['history'], 'changes': list(records.values()), 'limitations': plan['limitations'],
        'dependencyLockSHA256': digest(ROOT / 'plugins/golden-gate/package-lock.json'),
        'dependencies': {k: v['version'] for k, v in read('plugins/golden-gate/package-lock.json')['packages'].items() if k},
        'tests': report['results'], 'evidenceChecksumsSHA256': digest(evidence / 'SHA256SUMS.txt'),
        'security': scans, 'directoryFindings': preflight['findings'],
        'artifacts': {p.name: digest(p) for p in (source, plugin)},
        'gates': {'functionalAcceptance': 'NOT_VERIFIED', 'securityAcceptance': 'NOT_VERIFIED',
                  'syntheticRegression': 'PASS', 'buildIntegrity': 'PASS', 'versionAccuracy': 'PASS',
                  'releaseDocumentationReview': 'NOT_VERIFIED', 'nativeCompatibility': 'NOT_VERIFIED',
                  'distributionReadiness': 'BLOCKED', 'nativeRollback': 'NOT_VERIFIED',
                  'archiveRecovery': 'PASS', 'ownerAuthorization': 'NOT_VERIFIED'},
        'approval': None, 'publicationAuthorized': False,
    }
    (output / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    notes = [f"# Golden Gate {plan['version']}", '', 'Internal candidate for review.', '', '## Changes', '']
    for item in plan['history']:
        links = [f'[{key}]({JIRA}{key})' for key in item['issues']]
        if item['pr']:
            links.append(f"[PR #{item['pr']}]({REPO}/pull/{item['pr']})")
        notes.append(f"- {item['summary']} " + ' · '.join(links))
    for item in records.values():
        links = [f"[{item['issue']}]({JIRA}{item['issue']})"]
        links.extend(f"[PR #{pr}]({REPO}/pull/{pr})" for pr in item.get('pullRequests', []))
        notes.append(f"- {item['summary']} " + ' · '.join(links))
    notes.extend(['', '## Acceptance still required', '', *['- ' + s for s in plan['limitations']],
                  '', f'Source commit [{sha}]({REPO}/commit/{sha}).'])
    (output / 'NOTES.md').write_text('\n'.join(notes) + '\n')
    # Produce a reviewable Keep a Changelog entry without mutating tested source.
    categories = {'FEATURE': 'Added', 'BUGFIX': 'Fixed', 'SECURITY': 'Security'}
    entries = {}
    for item in [*plan['history'], *records.values()]:
        category = categories.get(item['class'], 'Changed')
        issues = item['issues'] if 'issues' in item else [item['issue']]
        links = ' · '.join(f'[{key}]({JIRA}{key})' for key in issues)
        entries.setdefault(category, []).append(f"- {item['summary']} {links}")
    changelog = [f"## [{plan['version']}] — Internal candidate", '']
    for category in ('Added', 'Changed', 'Fixed', 'Security'):
        if category in entries:
            changelog.extend([f'### {category}', '', *entries[category], ''])
    (output / 'CHANGELOG.md').write_text('\n'.join(changelog))
    with sums.open('a') as stream:
        for name in ('manifest.json', 'NOTES.md', 'CHANGELOG.md'):
            stream.write(f'{digest(output / name)}  {name}\n')
    print(f"Prepared {plan['version']} at {sha}. Owner approval pending.")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--scan-only', action='store_true')
    parser.add_argument('--output', type=Path)
    parser.add_argument('--evidence', type=Path)
    args = parser.parse_args()
    if args.scan_only:
        print(json.dumps(security()))
    elif args.output and args.evidence:
        prepare(args.output.resolve(), args.evidence.resolve())
    else:
        parser.error('provide --scan-only or both --output and --evidence')
