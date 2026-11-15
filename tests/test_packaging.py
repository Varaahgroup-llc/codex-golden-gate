"""Exercise release confidentiality boundaries using synthetic private files."""
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('packaging_script', ROOT / 'scripts/package.py')
packaging = importlib.util.module_from_spec(spec)
spec.loader.exec_module(packaging)


class PackagingTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / 'source'
        self.names = json.loads((ROOT / 'scripts/package-files.json').read_text())['source']
        for name in self.names:
            target = self.root / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text('public fixture\n')
        (self.root / 'plugins/secret-bridge/plugin.json').write_text('{"version":"0.1.0"}')
        self.catalog()
        self.output = Path(self.temp.name) / 'packages'

    def catalog(self):
        (self.root / 'scripts/package-files.json').write_text(json.dumps({'source': self.names}))

    def test_unknown_files_never_enter_either_archive(self):
        marker = b'SYNTHETIC-PRIVATE-NOT-A-CREDENTIAL'
        for name in ['private-account.md', 'docs/approval/verification.json', 'plugins/secret-bridge/dist/private.txt', 'plugins/secret-bridge/skills/save-secret/private.txt', 'plugins/secret-bridge/assets/private.txt', '.env', '.aws/credentials']:
            file = self.root / name
            file.parent.mkdir(parents=True, exist_ok=True)
            file.write_bytes(marker)
        source, release, sums = packaging.package(self.root, self.output)
        for file in [source, release]:
            with zipfile.ZipFile(file) as archive:
                self.assertTrue(archive.namelist())
                self.assertFalse(any(marker in archive.read(name) for name in archive.namelist()))
        with zipfile.ZipFile(source) as archive:
            self.assertEqual(set(archive.namelist()), {'codex-secret-bridge/' + n for n in self.names})
        with zipfile.ZipFile(release) as archive:
            self.assertIn('dist/server.mjs', archive.namelist())
            self.assertIn('skills/save-secret/SKILL.md', archive.namelist())
            self.assertIn('assets/logo.png', archive.namelist())
            self.assertIn('assets/icon.png', archive.namelist())
            self.assertIn('assets/icon-dark.png', archive.namelist())
            self.assertIn('assets/golden-gate-lock.png', archive.namelist())
        self.assertEqual(sums.read_text(), ''.join(f'{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.name}\n' for p in [source, release]))

    def test_missing_approved_file_fails_before_creating_archives(self):
        (self.root / 'README.md').unlink()
        with self.assertRaisesRegex(ValueError, 'missing'):
            packaging.package(self.root, self.output)
        self.assertFalse(self.output.exists())

    def test_symlink_file_and_parent_are_rejected(self):
        original = self.root / 'README.md'
        original.unlink()
        original.symlink_to(ROOT / 'README.md')
        with self.assertRaisesRegex(ValueError, 'symlinks'):
            packaging.package(self.root, self.output)
        original.unlink()
        original.write_text('public fixture')
        # A listed file beneath a directory symlink must also be refused.
        # Use a separate listed directory with a single file.
        (self.root / 'links').symlink_to(ROOT / 'docs', target_is_directory=True)
        self.names.append('links/TRACKING.md')
        self.catalog()
        with self.assertRaisesRegex(ValueError, 'symlinks'):
            packaging.package(self.root, self.output)

    def test_invalid_or_sensitive_catalog_entries_are_rejected(self):
        for name in ['../private.txt', '/tmp/private.txt', '.env', 'node_modules/private.txt', 'docs\\private.txt', 'docs//private.txt']:
            with self.subTest(name=name):
                self.names.append(name)
                self.catalog()
                with self.assertRaisesRegex(ValueError, 'Unsafe'):
                    packaging.package(self.root, self.output)
                self.names.pop()

    def test_offline_source_archive_remains_repackagable(self):
        source, _, _ = packaging.package(self.root, self.output)
        extracted = Path(self.temp.name) / 'extracted'
        with zipfile.ZipFile(source) as archive:
            archive.extractall(extracted)
        rebuilt, _, _ = packaging.package(extracted / 'codex-secret-bridge', Path(self.temp.name) / 'rebuilt')
        with zipfile.ZipFile(source) as first, zipfile.ZipFile(rebuilt) as second:
            self.assertEqual(first.namelist(), second.namelist())
            for name in first.namelist():
                self.assertEqual(first.read(name), second.read(name))


if __name__ == '__main__':
    unittest.main()
