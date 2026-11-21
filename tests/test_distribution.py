"""Reject incomplete, stale or modified release assets before distribution."""
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import verify_distribution as verify


class DistributionTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.tag = 'v0.3.0-rc.1'
        self.sha = 'a' * 40
        for name in ('golden-gate-0.3.0-rc.1-plugin.zip', 'golden-gate-0.3.0-rc.1-source.zip',
                     'NOTES.md', 'CHANGELOG.md', 'sbom.cdx.json', 'test-evidence.zip'):
            (self.root / name).write_bytes(b'synthetic artifact')
        (self.root / 'manifest.json').write_text(json.dumps({'version': self.tag[1:], 'commit': self.sha}))
        (self.root / 'release-guard.json').write_text(json.dumps(
            {'commit': self.sha, 'tag': self.tag, 'draftCreationAllowed': True}))
        self.index = self.root / 'SHA256SUMS.txt'
        self.index.write_text(''.join(f'{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.name}\n'
                                      for p in sorted(self.root.iterdir())))

    def check(self):
        verify.verify_inventory(self.root, self.tag, self.sha, hashlib.sha256(self.index.read_bytes()).hexdigest())

    def test_exact_set_and_bytes(self):
        self.check()
        (self.root / 'test-evidence.zip').write_bytes(b'changed')
        with self.assertRaisesRegex(ValueError, 'checksum mismatch'):
            self.check()

    def test_extra_and_missing_assets(self):
        extra = self.root / 'unreviewed.txt'
        extra.touch()
        with self.assertRaisesRegex(ValueError, 'asset set'):
            self.check()
        extra.unlink()
        (self.root / 'sbom.cdx.json').unlink()
        with self.assertRaisesRegex(ValueError, 'asset set'):
            self.check()

    def test_wrong_commit_or_inventory(self):
        for sha, inventory in [('b' * 40, hashlib.sha256(self.index.read_bytes()).hexdigest()),
                               (self.sha, 'f' * 64)]:
            with self.assertRaises(ValueError):
                verify.verify_inventory(self.root, self.tag, sha, inventory)

    def test_duplicate_and_path_entries(self):
        original = self.index.read_text()
        for entry in (original.splitlines()[0], 'a' * 64 + '  ../unexpected'):
            self.index.write_text(original + entry + '\n')
            with self.assertRaisesRegex(ValueError, 'Invalid checksum entry'):
                self.check()

    def test_missing_decision_or_unprotected_environment(self):
        with patch.object(verify, 'ROOT', self.root), self.assertRaises(FileNotFoundError):
            verify.decision(self.tag)
        with patch.object(verify, 'api', return_value={}), self.assertRaises(ValueError):
            verify.verify_environment()
