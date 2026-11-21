# Software release management

Effective 21 November 2026. The Golden Gate maintainer owns this policy for every distributed change, including dependencies, security, workflows and behavior-related documentation. [Verified starting point](RELEASE_BASELINE.md)

| Stage | Evidence required to advance |
| --- | --- |
| Backlog and development | Search GG for existing work. Record scope, owner, risk, acceptance criteria, target and change class. [Change management](CHANGE_MANAGEMENT.md) |
| Integration | Short-lived branch, PR, review, CI and evidence on the merged SHA. [Branch strategy](BRANCHING_STRATEGY.md) |
| Candidate | Select completed slices, check dependencies and exclusions, propose a version, freeze the commit, change records, lockfile and ZIP digests. [Versioning](VERSIONING_POLICY.md) |
| Isolated validation | Reproduce ZIPs, exercise core/stdio/Chromium with synthetic fixtures and mocked CLI identities. Collect security evidence. |
| Staging | Use the exact ZIPs in a disposable local profile and dedicated provider sandbox. Record host, OS, Node, SHA, hashes and outcome. Native staging requires an actual host run. |
| Decision and distribution | Classify every gate and record explicit owner authorization per channel. The protected GitHub workflow creates drafts only. [Approval policy](RELEASE_APPROVAL_POLICY.md) |
| Verification and archive | Verify downloads against approved checksums, install into a clean profile, run the authorized smoke test, archive the record and only then reconcile Jira. [Release checklist](../releases/RELEASE_CHECKLIST.md) |

The current release unit is one local plugin and its source marketplace archive. A hosted service or independently versioned integration needs its own approved contract and recovery procedure before introduction. Development, synthetic test, disposable native staging and repository distribution have separate configuration and credentials. Do not copy credentials between them.

Use [hotfix policy](HOTFIX_POLICY.md) for emergencies and [rollback policy](ROLLBACK_POLICY.md) for recovery. NIST SSDF informs review and evidence retention. SLSA informs source, dependency and build provenance. The generated hashes establish artifact identity. Independent attestations and a formal compliance assessment require separate evidence. [NIST SSDF](https://csrc.nist.gov/projects/ssdf) · [SLSA](https://slsa.dev/)
