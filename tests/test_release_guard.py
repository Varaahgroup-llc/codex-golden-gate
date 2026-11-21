"""Release decisions use synthetic API responses; no tags/releases/cloud writes."""
import copy
import importlib.util
from pathlib import Path
import unittest
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))

spec = importlib.util.spec_from_file_location('release_guard', Path(__file__).resolve().parents[1] / 'scripts/release_guard.py')
guard = importlib.util.module_from_spec(spec)
spec.loader.exec_module(guard)
SHA = 'a' * 40


class ReleaseGuardTests(unittest.TestCase):
    def setUp(self):
        self.inputs = dict(tag='v0.2.0', version='0.2.0', commit=SHA, on_main=True, annotated=True,
                           runs=[dict(databaseId=2, attempt=1, headSha=SHA, headBranch='main', event='push', status='completed', conclusion='success')],
                           existing_release=False, protected_environment={'can_admins_bypass': False, 'protection_rules': [
                               {'type': 'required_reviewers', 'reviewers': [{'type': 'User', 'reviewer': {'id': 123}}]}]})

    def test_valid_fixture_only_allows_draft_creation(self):
        self.assertEqual(guard.findings(**self.inputs), [])

    def test_wrong_or_injected_tags_are_blocked(self):
        for tag in ['v0.1.0', '--help', 'v0.2.0;echo bad', 'v0.2.0/other']:
            with self.subTest(tag=tag):
                self.assertTrue(guard.findings(**{**self.inputs, 'tag': tag}))

    def test_off_main_unannotated_or_short_sha_is_blocked(self):
        for change in [{'on_main': False}, {'annotated': False}, {'commit': 'aaaaaaa'}]:
            self.assertTrue(guard.findings(**{**self.inputs, **change}))

    def test_missing_failed_cancelled_running_ci_is_blocked(self):
        for status, conclusion in [('completed', 'failure'), ('completed', 'cancelled'), ('in_progress', None)]:
            run = {**self.inputs['runs'][0], 'status': status, 'conclusion': conclusion}
            self.assertTrue(guard.findings(**{**self.inputs, 'runs': [run]}))
        self.assertTrue(guard.findings(**{**self.inputs, 'runs': []}))

    def test_other_commit_branch_or_event_cannot_satisfy_gate(self):
        for change in [{'headSha': 'b' * 40}, {'headBranch': 'feature'}, {'event': 'pull_request'}]:
            run = {**self.inputs['runs'][0], **change}
            self.assertTrue(guard.findings(**{**self.inputs, 'runs': [run]}))

    def test_latest_failure_overrides_older_green_run(self):
        runs = self.inputs['runs'] + [{**self.inputs['runs'][0], 'databaseId': 3, 'conclusion': 'failure'}]
        self.assertTrue(guard.findings(**{**self.inputs, 'runs': runs}))

    def test_existing_draft_or_published_release_cannot_be_overwritten(self):
        self.assertTrue(guard.findings(**{**self.inputs, 'existing_release': True}))

    def test_unprotected_or_bypassable_environment_is_blocked(self):
        for environment in [{}, {'can_admins_bypass': False, 'protection_rules': []},
                            {'can_admins_bypass': False, 'protection_rules': [{'type': 'required_reviewers', 'reviewers': []}]},
                            {**copy.deepcopy(self.inputs['protected_environment']), 'can_admins_bypass': True}]:
            self.assertTrue(guard.findings(**{**self.inputs, 'protected_environment': environment}))


if __name__ == '__main__':
    unittest.main()
