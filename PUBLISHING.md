# Distribution

## Current policy gate

The raw-credential-entry prototype is not ready for a directory submission. The current directory guidelines prohibit processing API keys/passwords. Resolve SBR-2 with written clarification or an approved redesign before asserting eligibility. Track the standalone project and prerequisites in docs/TRACKING.md. Business verification and local-MCP allowlisting remain separate requirements.

An authorized eligibility inquiry was escalated to an OpenAI support specialist on November 14, 2026. See docs/approval/SUPPORT_STATUS.md. This is not an approval or listing submission.

Plugin Creator's official preparation workflow has been applied to the current source; see [the preparation record](docs/approval/SUBMISSION_PREPARATION.md). Proposed icons and publication-country scope are packaged. The [terms draft](docs/approval/TERMS_DRAFT.md) still needs owner review and a verified published URL; it is not an effective terms page. Current-version commerce metadata describes the existing no-checkout behavior; future payment plans remain a separate eligibility/product decision.

Run `python3 scripts/preflight_submission.py` before attempting portal submission. It exits nonzero while known evidence gates are unresolved. `--report-only` is for displaying blockers in CI and does not grant eligibility. This limited offline check does not replace OpenAI package/skill scans, verification, policy attestations or human review. Proposed reviewer scenarios and unverified evidence are in docs/approval/REVIEW_PLAN.md.

For this single-MCP package the checker also requires the four listing URLs, five positive/three negative case declarations, a recording URL and release notes. It accepts the declared draft cases only as expectations: no case has been certified in native Codex. The current output explicitly reports the missing Terms of Service and recording URLs, as well as seven unresolved manual gates. URL syntax validation does not establish public page content, video playback, eligible local-MCP access or policy approval.

## Repository distribution

The standalone project home is `Varaahgroup-llc/codex-secret-bridge`. The root `.agents/plugins/marketplace.json` catalog points to `plugins/secret-bridge`; the built `dist/server.mjs`, notices, skill, and manifests must be included. After approving installation, users can register it with `codex plugin marketplace add Varaahgroup-llc/codex-secret-bridge` and install with `codex plugin add secret-bridge@varaahgroup-secret-bridge` in supported clients. See INSTALL.md for the approval flow.

For a release from source, run the plugin build and all tests, then `python3 scripts/package.py --output /absolute/output/folder`. It produces an installable plugin ZIP, a source/marketplace ZIP, and SHA-256 checksums. Both archives use the exact public-file catalog in `scripts/package-files.json`; adding a new public file requires an explicit catalog review. Unknown workspace files are excluded, and missing/symlinked catalog files fail packaging. Keep secrets out of approved public files too. Rebuild before packaging so the bundle matches its source. See [security preparation](docs/approval/SECURITY_PREPARATION.md) for findings and limitations.

## Universal OpenAI Plugin Directory

This is a **desktop-only local stdio MCP plugin**. Current official documentation limits local MCP submissions to approved partners. The submitting organization must be allowlisted through its OpenAI representative before submission. Repo distribution and a local marketplace do not publish a universal listing.

Before requesting review:

1. Verify a clean desktop installation, inline rendering, host permission handling, cancellation, expiry, encrypted saving, and supported modal behavior. Include target client/version evidence. The built-in browser harness is not that evidence.
2. Validate each advertised live cloud provider in disposable test resources using synthetic secrets. The existing tests cover CLI boundaries without making cloud writes.
3. Complete security review and resolve any findings. Check runtime sandbox/filesystem restrictions in the target client. Never broaden permissions silently to make a test pass.
4. Verify the publisher/author, repository URL and privacy-policy URL in `plugins/secret-bridge/plugin.json`. Add verified submission contact, applicable terms and branding required by the portal; do not invent verification or eligibility.
5. With confirmed submission access and publisher identity, upload the plugin-root ZIP using the portal's desktop-only flow. Submit for review, then publish after approval.

For a future remote/multi-user plugin, create a separate authenticated HTTPS backend with per-user OAuth, tenant/destination authorization, restricted CSP, no body logging, expiring submission capabilities and a suitable privacy policy. Do not expose this local stdio server or share one user's provider login across users.

Official references:

- [Package and distribute plugins](https://developers.openai.com/plugins/build/plugins)
- [Desktop-only submission and allowlisting](https://developers.openai.com/plugins/deploy/desktop-only)
- [MCP Apps UI](https://developers.openai.com/plugins/build/chatgpt-ui)
- [Modal API and host extensions](https://developers.openai.com/plugins/reference#open-a-modal)
