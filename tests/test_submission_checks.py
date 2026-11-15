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
            'displayName': 'Golden Gate', 'shortDescription': 'Private secret setup',
            'longDescription': 'Local prototype with destination review.',
            'developerName': 'Varaahgroup-llc', 'category': 'Productivity',
            'defaultPrompt': ['Open the setup form.'], 'capabilities': ['Read', 'Write'],
            'supportURL': 'https://github.com/Varaahgroup-llc/codex-golden-gate/issues'}}}}

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

    def mcp_fixture(self):
        manifest = copy.deepcopy(self.manifest)
        openai = manifest['extensions']['com.openai']
        for key in ['websiteURL', 'supportURL', 'privacyPolicyURL', 'termsOfServiceURL']:
            openai['interface'][key] = 'https://example.test/' + key
        openai['review'] = {
            'test_cases': {
                'positive': [{'description': f'Draft fixture {i}', 'prompt': f'Test {i}', 'tools_triggered': 'fixture_tool', 'expected_behavior': 'An observable result.'} for i in range(5)],
                'negative': [{'description': f'Unsupported fixture {i}', 'prompt': f'Do unsupported action {i}'} for i in range(3)],
            },
            'demo_recording_url': 'https://example.test/recording',
        }
        openai['publication'] = {'release_notes': 'Synthetic fixture notes.'}
        return manifest, {'mcpServers': {'fixture': {'type': 'stdio', 'command': 'node'}}}

    def test_mcp_missing_listing_urls_are_reported_individually(self):
        findings = module.listing_findings(self.manifest, mcp_review=True)
        self.assertEqual({f['code'] for f in findings}, {'listing.websiteURL', 'listing.privacyPolicyURL', 'listing.termsOfServiceURL'})

    def test_skills_only_does_not_require_mcp_review_materials(self):
        self.assertEqual(module.review_findings(self.manifest, {}), [])
        self.assertEqual(module.listing_findings(self.manifest), [])

    def test_draft_case_declarations_do_not_replace_execution_evidence(self):
        manifest, config = self.mcp_fixture()
        self.assertEqual(module.review_findings(manifest, config), [])
        result = module.assess(manifest, {}, config)
        self.assertFalse(result['readyForMaintainerPortalReview'])
        self.assertIn('gate.executed_reviewer_materials', {f['code'] for f in result['findings']})

    def test_missing_terms_cannot_hide_behind_verified_manual_flags(self):
        manifest, config = self.mcp_fixture()
        del manifest['extensions']['com.openai']['interface']['termsOfServiceURL']
        readiness = {'gates': {name: {'status': 'verified', 'evidence': ['synthetic-fixture']} for name in module.REQUIRED_GATES}}
        result = module.assess(manifest, readiness, config)
        self.assertFalse(result['readyForMaintainerPortalReview'])
        self.assertEqual([f['code'] for f in result['findings']], ['listing.termsOfServiceURL'])

    def test_incomplete_case_counts_are_reported(self):
        manifest, config = self.mcp_fixture()
        manifest['extensions']['com.openai']['review']['test_cases']['positive'].pop()
        self.assertIn('review.positive', {f['code'] for f in module.review_findings(manifest, config)})

    def test_positive_expectations_need_tools_and_observable_result(self):
        manifest, config = self.mcp_fixture()
        manifest['extensions']['com.openai']['review']['test_cases']['positive'][0]['expected_behavior'] = ' '
        self.assertIn('review.positive.1', {f['code'] for f in module.review_findings(manifest, config)})

    def test_recording_and_release_notes_cannot_be_omitted(self):
        manifest, config = self.mcp_fixture()
        del manifest['extensions']['com.openai']['review']['demo_recording_url']
        del manifest['extensions']['com.openai']['publication']['release_notes']
        self.assertEqual({f['code'] for f in module.review_findings(manifest, config)}, {'review.demo_recording_url', 'publication.release_notes'})

    def test_url_syntax_rejects_empty_credentials_controls_and_bad_ports(self):
        for value in ['https://@example.test', 'https://example.test/\nsecret', 'https://example.test:bad', 'https://example.test/with space', 'https://example.test\\path']:
            with self.subTest(value=value):
                self.assertFalse(module.valid_https_url(value))

    def test_documented_single_starter_prompt_is_accepted(self):
        self.manifest['extensions']['com.openai']['interface']['defaultPrompt'] = 'Open the setup form.'
        self.assertEqual(module.listing_findings(self.manifest), [])


if __name__ == '__main__':
    unittest.main()
