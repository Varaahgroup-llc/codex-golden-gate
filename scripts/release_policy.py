"""Validate a Golden Gate change record and the reviewed release bundle."""
import argparse
import json
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]
VERSION = r'(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)(?:-(?:alpha|beta|rc)\.(?:0|[1-9][0-9]*))?'
CLASSES = set('FEATURE ENHANCEMENT BUGFIX SECURITY PERFORMANCE REFACTOR INFRASTRUCTURE DEPENDENCY DOCUMENTATION BREAKING_CHANGE'.split())


def require(condition, message):
    if not condition:
        raise ValueError(message)


def git(*args):
    return subprocess.check_output(['git', *args], cwd=ROOT, text=True).strip()


def read(path):
    return json.loads((ROOT / path).read_text())


def check_issue(key):
    require(isinstance(key, str) and re.fullmatch(r'GG-[1-9][0-9]*', key), 'Invalid GG issue')
    require(f'/browse/{key})' in (ROOT / 'docs/TRACKING.md').read_text(), f'Add {key} to the verified GG crosswalk')


def record(filename):
    require(re.fullmatch(r'GG-[1-9][0-9]*-[a-z0-9-]+\.json', filename), 'Invalid change filename')
    data = read(Path('docs/changes') / filename)
    check_issue(data['issue'])
    require(filename.startswith(data['issue'] + '-'), 'Change filename and issue differ')
    require(data['class'] in CLASSES, 'Unknown change class')
    for field in ('summary', 'owner', 'priority', 'acceptance', 'validation', 'securityImpact'):
        require(isinstance(data[field], str) and data[field].strip(), f'Missing change field {field}')
    require(data['target'] == 'unassigned' or re.fullmatch(VERSION, data['target']), 'Invalid release target')
    return data


def pr_check(base):
    require(re.fullmatch('[0-9a-f]{40}', base), 'Expected full PR base SHA')
    changed = git('diff', '--name-only', '--diff-filter=AM', base + '...HEAD').splitlines()
    files = [p for p in changed if p.startswith('docs/changes/')]
    require(files and 'CHANGELOG.md' in changed, 'PR requires a changed GG record and CHANGELOG.md')
    changelog = (ROOT / 'CHANGELOG.md').read_text()
    unreleased = re.search(r'^## \[Unreleased\]\s*$(.*?)(?=^## |\Z)', changelog, re.M | re.S)
    require(unreleased, 'Missing Unreleased section')
    for path in files:
        change = record(path.removeprefix('docs/changes/'))
        require(re.search(r'\b' + change['issue'] + r'\b', unreleased[1]), 'Unreleased entry must reference its issue')


def proposal(previous, impact):
    require(re.fullmatch(VERSION, previous) and '-' not in previous, 'Invalid previous proposal')
    major, minor, patch = map(int, previous.split('.'))
    if impact == 'major':
        return f'{major + 1}.0.0'
    if impact == 'minor':
        return f'{major}.{minor + 1}.0'
    require(impact == 'patch', 'Expected major, minor or patch impact')
    return f'{major}.{minor}.{patch + 1}'


def bundle():
    plan = read('docs/releases/bundle.json')
    version = read('plugins/golden-gate/plugin.json')['version']
    require(re.fullmatch(VERSION, version) and plan['version'] == version, 'Bundle and plugin versions must agree')
    require(plan['proposalReason'].strip() and plan['limitations'], 'Explain the version impact and limitations')
    require(re.fullmatch('v' + VERSION, plan['previousTag']), 'Invalid baseline tag')
    baseline = git('rev-parse', '--verify', 'refs/tags/' + plan['previousTag'] + '^{commit}')
    chain = git('rev-list', '--first-parent', 'HEAD').splitlines()
    require(baseline in chain, 'Baseline must be on first-parent history')
    remaining = set(chain[:chain.index(baseline)])
    anchor = plan['previousProposalCommit']
    require(anchor == baseline or anchor in remaining, 'Version baseline lies outside the release range')
    after_proposal = set(chain[:chain.index(anchor)])
    classes = set()
    for item in plan['history']:
        sha = item['commit']
        require(sha in remaining, 'Unexpected or duplicate bundled commit')
        remaining.remove(sha)
        if sha in after_proposal:
            classes.add(item['class'])
        require(item['class'] in CLASSES and item['summary'].strip() and item['issues'], 'Invalid historical change')
        for issue in item['issues']:
            check_issue(issue)
        subject = git('show', '-s', '--format=%s', sha)
        pr = re.match(r'Merge pull request #(\d+) ', subject)
        require(item['pr'] == (int(pr[1]) if pr else None), 'PR and historical commit differ')
    catalog = set(read('scripts/package-files.json')['source'])
    records = {}
    for name in plan['records']:
        require(f'docs/changes/{name}' in catalog, 'Include selected change record in source package catalog')
        change = record(name)
        require(change['target'] == version and name not in records, 'Bundle contains duplicate or untargeted work')
        records[name] = change
    # Cover each remaining first-parent delta, including squash and merge commits.
    # A later unrelated commit cannot silently ride along in the tested package.
    used = set()
    for sha in sorted(remaining):
        paths = git('diff', '--name-only', sha + '^1', sha, '--', 'docs/changes').splitlines()
        names = [p.removeprefix('docs/changes/') for p in paths]
        require(names and all(n in records for n in names), f'Unaccounted release content at {sha}')
        used.update(names)
        for name in names:
            change = records[name]
            change.setdefault('commits', []).append(sha)
            subject = git('show', '-s', '--format=%s', sha)
            pr = re.match(r'Merge pull request #(\d+) ', subject) or re.search(r'\(#(\d+)\)$', subject)
            if pr:
                change.setdefault('pullRequests', []).append(int(pr[1]))
            if sha in after_proposal:
                classes.add(change['class'])
    require(used == set(records), 'Selected work lacks implementation in the release range')
    impact = 'patch'
    if classes & {'FEATURE', 'ENHANCEMENT', 'BREAKING_CHANGE'}:
        impact = 'minor'
    if 'BREAKING_CHANGE' in classes and not plan['previousProposal'].startswith('0.'):
        impact = 'major'
    require(proposal(plan['previousProposal'], impact) == version.split('-')[0], 'Version differs from included change impact')
    return plan, records


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base', required=True)
    pr_check(parser.parse_args().base)
