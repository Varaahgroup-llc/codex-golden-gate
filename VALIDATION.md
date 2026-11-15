# Validation — November 14, 2026

Tested locally using Node.js 24.7.0 on macOS. [Initial public CI](https://github.com/Varaahgroup-llc/codex-golden-gate/actions/runs/43655774411) passed the full build, reproducible-bundle check, 16 core/adapter/MCP tests, browser integration, and release metadata validation on macOS and Ubuntu using Node.js 22 and 24.

- Build: self-contained ESM server and third-party notices generated successfully.
- Core, adapter and stdio MCP suite: 16 tests passed.
- Browser integration: one real Chromium test passed, covering encrypted save, secret-free bridge arguments, form clearing, lack of unsupported modal controls, and cancellation without writing.
- Bundled skill: Skill Creator validator passed.
- A copy of the server bundle was run from an isolated temporary folder without node_modules. Discovery, UI resources, widget-only capabilities, encrypted saving, receipt polling, cancellation and replay rejection passed through the official MCP SDK client.

The original public marketplace and plugin were installed successfully through Codex CLI 0.167.0-alpha.4.1 using the native `plugin marketplace add` and `plugin add` commands. That historical installed result identified secret-bridge@varaahgroup-secret-bridge version 0.1.0. The actual Codex chat form and modal have not been exercised.

All entry values were synthetic. Local files and test repositories were temporary and cleaned up. Cloud CLI boundaries were mocked; no live GitHub/AWS/Azure secret was saved or read. The browser test used an MCP Apps host harness rather than Codex's renderer.

Outstanding before advertising production readiness: clean target-client rendering/approval checks, actual host modal behavior, disposable live provider tests, independent security review, remaining directory submission/legal/branding requirements, and OpenAI directory eligibility/review.

## Approval-readiness branch checks

The GG-6/GG-7/GG-8 follow-up upgrades Zod to 4.6.7 and rebuilds the server bundle. On November 14, 2026, local validation passed 16 core/adapter/MCP tests, one Chromium iframe integration test, ten Python readiness/packaging tests, release metadata validation and ZIP creation. A fresh `npm audit --json --ignore-scripts` reported zero known vulnerabilities. These checks do not replace an independent audit or native Codex reviewer tests.

The packaging tests verify that synthetic private files outside the exact public-file catalog cannot enter either ZIP, including files placed beside runtime and skill files. They also cover missing files, symlink files/parents, unsafe catalog paths, checksums and repackaging an extracted offline source archive. New public files require a reviewed catalog entry. No content scanner can guarantee that approved source files themselves contain no sensitive information; maintainers must review them.

The strict submission preflight still returns **NOT READY** with seven unresolved evidence gates. Owner verification is in progress on the official phone flow; no successful OpenAI verification state has been observed. Human support eligibility/local-MCP clarification remains pending. No new release, directory submission or approval is implied by these checks.

The submission-preparation follow-up includes earlier 256px geometric studies and the current 1254px Golden Gate Bridge/central-padlock PNG used by all listing/composer references. Release validation checks PNG signatures/dimensions/size and packaging tests check inclusion in both exact-file archives. The final installable ZIP was inspected for its actual manifest, image files, explicit unrestricted country selection and current no-checkout commerce scope. The terms remain clearly marked as a draft with no `termsOfServiceURL`; no effective/published terms or completed native reviewer cases are claimed.

The MCP-preflight follow-up passes 19 Python tests (14 submission checks and five packaging tests). Regression coverage now prevents missing terms from being hidden by manually verified flags, distinguishes skills-only metadata from MCP review preparation, rejects malformed/credential-bearing URLs, and checks declared case counts/positive expectations, recording presence and release notes. Five positive/three negative draft cases and release notes are included in the actual manifest; descriptions explicitly say DRAFT / NOT RUN. Strict preflight now reports nine findings: two missing public materials (terms/recording URLs) and seven unresolved manual gates. These tests certify local preparation behavior only.

The stdio protocol suite also compares each draft case's exact declared tool names against actual MCP discovery for the source, built bundle and isolated release. App-only visibility is explained in case text rather than appended to the tool names. This checks the review contract, not execution of the native reviewer scenarios.
