# Changelog

## [Unreleased]

### Added

- GG-5 adds local Cloudflare Worker setup from a selected Wrangler configuration, with environment-specific destination review and protection against shadowing existing dotenv settings.

## 0.3.0 — Inline paste slot (prepared, unreleased)

- Replaced the expanded entry layout with a compact approval-style paste slot, visible destination/identity, masking, Save and Cancel. Save confirms delivery/replacement; pasting alone never submits.
- Removed the optional modal control, declared inline-only rendering and added content-size notifications. The host still controls its tool-row presentation.
- Preserved encryption, app-only submission, immutable destinations, expiry, receipts and cancellation. Kept multiline entry in place and prevented line-break loss when switching modes.
- Versioned the UI resource as entry-v2 to avoid stale component caches and extended browser/protocol regression checks.
- Personal Vault is an existing native Codex Cloud facility; a third-party API for local inline entry/destination routing is not established. Native candidate rendering, directory eligibility and release approval remain pending.

## 0.2.0 — Golden Gate rename (prepared, unreleased)

- Renamed the product, repository, plugin, marketplace, local server and source path to Golden Gate / golden-gate.
- Renamed Jira to Golden Gate with key GG; previous SBR issue keys remain historical aliases.
- Renamed the existing OpenAI publishing project; publisher identity and verification requirements remain the same.
- Added migration instructions, updated package/installation references, and retained the original artwork-generation prompt and immutable v0.1.0 history.
- Directory eligibility, owner verification, native reviewer execution and independent security/live-provider evidence remain pending. No new release or directory approval is claimed.

## 0.1.0 — Original Secret Bridge preview

- Added an MCP Apps secret-entry form with destination and signed-in identity review.
- Added encrypted UI submissions, one-use forms, expiry, cancellation and secret-free receipts.
- Added dotenv, GitHub Actions, existing AWS Secrets Manager and Azure Key Vault adapters.
- Added the bundled save-secret skill, self-contained desktop server and downloadable packages.
- Added automated checks, pinned CI actions, release packaging, dependency update configuration and maintainer guidance.

Core behavior and an isolated MCP installation are tested. Native Codex UI/modal behavior and live cloud writes remain unverified. macOS/Linux only; Node.js 22+ and an MCP Apps-compatible local host are required.
