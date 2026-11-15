# Migrate to Golden Gate

The maintainer renamed Secret Bridge to **Golden Gate**. The prepared rename version is **0.2.0**. This is the same standalone Varaahgroup LLC product and existing repository/project history, not a new publisher identity or OpenAI-approved listing.

| Item | Current identity |
| --- | --- |
| GitHub | https://github.com/Varaahgroup-llc/codex-golden-gate |
| Plugin | golden-gate |
| Marketplace | varaahgroup-golden-gate |
| Install selector | golden-gate@varaahgroup-golden-gate |
| Package | codex-golden-gate |
| Source folder | plugins/golden-gate |
| Local MCP server/resource | golden-gate / ui://golden-gate/entry-v1.html |
| Jira | Golden Gate, GG; existing work-item numbers are preserved |
| OpenAI publishing project | Golden Gate, in the existing Varaah group llc organization |

## Existing installations

Close or cancel old entry forms before switching. Use one version at a time. After the rename has been merged into the repository's default branch, migrate using Codex's normal plugin commands:

```bash
codex plugin remove secret-bridge@varaahgroup-secret-bridge
codex plugin marketplace remove varaahgroup-secret-bridge
codex plugin marketplace add Varaahgroup-llc/codex-golden-gate
codex plugin add golden-gate@varaahgroup-golden-gate
```

During PR review, register the reviewed local checkout's absolute path or use the Git marketplace's `--ref` option with the reviewed commit instead of the GitHub default branch, then install the new selector. Restart Codex or start a fresh local chat to load the renamed tool set. Native chat rendering still requires separate validation.

The rename does not transfer, read, rotate or delete existing destination secrets. Provider login and authorization remain per user. Receipts/forms from the old runtime are not migrated; check prior receipt status before beginning a new write.

## Developer configuration

Update custom MCP paths to plugins/golden-gate/dist/server.mjs and use the golden-gate server key. Browser-test overrides are now GOLDEN_GATE_TEST_BROWSER and GOLDEN_GATE_SCREENSHOT. Refresh bookmarks, Git remotes and integrations to the new repository and GG issue URLs. Jira retains SBR as a previous project key; check any external automation that embeds the old key.

Jira's project and visible board tab are Golden Gate / Golden Gate board. Its team-managed board directory record still exposes the original generated name SBR board; the connected API and visible board settings do not expose an edit for that backend field. This remaining platform label is recorded under GG-8 rather than presented as renamed.

The original v0.1.0 tag and its historical source remain immutable. Old names in that history, the original artwork prompt and migration examples are intentional. v0.2.0 packages must be rebuilt from the renamed source; no tag or publication is created merely by this rename.

The rename is prepared in the existing review PR. MAINTAINING.md requires passing CI and maintainer review for the dependency/release changes in that PR before merge. Public directory submission remains gated separately by verification, permitted architecture, local-MCP eligibility and review evidence.
