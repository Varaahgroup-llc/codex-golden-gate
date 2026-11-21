"""Regression tests for scope, source identity and incomplete test evidence."""
from pathlib import Path
import json
import re
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import candidate
import release_policy as policy


class CandidateTests(unittest.TestCase):
    def test_version_contract(self):
        for version in ('0.3.0', '0.3.0-rc.1', '1.0.0-beta.12', '2.0.0-alpha.1'):
            self.assertTrue(re.fullmatch(policy.VERSION, version))
        for version in ('01.1.0', '1.0.0-rc.01', '1.0.0-rc.', 'v1.0.0', '1.0.0-../../x'):
            self.assertFalse(re.fullmatch(policy.VERSION, version))
        self.assertEqual(policy.proposal('1.1.9', 'major'), '2.0.0')
        self.assertEqual(policy.proposal('0.2.8', 'minor'), '0.3.0')
        self.assertEqual(policy.proposal('0.3.0', 'patch'), '0.3.1')

    def test_stale_dirty_and_incomplete_evidence(self):
        with tempfile.TemporaryDirectory() as tmp:
            evidence = Path(tmp)
            fields = dict(commit='a' * 40, dirty=False, technicalChecksPassed=True, results=[])
            for change, error in [({'commit': 'b' * 40}, 'clean candidate'), ({'dirty': True}, 'clean candidate'),
                                  ({}, 'Incomplete')]:
                (evidence / 'report.json').write_text(json.dumps({**fields, **change}))
                with self.assertRaisesRegex(ValueError, error):
                    candidate.checked_evidence(evidence, 'a' * 40)

    def test_missing_record_and_duplicate_history(self):
        previous, current = 'a' * 40, 'b' * 40
        plan = dict(version='0.2.0-rc.1', proposalReason='feature', limitations=['native pending'],
                    previousTag='v0.1.0', previousProposal='0.1.0', previousProposalCommit=previous,
                    records=[], history=[])
        def git(*args):
            if args[0] == 'rev-parse':
                return previous
            if args[0] == 'rev-list':
                return current + '\n' + previous
            return ''
        with patch.object(policy, 'git', git), patch.object(policy, 'read', side_effect=lambda path: {'source': []} if path == 'scripts/package-files.json' else plan):
            with self.assertRaisesRegex(ValueError, 'Unaccounted'):
                policy.bundle()
            item = dict(commit=current, issues=['GG-9'], summary='feature', pr=None, **{'class': 'FEATURE'})
            plan['history'] = [item, item]
            with self.assertRaisesRegex(ValueError, 'duplicate'):
                policy.bundle()
