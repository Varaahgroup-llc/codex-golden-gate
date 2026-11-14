# Contributing

Varaahgroup-llc maintains Secret Bridge. Use GitHub issues for reproducible bugs and narrowly scoped feature requests. Use private security reporting for vulnerabilities. All test values and examples must be synthetic.

Create a branch, make the smallest complete change, and open a pull request. Run the build and tests from plugins/secret-bridge:

```bash
npm ci --ignore-scripts
npm run build
npm test
npm run test:ui
```

On Linux, first run `npx playwright install --with-deps chromium`. On macOS the UI test uses installed Google Chrome; a trusted Chromium executable can be supplied with SECRET_BRIDGE_TEST_BROWSER.

Commit regenerated dist/server.mjs and dist/THIRD_PARTY_LICENSES.txt with source changes. Do not edit generated files directly. CI checks Node.js 22 and 24 on macOS and Linux, the browser flow, metadata consistency and release packaging.

Keep secret values out of plaintext tool arguments, model context, receipts, widget state, logs and CLI arguments. Preserve destination/identity review, short-lived capabilities, authenticated encryption, cancellation, expiry and one-write enforcement. Adding a provider requires its official API/CLI references, exact scope, mocked boundary tests, safe error handling and disposable live validation evidence before claiming it is verified. Do not use production resources or live credentials in CI.

Maintainers review changes affecting cryptography, adapters, installation or permissions before merging. A passing harness does not establish native Codex UI compatibility: include the client version and clean-install evidence for those claims. Use Semantic Versioning and record user-visible changes in CHANGELOG.md. Maintainers publish releases following MAINTAINING.md.
