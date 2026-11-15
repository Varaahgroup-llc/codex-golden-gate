#!/usr/bin/env python3
"""Fail closed before draft creation; never publish, tag, or change repository settings."""
import argparse
import json
from pathlib import Path
import re
import subprocess

REPOSITORY = 'Varaahgroup-llc/codex-golden-gate'


def findings(*, tag, version, commit, on_main, annotated, runs, existing_release, protected_environment):
    errors = []
    if not re.fullmatch(r'v\d+\.\d+\.\d+(?:-[0-9A-Za-z.-]+)?', tag) or tag != f'v{version}':
        errors.append('Tag must match the package version exactly.')
    if not re.fullmatch(r'[0-9a-f]{40}', commit):
        errors.append('Release source must be a full Git commit SHA.')
    if not on_main:
        errors.append('Release commit must belong to origin/main.')
    if not annotated:
        errors.append('Release tag must be annotated.')
    # A later failed/re-running CI cannot hide behind an earlier green attempt.
    matching = [r for r in runs if r.get('headSha') == commit and r.get('headBranch') == 'main' and r.get('event') == 'push']
    latest = max(matching, key=lambda r: (r.get('databaseId', 0), r.get('attempt', 0)), default={})
    if latest.get('status') != 'completed' or latest.get('conclusion') != 'success':
        errors.append('The latest main push CI for this exact commit must have passed.')
    if existing_release:
        errors.append('A release already exists for this tag; do not overwrite or reuse it.')
    rules = protected_environment.get('protection_rules', [])
    if not any(rule.get('type') == 'required_reviewers' and rule.get('reviewers') for rule in rules):
        errors.append('The release-draft environment needs a required reviewer.')
    if protected_environment.get('can_admins_bypass') is not False:
        errors.append('The release-draft environment must disallow administrator bypass.')
    return errors


def command(args):
    return subprocess.check_output(args, text=True).strip()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--tag', required=True)
    parser.add_argument('--report', required=True, type=Path)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    version = json.loads((root / 'plugins/golden-gate/package.json').read_text())['version']
    # Fully qualified refs avoid revision/option ambiguity. Invalid tags stop before Git/network.
    if not re.fullmatch(r'v\d+\.\d+\.\d+(?:-[0-9A-Za-z.-]+)?', args.tag):
        raise SystemExit('Invalid release tag.')
    commit = command(['git', 'rev-parse', '--verify', f'refs/tags/{args.tag}^{{commit}}'])
    on_main = subprocess.run(['git', 'merge-base', '--is-ancestor', commit, 'refs/remotes/origin/main'], check=False).returncode == 0
    annotated = command(['git', 'cat-file', '-t', f'refs/tags/{args.tag}']) == 'tag'
    runs = json.loads(command(['gh', 'run', 'list', '--repo', REPOSITORY, '--workflow', 'ci.yml', '--commit', commit,
                               '--branch', 'main', '--limit', '100', '--json', 'databaseId,attempt,headSha,headBranch,event,status,conclusion,url']))
    # Paginated listing distinguishes absence from API failure; errors raise, never imply absence.
    releases = json.loads(command(['gh', 'api', '--paginate', '--slurp', f'repos/{REPOSITORY}/releases?per_page=100']))
    existing = any(r.get('tag_name') == args.tag for page in releases for r in page)
    environment = json.loads(command(['gh', 'api', f'repos/{REPOSITORY}/environments/release-draft']))
    errors = findings(tag=args.tag, version=version, commit=commit, on_main=on_main, annotated=annotated,
                      runs=runs, existing_release=existing, protected_environment=environment)
    report = {'schemaVersion': 1, 'tag': args.tag, 'commit': commit, 'draftCreationAllowed': not errors,
              'findings': errors, 'ciRuns': runs, 'publicationAuthorized': False, 'openAIApproval': 'not established'}
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2) + '\n')
    print('Draft release guard: ' + ('PASS' if not errors else 'BLOCKED'))
    for error in errors:
        print('- ' + error)
    return bool(errors)


if __name__ == '__main__':
    raise SystemExit(main())
