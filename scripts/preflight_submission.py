#!/usr/bin/env python3
"""Offline listing checks and evidence gates. This is not the OpenAI validator."""
import argparse
import json
from pathlib import Path
import re
from urllib.parse import urlsplit

CATEGORIES = {'Productivity', 'Creativity', 'Developer Tools', 'Business & Operations',
              'Data & Analytics', 'Communication', 'Education & Research', 'Security',
              'Finance', 'Healthcare', 'Travel', 'Entertainment', 'Scientific Research', 'Other'}
REQUIRED_GATES = {'policy_eligibility', 'verified_publisher', 'local_mcp_allowlisting',
                  'native_client_validation', 'security_provider_validation',
                  'executed_reviewer_materials', 'publisher_listing_materials'}


def valid_https_url(value):
    try:
        if not isinstance(value, str) or len(value) > 1024 or '\\' in value or any(c.isspace() or ord(c) < 33 or 127 <= ord(c) <= 159 for c in value):
            return False
        url = urlsplit(value)
        port = url.port  # Reject malformed ports as well as malformed hosts.
        return bool(url.scheme == 'https' and url.hostname and url.username is None and url.password is None)
    except ValueError:
        return False


def listing_findings(manifest, *, mcp_review=False):
    findings = []
    interface = manifest.get('extensions', {}).get('com.openai', {}).get('interface', {})
    def fail(code, message):
        findings.append({'code': code, 'message': message})
    for key, maximum, multiline in [('displayName', 30, False), ('shortDescription', 30, False),
                                     ('longDescription', 4000, True), ('developerName', 80, False)]:
        value = interface.get(key)
        if not isinstance(value, str) or not value.strip():
            fail('listing.' + key, f'{key} must be nonempty text')
        elif len(value) > maximum or (not multiline and ('\n' in value or '\r' in value)):
            fail('listing.' + key, f'{key} exceeds its final directory limit or single-line rule')
    if interface.get('category') not in CATEGORIES:
        fail('listing.category', 'Choose a documented directory category')
    for key, limit, count in [('defaultPrompt', 128, 3), ('capabilities', 120, 20)]:
        values = interface.get(key, [])
        if key == 'defaultPrompt' and isinstance(values, str):
            values = [values]
        if not isinstance(values, list) or len(values) > count:
            fail('listing.' + key, f'{key} must be a list with at most {count} entries')
            continue
        if any(not isinstance(v, str) or not v.strip() or len(v) > limit or '\n' in v or '\r' in v for v in values):
            fail('listing.' + key, f'{key} contains an empty, multiline or overlong entry')
        if key == 'defaultPrompt' and len({re.sub(r'\s+', ' ', str(v)).strip().casefold() for v in values}) != len(values):
            fail('listing.defaultPrompt', 'Starter prompts must be unique')
    for key in ['websiteURL', 'supportURL', 'privacyPolicyURL', 'termsOfServiceURL']:
        if key not in interface:
            if mcp_review:
                fail('listing.' + key, f'{key} is missing from the MCP review listing; publish and verify the real page before supplying its URL')
            continue
        value = interface[key]
        if not valid_https_url(value):
            fail('listing.' + key, f'{key} must be an HTTPS URL without embedded credentials')
    return findings


def review_findings(manifest, mcp_config):
    """Check single-server review expectations, never claim they were executed."""
    servers = mcp_config.get('mcpServers', {})
    if not servers:
        return []
    findings = []
    def fail(code, message):
        findings.append({'code': code, 'message': message})
    openai = manifest.get('extensions', {}).get('com.openai', {})
    review = openai.get('review', {})
    if len(servers) != 1:
        fail('preflight.multipleServers', 'This local checker supports the single-server review profile only; inspect per-server requirements separately')
        return findings
    cases = review.get('test_cases', {})
    if not isinstance(cases, dict):
        cases = {}
    for kind, count in [('positive', 5), ('negative', 3)]:
        values = cases.get(kind)
        if not isinstance(values, list) or len(values) != count:
            fail('review.' + kind, f'Declare exactly {count} {kind} review expectations; executed evidence remains a separate gate')
            continue
        required = ['description', 'prompt'] + (['tools_triggered', 'expected_behavior'] if kind == 'positive' else [])
        for index, case in enumerate(values):
            if not isinstance(case, dict) or any(not isinstance(case.get(k), str) or not case[k].strip() or len(case[k]) > 4000 for k in required):
                fail(f'review.{kind}.{index + 1}', 'Review expectations need nonblank description/prompt and positive tool/result fields, at most 4000 characters each')
    if not valid_https_url(review.get('demo_recording_url')):
        fail('review.demo_recording_url', 'A real reviewer-accessible HTTPS recording URL is missing or invalid; a script or unrun plan is not a recording')
    notes = openai.get('publication', {}).get('release_notes')
    if not isinstance(notes, str) or not notes.strip():
        fail('publication.release_notes', 'Describe the actual submitted version in publication.release_notes')
    return findings


def assess(manifest, readiness, mcp_config=None):
    mcp_config = mcp_config or {}
    findings = listing_findings(manifest, mcp_review=bool(mcp_config.get('mcpServers')))
    findings.extend(review_findings(manifest, mcp_config))
    gates = readiness.get('gates', {})
    for name in sorted(REQUIRED_GATES):
        gate = gates.get(name, {})
        evidence = gate.get('evidence', [])
        if gate.get('status') != 'verified' or not isinstance(evidence, list) or not evidence or not all(isinstance(e, str) and e.strip() for e in evidence):
            findings.append({'code': 'gate.' + name, 'issue': gate.get('issue'),
                             'message': gate.get('reason', 'Missing explicit verification and evidence')})
    return {'localChecksOnly': True, 'readyForMaintainerPortalReview': not findings,
            'openAIApproval': 'not established by this check', 'findings': findings}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--json', action='store_true', dest='as_json')
    parser.add_argument('--report-only', action='store_true', help='Report known blockers without failing CI; never means eligible or approved')
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    manifest = json.loads((root / 'plugins/secret-bridge/plugin.json').read_text())
    mcp_file = root / 'plugins/secret-bridge/mcp.json'
    mcp_config = json.loads(mcp_file.read_text()) if mcp_file.is_file() else {}
    readiness = json.loads((root / 'docs/approval/readiness.json').read_text())
    result = assess(manifest, readiness, mcp_config)
    if args.as_json:
        print(json.dumps(result, indent=2))
    else:
        print('Local preflight: ' + ('ready for maintainer portal review' if result['readyForMaintainerPortalReview'] else 'NOT READY'))
        for finding in result['findings']:
            print(f"- {finding['code']}: {finding['message']}")
        print('This limited local check does not establish OpenAI eligibility, approval or passing portal scans.')
    return 0 if result['readyForMaintainerPortalReview'] or args.report_only else 1


if __name__ == '__main__':
    raise SystemExit(main())
