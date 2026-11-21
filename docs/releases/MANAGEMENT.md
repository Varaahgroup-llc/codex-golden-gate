# Golden Gate release management

Tracking: GG-9. Scope: repeatable test evidence and maintainer-reviewed GitHub draft releases. OpenAI directory approval and public release publication are separate decisions. No new tag or release is created by implementing this infrastructure.

## Flow and controls

1. Implement on a GG-linked branch and open a PR. CI on macOS/Linux and Node 22/24 builds, checks the committed bundle, runs core/adapter/stdio/browser/Python tests, validates metadata and records strict submission-preflight findings.
2. Each job uploads `evidence-<os>-node<version>-<attempt>` for 30 days, including failing checks when available. JUnit files, Python logs, source-file hashes, source commit, dirty status, runtime, exit codes and SHA-256 checksums distinguish actual automated results from native UAT. Download evidence before expiry when needed for audit/review. These logs use synthetic fixtures; never add real secrets or private account data to tests.
3. Maintainer reviews the exact PR, test evidence, UAT status, changelog and scope. MAINTAINING.md requires this review for release scripts/dependencies/secret handling. Merge, then wait for successful **main push CI on that exact commit**. PR CI alone is insufficient.
4. Only after explicit candidate-release authorization, create an annotated immutable `vX.Y.Z` tag at the reviewed commit. Version fields must agree. Never move/reuse an existing tag, including v0.1.0. A failed candidate gets a new version/tag after repair.
5. The tag workflow's read-only `verify` job checks annotation, version, main ancestry, exact-commit latest CI, absence of an existing release and a required-reviewer environment with administrator bypass disabled. API/auth errors fail closed. It reruns checks and stages source/plugin ZIPs, release-guard JSON, test-evidence ZIP and checksums.
6. The separate `draft` job requires the **release-draft** environment approval. It rechecks the guards after approval and verifies downloaded artifact hashes. Only this job has contents-write permission. It creates a draft, with 0.x/prerelease versions marked prerelease. Nothing publishes automatically. If a release already exists, the workflow stops instead of clobbering it. A partial draft-creation failure requires manual inspection; do not blindly rerun/overwrite it.
7. Review the draft and recorded UAT/reviewer/legal/security results. Publish only after a separate explicit maintainer decision with accurate compatibility claims. A technically green preview is not directory eligibility. The current secret-entry prototype remains blocked for directory submission.

Repository administrators can change workflows or environment settings; this is governance and auditability, not protection against a malicious administrator. Guard API checks supplement GitHub environment enforcement. Do not treat a hardcoded allow flag or a documentation checkbox as approval.

## Environment configuration

On November 15, 2026, GitHub API readback verified environment **release-draft**, required reviewer **bharatk1207**, administrator bypass disabled and a selected **tag `v*`** deployment policy. No environment secret was added. Self-review is permitted because only the current maintainer is configured; this is a human review gate, not a claimed two-person control. Add a second authorized maintainer before adopting independent-review requirements. The environment was verified again on 21 November. PR #17 integrated the original draft workflow. Further workflow changes take effect on main after review and merge.

Check settings before each release or after repository visibility/plan changes. An environment mentioned in YAML can otherwise be created without protections; the guard explicitly refuses that state. Settings reference: [GitHub environments](https://docs.github.com/en/actions/how-tos/deploy/configure-and-manage-deployments/manage-environments).

## Local evidence reproduction

```sh
# From repository root, with dependencies and a supported Chromium installed:
python3 scripts/collect_test_evidence.py --output /private/tmp/golden-gate-evidence-RUN_ID
python3 scripts/package.py --output /private/tmp/golden-gate-packages-RUN_ID
```

Choose a fresh evidence directory. The runner uses only fixed local build/test commands and never creates releases, tags or provider secrets. A strict preflight exit 1 with parseable NOT READY findings is retained as an approval blocker, while technical checks can pass. Inspect `preflight.json` separately from `technicalChecksPassed`; native UAT/live-provider fields remain false. Source hashes identify uncommitted runs; prefer clean committed CI evidence for review. CI synthetic logs are publicly downloadable in this public repository; inspect contents before attaching any additional evidence. Do not run the suite with production fixtures or paste private logs into artifacts.

## Failed releases and rollback

- Before draft creation: retain failing evidence; fix through another reviewed PR. Never force a tag to a different commit.
- Existing draft/partial creation: inspect assets and workflow history. Repair only with explicit maintainer authorization; this pipeline never overwrites existing releases automatically.
- Bad published candidate: mark release notes with the defect and the supported fallback; coordinate withdrawal/advisory if needed. Publish a fixed version under a new tag after validation.
- Client rollback: in a disposable profile first, select a known reviewed version/commit via the supported marketplace/installation flow, restart as needed, and run lifecycle UAT R6. Do not erase or rotate destination secrets as a rollback side effect. Reopen a fresh form; previous in-memory capabilities are process-bound.

Release evidence, source/tag hashes, checksums, CI URL, maintainer approval and UAT outcomes belong in a GG-9 comment and release record. Keep OpenAI verification/allowlisting/approval in their own GG-2/GG-3/GG-7 records. R1–R6 in UAT_CASES.md are **not run end-to-end** until an explicitly authorized candidate exercises them; guard unit tests alone do not certify the entire workflow.

## Candidate rehearsal

Use a clean GG checkout, Node 22/24, lockfile-installed dependencies, a supported Chromium, Python 3.9+ and checksum-verified Gitleaks 8.24.3. Set GG_GITLEAKS to its executable if it is outside PATH. The candidate scan needs access to the npm advisory registry. From the repository root run these commands with fresh output paths outside the checkout (or the ignored evidence and release directories).

```sh
python3 scripts/collect_test_evidence.py --output evidence
python3 scripts/candidate.py --evidence evidence --output release
(cd release && shasum -a 256 -c SHA256SUMS.txt)
```

The CI workflow rehearses on bundle changes and manual dispatch. Ordinary PRs still run traceability, syntax, security, packaging and matrix checks. A green rehearsal with outstanding product gates is eligible for engineering review only. For a new bundle update bundle.json with the previous immutable tag, previous version proposal and its commit, compatibility rationale, included change records and limitations. Reconcile legacy commits without change records individually using full SHA and verified PR. An omitted integration commit blocks the candidate. Review the generated CHANGELOG.md entry for incorporation into the repository on release. Archive the manifest, notes, ZIPs, checksums and associated test evidence together. Any source or scope edit invalidates previous acceptance.

[Permanent policy](../governance/SOFTWARE_RELEASE_MANAGEMENT.md) · [Release register](RELEASE_REGISTER.md)
