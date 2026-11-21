# Golden Gate distribution and verification

The release unit comprises the plugin ZIP and marketplace source ZIP. CI stages review artifacts. An authorized annotated tag runs the existing draft workflow. A separate manual dispatch promotes an approved draft to a public GitHub release. The OpenAI directory has its own GG-2, GG-3 and GG-7 gates and authorization.

## Repository controls

The 21 November 2026 GitHub readback showed active main and version-tag rules. Main requires one approving review, dismissed stale approvals, resolved threads and all four strict Actions matrix checks. Force pushes and deletion are blocked. The live rule had code-owner review disabled, with one write collaborator. Add a second eligible security reviewer with write access, include the approved reviewer in CODEOWNERS, merge the file through review, and enable **Require review from Code Owners** in the main ruleset. Compare settings with the versioned rules under .github/rulesets. The release-draft environment has a required reviewer, no administrator bypass and a single v* tag policy. Self-review is possible there.

GitHub-hosted secret scanning, push protection and Dependabot security updates were disabled at discovery. An administrator can enable them in the repository's Security settings. CI independently audits the lockfile and scans Git history, outgoing evidence and nested release ZIPs. A scanner failure blocks that upload. Reviewers must also inspect fixture and artifact scope. Build evidence includes automated suites using synthetic fixtures. The CycloneDX inventory covers locked npm build and runtime dependencies. Bundled runtime licenses are in dist/THIRD_PARTY_LICENSES.txt.

## Publication decision

1. Complete the applicable [native UAT](../approval/UAT_CASES.md), independent security review, architecture disposition and recovery rehearsal for the exact tagged commit. Record the actual reviewer, build, OS, version, artifact hashes, scope and decision in GG. Explicitly approve the named GitHub distribution channel. A failed or pending applicable gate holds the release in draft.
2. The protected draft workflow signs SHA256SUMS.txt using GitHub workload identity and verifies the attestation against the tag, commit and workflow. Archive the draft guard, workflow URL, manifest, SBOM, notes, test evidence and checksums. Keep private acceptance evidence in Jira.
3. A repository administrator must create **release-publication**, choose the authorized maintainer reviewer, disable administrator bypass and select exactly one deployment branch rule for main. Restrict repository release write access to authorized maintainers. Direct publication by a repository administrator remains an administrative capability.
4. Submit a reviewed main PR adding docs/releases/approvals/vX.Y.Z.json. The verifier requires tag, commit (40 lowercase hex), inventorySHA256 (SHA-256 of the signed checksum file), channel (github-release), decision (APPROVED), and an evidence object with nativeUAT, security, rollback, architecture and ownerApproval. Each value is a permanent GG issue comment URL ending in ?focusedCommentId=NUMBER. Reviewers verify the actual decisions and applicability to this artifact. Keep private data out of the file. Never generate an approval from CI.
5. The authorized maintainer manually dispatches **Approved GitHub publication** on main with the exact tag. Inspection verifies the decision, environment, annotated tag, signed inventory, manifest, guard and every downloaded asset. Following separate environment approval the job repeats verification, promotes the existing draft and downloads the public assets again. An old draft lacking this evidence cannot pass. On verification failure preserve the run and open a GG incident. Never retry a publication blindly.
6. Install the verified public marketplace archive in a clean profile, repeat the scoped smoke test and record the run and hashes in GG-9 and the release register. The daily Codex reconciliation compares GitHub metadata with GG-9. It uses connected accounts, retains unresolved UAT and review status, and requires the local scheduler to be available. It cannot authorize publication or advance Jira status.

## CLI recovery rehearsal

Select a previously verified, compatible marketplace source ZIP and the corresponding SHA-256 from a trusted record. To exercise installation and rollback in a new disposable profile, run the following command with those paths and digests.

```sh
python3 scripts/rehearse_install.py \
  --previous "$PRIOR_SOURCE_ZIP" --previous-sha256 "$PRIOR_SHA256" \
  --candidate "$CANDIDATE_SOURCE_ZIP" --candidate-sha256 "$CANDIDATE_SHA256"
```

The script uses a temporary home, verifies each archive before installation, and switches versions using the native CLI remove and add commands. It checks enabled state, installed bundle bytes, MCP initialization and discovery, and preservation of a synthetic dotenv file. This exercises manual recovery in an isolated profile. Native desktop rendering, real provider access and consequential recovery on user installations require separate acceptance and authorization. Record the prior version, restored version, incident, corrective action and verification in GG.
