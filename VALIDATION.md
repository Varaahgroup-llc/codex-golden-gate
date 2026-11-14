# Validation — November 14, 2026

Tested using Node.js 24.7.0 on macOS. Minimum advertised runtime: Node.js 22; that version has not separately been exercised.

- Build: self-contained ESM server and third-party notices generated successfully.
- Core, adapter and stdio MCP suite: 16 tests passed.
- Browser integration: one real Chromium test passed, covering encrypted save, secret-free bridge arguments, form clearing, lack of unsupported modal controls, and cancellation without writing.
- Bundled skill: Skill Creator validator passed.
- A copy of the server bundle was run from an isolated temporary folder without node_modules. Discovery, UI resources, widget-only capabilities, encrypted saving, receipt polling, cancellation and replay rejection passed through the official MCP SDK client.

All entry values were synthetic. Local files and test repositories were temporary and cleaned up. Cloud CLI boundaries were mocked; no live GitHub/AWS/Azure secret was saved or read. The browser test used an MCP Apps host harness; it was not a Codex desktop installation or a native modal test.

Outstanding before advertising public production readiness: clean target-client installation/rendering/approval checks, actual host modal behavior, disposable live provider tests, minimum Node.js runtime verification, independent security review, publisher identity/legal/branding metadata, and directory eligibility/review if using the public OpenAI directory.
