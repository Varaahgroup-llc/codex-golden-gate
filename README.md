# Golden Gate

Golden Gate is the new name for Secret Bridge. The 0.2.0 rename source was merged in PR #14; see [migration instructions](MIGRATION.md) for the new repository, marketplace and plugin IDs. Version 0.2.0 is not a published release or an approved OpenAI directory listing.

The primary goal is secure key entry in a window inside Codex, with delivery to a user-confirmed destination and no plaintext in chat/model-visible output. The current local credential-entry prototype conflicts with directory rules, as confirmed by OpenAI Support. An approved in-session capability is not established yet; an external-page handoff is not treated as fulfilling this goal. See [requirements and candidate paths](docs/approval/REQUIREMENTS.md), [UAT cases](docs/approval/UAT_CASES.md) and [release management](docs/releases/MANAGEMENT.md).

## Directory eligibility and project tracking

Golden Gate has its own [GG Jira board](https://varaahgroup.atlassian.net/jira/software/projects/GG/boards/72), [public roadmap](https://github.com/Varaahgroup-llc/codex-golden-gate/issues/6) and [issue crosswalk](docs/TRACKING.md).

**Directory submission is gated.** The current encrypted local entry form still processes API keys/passwords, which the [directory restricted-data rule](https://developers.openai.com/plugins/plugin-guidelines#data-collection) prohibits. The product needs written OpenAI clarification or an approved redesign before submission. The proposed service-owned entry alternative is not implemented or approved. Repository installation is available; the packaged v0.1.0 release remains a draft.

Maintained by **Varaahgroup-llc**. [Downloads](https://github.com/Varaahgroup-llc/codex-golden-gate/releases) · [Install in Codex](INSTALL.md) · [Report a bug](https://github.com/Varaahgroup-llc/codex-golden-gate/issues) · [Maintenance](MAINTAINING.md)

**Preview release:** native Codex rendering/modal behavior and live cloud saves remain unverified. This is a standalone Codex plugin, distributed like an IDE extension. It is not affiliated with or endorsed by OpenAI.

Standalone desktop MCP Apps plugin with a bundled Codex skill. Ask your AI to save an API key, review the destination in the entry form, paste the value there, and save. The form encrypts the value before making an MCP call; the assistant receives a receipt without the value.

This project is independent of any application repository. It does not call an AI API or require an OpenAI API key. It uses the user's existing provider CLI authentication.

## What is included

- An inline MCP Apps form with password masking, optional multiline entry, explicit destination/identity review, save consent and cancellation.
- An optional host-controlled modal button when `window.openai.requestModal` is available.
- Hybrid RSA-OAEP/SHA-256 and AES-256-GCM encryption before the value enters the MCP bridge. The local server holds an ephemeral key per form. Tool arguments contain ciphertext; `_meta` carries the UI-only form capability and public key.
- Five-minute expiry, destination binding, authenticated ciphertext, single-submission enforcement and secret-free receipts.
- Local dotenv files, GitHub Actions repository/environment secrets, existing AWS Secrets Manager secrets, and Azure Key Vault.
- A self-contained Node.js server bundle: installing the release does not run npm or download dependencies.

**Compatibility:** Node.js 22+ on macOS/Linux, a locally executing chat, and an MCP Apps-compatible UI host. CI passes on both operating systems using Node.js 22 and 24. Native Codex CLI installation is verified; the chat renderer and modal still need testing in a fresh chat. The documented `requestModal` extension is for ChatGPT; its presence is checked at runtime. A host without MCP Apps rendering cannot display this form. Windows and browser-only/cloud execution are not supported in this release.

## Install the release

Ask Codex: **“Install Golden Gate from Varaahgroup-llc/codex-golden-gate.”** Review the source and installation approval before accepting. The supported CLI flow is:

```bash
codex plugin marketplace add Varaahgroup-llc/codex-golden-gate
codex plugin add golden-gate@varaahgroup-golden-gate
```

Restart Codex or start a fresh local chat after installation. If the CLI lacks these commands, use its plugin browser and the repository marketplace. Installing the plugin does not grant access to a destination provider; authorize your own service account separately.

For an offline source download:

Unzip `golden-gate-0.2.0-source.zip` into a separate folder. It includes the built bundle and this repository's marketplace catalog.

Register that folder using:

```bash
codex plugin marketplace add /absolute/path/to/codex-golden-gate
```

Restart the desktop app, open its Plugins directory, choose the **Golden Gate** marketplace, and install/enable **Golden Gate**. Start a fresh local chat. Installation and rendering must be checked in the target host; do not assume a successful SDK test means the host has enabled it.

Alternatively, `golden-gate-0.2.0-plugin.zip` contains the plugin files at the ZIP root for supported plugin import/submission workflows. It is not an npm package or a browser extension. A bundled stdio MCP server is declared in `mcp.json` with the documented `${PLUGIN_ROOT}` placeholder.

If the target host's plugin installation is unavailable, its normal MCP configuration can launch `node /absolute/path/to/plugins/golden-gate/dist/server.mjs`. This registers the tools but still requires that host to support MCP Apps UI. Never place a secret value in an MCP config file.

Try:

> Use Golden Gate to save SERVICE_API_KEY to /absolute/path/to/my-project/.env.local.

> Save a new SERVICE_API_KEY as a GitHub Actions secret for owner/repository, in staging.

> Save a value to my existing AWS Secrets Manager secret. Ask me for the full ARN and profile.

The AI supplies metadata only. The user pastes the actual value into the form.

## Provider setup

| Destination | Requirements | Scope |
| --- | --- | --- |
| Dotenv | Existing parent folder; ignored and untracked if inside Git | `.env`, `.env.*` or `.dev.vars*`; regular private files only, mode `0600`. Conservative single-line format; example files and ambiguous quoting/multiline values are refused. Use a dotenv parser without interpolation; do not source this as a shell script. |
| GitHub | Installed/authenticated `gh`; repository permissions | GitHub.com Actions secrets, repository or existing environment. No organization/Enterprise/Codespaces support. |
| AWS | Installed/authenticated AWS CLI v2; profile with STS access and `PutSecretValue` | Existing secret, full ARN required. Adds a version, no provisioning. ARN fixes region/account. |
| Azure | Installed/authenticated `az`; explicit subscription and vault permission | Creates or updates a Key Vault secret; no vault provisioning. |

The form displays the signed-in account. Cloud identity is checked again immediately before writing. Values travel to provider CLIs through stdin, never command arguments. AWS and Azure use `/dev/stdin` on supported systems. Provider write output is discarded. An unacknowledged cloud write returns `uncertain`; inspect metadata before attempting another write. The plugin does not read values back, deploy, restart, or rotate anything automatically.

## Develop and test

```bash
cd plugins/golden-gate
npm ci --ignore-scripts
npm run build
npm test
npm run test:ui
```

The UI test uses installed Google Chrome on macOS by default and Playwright Chromium on Linux. Set `GOLDEN_GATE_TEST_BROWSER` to a trusted Chromium executable to override it. It uses synthetic values and a temporary dotenv file; no provider account is used. Unit tests mock the cloud CLI boundaries. Live cloud writes have not been tested.

## Share or publish

The public repository provides versioned downloads and a Codex marketplace. See [PUBLISHING.md](PUBLISHING.md) for the distinction between repository distribution and the public OpenAI directory. GitHub availability does not mean OpenAI has approved a native directory listing or automatic recommendations.

Read [SECURITY.md](SECURITY.md) before handling real credentials. This is an initial implementation, not a claim of an independent security audit.
