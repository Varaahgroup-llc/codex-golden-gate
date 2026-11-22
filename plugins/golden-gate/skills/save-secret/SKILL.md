---
name: save-secret
description: Open Golden Gate's encrypted inline MCP Apps paste slot to save API keys, tokens, or passwords to a selected dotenv file, GitHub Actions, AWS Secrets Manager, or Azure Key Vault without pasting values in chat.
---

# Save a secret

Use the connected Golden Gate MCP tools. A skill alone cannot render this UI; if its MCP tools are unavailable, explain that the companion plugin must be installed and enabled.

Select the destination automatically from the user's instruction and unambiguous project metadata. The user's explicit service/project/environment wins. For a CI secret use the requested repository and existing Actions environment; for local app setup use the active project's private dotenv location; for a named vault or secret manager use its exact resource identity. Read only the non-secret project/configuration metadata needed to distinguish these options. Do not read existing secret values to infer routing.

Show the selected destination and identity in the inline paste slot. Ask a short non-secret clarification only if multiple destinations or environments are plausible or an identifier is missing. Never infer production from a key's format or silently switch services when an adapter is unavailable. Never request a secret in chat or a model-visible tool argument.

Once installed and enabled, this skill can be selected automatically for relevant tasks. Before installation, an uninstalled plugin cannot inject instructions into unrelated chats. Use the public install instructions or native directory recommendation flow with the user's approval; never silently install or weaken permissions.

Call `open_secret_entry` with one destination object:

- `env`: `provider`, absolute `file`, `name`. Parent must exist; inside Git the file must be ignored and untracked. Add a narrow ignore rule only when authorized. The adapter rejects symlinks and unsupported existing dotenv syntax.
- `cloudflare-local`: for an explicitly local Wrangler Worker, pass its absolute `configFile`, binding `name`, and the requested local `environment` if named. Use the config file selected by the user's dev command. The slot displays the exact .dev.vars file. If the project uses custom env files, use the explicitly identified private file through `env`. If a named environment inherits shared settings, clarify before selecting a shared file. A request for a deployed Worker binding or account Secrets Store has no remote adapter here. Do not substitute a local file or run a deployment.
- `github`: `provider`, `repo` as `owner/repository`, `name`, optional existing `environment`. Requires authenticated `gh` for GitHub.com. Saves Actions secrets only.
- `aws`: `provider`, full existing `secretArn`, explicit `profile`. Requires AWS CLI v2. The ARN determines region/account; no secret is created.
- `azure`: `provider`, `vault`, explicit `subscription`, `name`. Requires authenticated Azure CLI.

The slot shows the immutable destination, signed-in provider identity and replacement notice. Selecting Save explicitly confirms delivery and replacement at that displayed target. Let the user paste and select Save or Cancel; pasting alone never submits. No additional open-form step or modal is part of this component. Do not inspect, screenshot, automate, or extract values from the slot. Do not call app-only `submit_secret` yourself. Never put secrets in widget state, chat, logs, CLI flags, environment variables, or source control.

Use `secret_entry_status` with the returned request ID when the user asks about completion. Report saved only for a `saved` receipt. A cloud `uncertain` result means the remote write might have succeeded; check metadata only and ask before another write. Do not automatically retry, read values back, or deploy/restart services.

Forms expire in five minutes and accept one submission. Cancelled or expired forms require a new request. Normal runtime permissions apply; never bypass a denied operation.

Embedded UI requires an MCP Apps-compatible inline host. The 0.3.0 candidate declares inline-only support; the host controls actual rendering and tool-row expansion. This is a plugin component, not Codex's built-in approval prompt. Do not claim an unsupported host has rendered a slot or that a test harness certifies native behavior.
