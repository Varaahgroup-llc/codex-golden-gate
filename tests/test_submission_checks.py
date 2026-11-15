import copy
import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location('submission_preflight', Path(__file__).resolve().parents[1] / 'scripts/preflight_submission.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class SubmissionChecks(unittest.TestCase):
    def setUp(self):
        self.manifest = {'extensions': {'com.openai': {'interface': {
            'displayName': 'Secret Bridge', 'shortDescription': 'Private secret setup',
            'longDescription': 'Local prototype with destination review.',
            'developerName': 'Varaahgroup-llc', 'category': 'Productivity',
            'defaultPrompt': ['Open the setup form.'], 'capabilities': ['Read', 'Write'],
            'supportURL': 'https://github.com/Varaahgroup-llc/codex-secret-bridge/issues'}}}}

    def test_final_directory_subtitle_limit_catches_old_listing(self):
        self.manifest['extensions']['com.openai']['interface']['shortDescription'] = 'Private secret entry and destination-aware saving'
        self.assertIn('listing.shortDescription', [f['code'] for f in module.listing_findings(self.manifest)])

    def test_url_cannot_smuggle_credentials(self):
        self.manifest['extensions']['com.openai']['interface']['supportURL'] = 'https://user:password@example.com/support'
        self.assertIn('listing.supportURL', [f['code'] for f in module.listing_findings(self.manifest)])

    def test_clean_listing_does_not_override_missing_evidence(self):
        self.assertEqual(module.listing_findings(self.manifest), [])
        result = module.assess(self.manifest, {})
        self.assertFalse(result['readyForMaintainerPortalReview'])
        self.assertEqual(len(result['findings']), len(module.REQUIRED_GATES))

    def test_verified_flag_without_evidence_does_not_open_gate(self):
        readiness = {'gates': {name: {'status': 'verified', 'evidence': []} for name in module.REQUIRED_GATES}}
        self.assertFalse(module.assess(self.manifest, readiness)['readyForMaintainerPortalReview'])

    def test_complete_local_evidence_still_does_not_claim_openai_approval(self):
        readiness = {'gates': {name: {'status': 'verified', 'evidence': ['test-fixture-only']} for name in module.REQUIRED_GATES}}
        result = module.assess(copy.deepcopy(self.manifest), readiness)
        self.assertTrue(result['readyForMaintainerPortalReview'])
        self.assertIn('not established', result['openAIApproval'])


if __name__ == '__main__':
    unittest.main()
