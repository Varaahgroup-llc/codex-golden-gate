"""Check an exact GitHub release against its approved inventory and attested source."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import tempfile

from release_policy import ROOT, VERSION, require

REPO = 'Varaahgroup-llc/codex-golden-gate'


def verify_inventory(directory, tag, commit, approved_hash):
    sums = directory / 'SHA256SUMS.txt'
    require(hashlib.sha256(sums.read_bytes()).hexdigest() == approved_hash,
            'Inventory differs from the approved digest')
    version = tag[1:]
    expected = {f'golden-gate-{version}-{kind}.zip' for kind in ('plugin', 'source')}
    expected.update({'sbom.cdx.json', 'manifest.json', 'release-guard.json', 'NOTES.md', 'CHANGELOG.md', 'test-evidence.zip'})
    require({p.name for p in directory.iterdir()} == expected | {sums.name}, 'Unexpected release asset set')
    seen = set()
    for line in sums.read_text().splitlines():
        item = re.fullmatch(r'([0-9a-f]{64})  ([A-Za-z0-9._-]+)', line)
        require(item and item[2] in expected and item[2] not in seen, 'Invalid checksum entry')
        seen.add(item[2])
        require(hashlib.sha256((directory / item[2]).read_bytes()).hexdigest() == item[1],
                'Release asset checksum mismatch')
    require(seen == expected, 'Incomplete inventory')
    manifest = json.loads((directory / 'manifest.json').read_text())
    require((manifest['version'], manifest['commit']) == (version, commit), 'Manifest identity mismatch')
    guard = json.loads((directory / 'release-guard.json').read_text())
    require(guard['tag'] == tag and guard['commit'] == commit and guard['draftCreationAllowed'] is True,
            'Draft guard identity mismatch')


def decision(tag):
    require(re.fullmatch('v' + VERSION, tag), 'Invalid tag')
    data = json.loads((ROOT / 'docs/releases/approvals' / (tag + '.json')).read_text())
    require(data['tag'] == tag and data['channel'] == 'github-release'
            and data['decision'] == 'APPROVED', 'Missing channel-specific owner decision')
    require(re.fullmatch(r'[0-9a-f]{40}', data['commit']) and
            re.fullmatch(r'[0-9a-f]{64}', data['inventorySHA256']), 'Invalid approved commit or digest')
    for gate in ('nativeUAT', 'security', 'rollback', 'architecture', 'ownerApproval'):
        require(re.fullmatch(r'https://varaahgroup\.atlassian\.net/browse/GG-[1-9]\d*\?focusedCommentId=[1-9]\d*',
                             data['evidence'][gate]), f'Missing GG decision evidence for {gate}')
    return data


def api(endpoint):
    return json.loads(subprocess.check_output(['gh', 'api', 'repos/' + REPO + '/' + endpoint]))


def verify_environment():
    env = api('environments/release-publication')
    require(env.get('can_admins_bypass') is False and any(
        r['type'] == 'required_reviewers' and r.get('reviewers') for r in env['protection_rules']),
        'Configure release-publication with required reviewers and no bypass')
    policies = api('environments/release-publication/deployment-branch-policies')
    require(env['deployment_branch_policy']['custom_branch_policies'] and policies['total_count'] == 1
            and [(p['type'], p['name']) for p in policies['branch_policies']] == [('branch', 'main')],
            'Restrict release-publication to main')


def verify(tag, state):
    approval = decision(tag)
    commit = approval['commit']
    tag_ref = api('git/ref/tags/' + tag)['object']
    require(tag_ref['type'] == 'tag', 'Expected an annotated tag')
    target = api('git/tags/' + tag_ref['sha'])['object']
    require(target['type'] == 'commit' and target['sha'] == commit, 'Approved tag and commit must agree')
    release = json.loads(subprocess.check_output(['gh', 'release', 'view', tag, '--repo', REPO,
                                                 '--json', 'tagName,isDraft']))
    require(release['tagName'] == tag and release['isDraft'] is (state == 'draft'), 'Release state changed')
    with tempfile.TemporaryDirectory() as tmp:
        directory = Path(tmp)
        subprocess.run(['gh', 'release', 'download', tag, '--repo', REPO, '--dir', directory], check=True)
        verify_inventory(directory, tag, commit, approval['inventorySHA256'])
        subprocess.run(['gh', 'attestation', 'verify', directory / 'SHA256SUMS.txt', '--repo', REPO,
                        '--signer-workflow', REPO + '/.github/workflows/release.yml', '--source-ref',
                        'refs/tags/' + tag, '--source-digest', commit], check=True)
    print(f'Verified {state} assets for {tag} at {commit}.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--tag', required=True)
    parser.add_argument('--state', choices=('draft', 'published'), required=True)
    args = parser.parse_args()
    if args.state == 'draft':
        verify_environment()
    verify(args.tag, args.state)
