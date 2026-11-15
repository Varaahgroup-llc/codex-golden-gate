# Validation — updated November 15, 2026

## Test evidence and release-management follow-up (GG-6/GG-7/GG-9)

On November 15, the updated suite passed **25 core/adapter/stdio MCP tests, one Chromium iframe integration test and 27 Python tests** on macOS arm64, Node 24.7.0 and Python 3.13.7. Nine additional core/adapter tests cover exact expiry, malformed/extra envelope fields, in-flight cancellation/status, terminal write failures, byte/control limits, reviewed-file replacement, hardlinks/locks, parser cleanup and provider output/timeout suppression. Eight new release-guard tests cover accepted fixtures and blocked source/CI/protection/release-reuse decisions. No runtime or secret-routing behavior changed in this work.

The full evidence runner passed build, committed-bundle comparison, Node/browser/Python suites and release metadata checks. Strict preflight returned 1 with **nine readiness findings**, retained as a blocker report rather than represented as test failure or approval. The first evidence run caught a catalog path named `release` colliding with the existing output exclusion; the documentation moved to `docs/releases`, and the full rerun passed. Exact-file source/plugin ZIP packaging was verified after the correction. Local records include dirty-source hashes; clean committed CI evidence is preferred for review.

The read-only release guard was exercised against the existing immutable v0.1.0 tag and refused both package-version mismatch and existing-release reuse. GitHub API readback confirmed the new release-draft environment's required reviewer, administrator-bypass prohibition and v* tag-only policy. The tag-to-draft workflow itself is **not run end-to-end**: no new tag or release was created. Required review of these release-script changes is still a separate maintainer action.

Detailed [UAT cases](docs/approval/UAT_CASES.md) contain 27 acceptance procedures, including the primary in-Codex entry requirement, eight initial-review cases, safety/lifecycle checks and release checks. None has been marked passed without native execution. Automated/browser evidence does not certify Codex's renderer, an approved credential-entry mechanism, live providers, independent security review or OpenAI eligibility. [Requirements](docs/approval/REQUIREMENTS.md) and [support status](docs/approval/SUPPORT_STATUS.md) record the November 15 checks and preserved product goal.

Tested locally using Node.js 24.7.0 on macOS. [Initial public CI](https://github.com/Varaahgroup-llc/codex-golden-gate/actions/runs/43655774411) passed the full build, reproducible-bundle check, 16 core/adapter/MCP tests, browser integration, and release metadata validation on macOS and Ubuntu using Node.js 22 and 24.

- Build: self-contained ESM server and third-party notices generated successfully.
- Core, adapter and stdio MCP suite: 16 tests passed.
- Browser integration: one real Chromium test passed, covering encrypted save, secret-free bridge arguments, form clearing, lack of unsupported modal controls, and cancellation without writing.
- Bundled skill: Skill Creator validator passed.
- A copy of the server bundle was run from an isolated temporary folder without node_modules. Discovery, UI resources, widget-only capabilities, encrypted saving, receipt polling, cancellation and replay rejection passed through the official MCP SDK client.

The original public marketplace and plugin were installed successfully through Codex CLI 0.167.0-alpha.4.1 using the native `plugin marketplace add` and `plugin add` commands. That historical installed result identified secret-bridge@varaahgroup-secret-bridge version 0.1.0. The actual Codex chat form and modal have not been exercised.

The Golden Gate rename was also installed through native Codex CLI from reviewed/tested rename commit 1948c9220fa270ec39a5d007567dc21d996d4ced using the Git marketplace's --ref option. Installation returned golden-gate@varaahgroup-golden-gate version 0.2.0, and plugin listing confirmed installed=true and enabled=true. The replaced Secret Bridge plugin and marketplace entries were removed as part of the requested full rename. This is a pinned preview installation pending source review/merge, not an approved directory listing or proof of native chat rendering. Follow MIGRATION.md and move the marketplace to the reviewed default branch after merge.

All entry values were synthetic. Local files and test repositories were temporary and cleaned up. Cloud CLI boundaries were mocked; no live GitHub/AWS/Azure secret was saved or read. The browser test used an MCP Apps host harness rather than Codex's renderer.

Outstanding before advertising production readiness: clean target-client rendering/approval checks, actual host modal behavior, disposable live provider tests, independent security review, remaining directory submission/legal/branding requirements, and OpenAI directory eligibility/review.

## Approval-readiness branch checks

The GG-6/GG-7/GG-8 follow-up upgrades Zod to 4.6.7 and rebuilds the server bundle. On November 14, 2026, local validation passed 16 core/adapter/MCP tests, one Chromium iframe integration test, ten Python readiness/packaging tests, release metadata validation and ZIP creation. A fresh `npm audit --json --ignore-scripts` reported zero known vulnerabilities. These checks do not replace an independent audit or native Codex reviewer tests.

The packaging tests verify that synthetic private files outside the exact public-file catalog cannot enter either ZIP, including files placed beside runtime and skill files. They also cover missing files, symlink files/parents, unsafe catalog paths, checksums and repackaging an extracted offline source archive. New public files require a reviewed catalog entry. No content scanner can guarantee that approved source files themselves contain no sensitive information; maintainers must review them.

The strict submission preflight still returns **NOT READY** with seven unresolved evidence gates. Owner verification is in progress on the official phone flow; no successful OpenAI verification state has been observed. Human support eligibility/local-MCP clarification remains pending. No new release, directory submission or approval is implied by these checks.

The submission-preparation follow-up includes earlier 256px geometric studies and the current 1254px Golden Gate Bridge/central-padlock PNG used by all listing/composer references. Release validation checks PNG signatures/dimensions/size and packaging tests check inclusion in both exact-file archives. The final installable ZIP was inspected for its actual manifest, image files, explicit unrestricted country selection and current no-checkout commerce scope. The terms remain clearly marked as a draft with no `termsOfServiceURL`; no effective/published terms or completed native reviewer cases are claimed.

The MCP-preflight follow-up passes 19 Python tests (14 submission checks and five packaging tests). Regression coverage now prevents missing terms from being hidden by manually verified flags, distinguishes skills-only metadata from MCP review preparation, rejects malformed/credential-bearing URLs, and checks declared case counts/positive expectations, recording presence and release notes. Five positive/three negative draft cases and release notes are included in the actual manifest; descriptions explicitly say DRAFT / NOT RUN. Strict preflight now reports nine findings: two missing public materials (terms/recording URLs) and seven unresolved manual gates. These tests certify local preparation behavior only.

The stdio protocol suite also compares each draft case's exact declared tool names against actual MCP discovery for the source, built bundle and isolated release. App-only visibility is explained in case text rather than appended to the tool names. This checks the review contract, not execution of the native reviewer scenarios.
