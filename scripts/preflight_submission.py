#!/usr/bin/env python3
"""Offline listing checks and evidence gates. This is not the OpenAI validator."""
import argparse
import json
from pathlib import Path
import re
from urllib.parse import urlsplit

CATEGORIES = {'Productivity', 'Creativity', 'Developer Tools', 'Business & Operations',
              'Data & Analytics', 'Communication', 'Education & Research', 'Security',
              'Finance', 'Healthcare', 'Travel', 'Entertainment', 'Other'}
REQUIRED_GATES = {'policy_eligibility', 'verified_publisher', 'local_mcp_allowlisting',
                  'native_client_validation', 'security_provider_validation',
                  'executed_reviewer_materials', 'publisher_listing_materials'}


def listing_findings(manifest):
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
        if not isinstance(values, list) or len(values) > count:
            fail('listing.' + key, f'{key} must be a list with at most {count} entries')
            continue
        if any(not isinstance(v, str) or not v.strip() or len(v) > limit or '\n' in v or '\r' in v for v in values):
            fail('listing.' + key, f'{key} contains an empty, multiline or overlong entry')
        if key == 'defaultPrompt' and len({re.sub(r'\s+', ' ', str(v)).strip().casefold() for v in values}) != len(values):
            fail('listing.defaultPrompt', 'Starter prompts must be unique')
    for key in ['websiteURL', 'supportURL', 'privacyPolicyURL', 'termsOfServiceURL']:
        if key not in interface:
            continue  # Route-specific required URLs remain a portal/manual check.
        value = interface[key]
        try:
            url = urlsplit(value) if isinstance(value, str) else None
            valid = url and url.scheme == 'https' and url.hostname and not url.username and not url.password and len(value) <= 1024
        except ValueError:
            valid = False
        if not valid:
            fail('listing.' + key, f'{key} must be an HTTPS URL without embedded credentials')
    return findings


def assess(manifest, readiness):
    findings = listing_findings(manifest)
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
    readiness = json.loads((root / 'docs/approval/readiness.json').read_text())
    result = assess(manifest, readiness)
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
