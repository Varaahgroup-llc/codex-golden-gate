# Release checklist

- [ ] Verify GG scope, classified changes, dependencies and completed slices. Reconcile all first-parent changes since the previous tagged baseline with the bundle. Exclude unresolved acceptance claims.
- [ ] Review version proposal, migrations and Unreleased notes. Freeze candidate commit and package/lock metadata. Verify against previously reserved versions.
- [ ] Pass PR review, CI matrix, secret scan and dependency audit. Match source hashes and suite results to a clean SHA.
- [ ] Generate candidate packages, manifest, notes and checksum index. Verify reproduction after extraction. Preserve CI evidence before artifact retention expires.
- [ ] Execute applicable native, live-provider and independent security gates with isolated configuration. Record exact artifacts and evidence. Record rollback rehearsal in a disposable profile.
- [ ] Review every gate and gather scoped owner authorization before tagging or distribution. Inspect exact-main CI and the protected draft environment.
- [ ] Create the authorized immutable tag, verify draft asset hashes, review notes and owner decision. Publish only within the approved channel and scope.
- [ ] Download and verify the published bytes, install and smoke test. Record post-release status, public URL, checksums and private approval reference. Archive the completed record and reconcile GG release/issue states.

[Approval policy](../governance/RELEASE_APPROVAL_POLICY.md) · [Release record](RELEASE_TEMPLATE.md)
