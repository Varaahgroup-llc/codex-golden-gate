# Validation — November 14, 2026

Tested locally using Node.js 24.7.0 on macOS. [Initial public CI](https://github.com/Varaahgroup-llc/codex-secret-bridge/actions/runs/43655774411) passed the full build, reproducible-bundle check, 16 core/adapter/MCP tests, browser integration, and release metadata validation on macOS and Ubuntu using Node.js 22 and 24.

- Build: self-contained ESM server and third-party notices generated successfully.
- Core, adapter and stdio MCP suite: 16 tests passed.
- Browser integration: one real Chromium test passed, covering encrypted save, secret-free bridge arguments, form clearing, lack of unsupported modal controls, and cancellation without writing.
- Bundled skill: Skill Creator validator passed.
- A copy of the server bundle was run from an isolated temporary folder without node_modules. Discovery, UI resources, widget-only capabilities, encrypted saving, receipt polling, cancellation and replay rejection passed through the official MCP SDK client.

The public marketplace and plugin were installed successfully through Codex CLI 0.167.0-alpha.4.1 using the native `plugin marketplace add` and `plugin add` commands. The installed result identified secret-bridge@varaahgroup-secret-bridge version 0.1.0. The current chat did not reload the newly installed tool set; the actual Codex chat form and modal have not been exercised.

All entry values were synthetic. Local files and test repositories were temporary and cleaned up. Cloud CLI boundaries were mocked; no live GitHub/AWS/Azure secret was saved or read. The browser test used an MCP Apps host harness rather than Codex's renderer.

Outstanding before advertising production readiness: clean target-client rendering/approval checks, actual host modal behavior, disposable live provider tests, independent security review, remaining directory submission/legal/branding requirements, and OpenAI directory eligibility/review.
