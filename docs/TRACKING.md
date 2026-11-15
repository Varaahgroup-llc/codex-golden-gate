# Secret Bridge tracking

Owner: Varaahgroup LLC. This is a standalone project.

- Canonical source: https://github.com/Varaahgroup-llc/codex-secret-bridge
- Jira project: SBR, https://varaahgroup.atlassian.net/jira/software/projects/SBR/boards/72
- Product epic: [SBR-1](https://varaahgroup.atlassian.net/browse/SBR-1)
- Public roadmap: [GitHub #6](https://github.com/Varaahgroup-llc/codex-secret-bridge/issues/6)

## Work crosswalk

| Jira | GitHub | Work |
| --- | --- | --- |
| [SBR-2](https://varaahgroup.atlassian.net/browse/SBR-2) | [#7](https://github.com/Varaahgroup-llc/codex-secret-bridge/issues/7) | Resolve OpenAI restricted-data eligibility and approve the entry architecture |
| [SBR-3](https://varaahgroup.atlassian.net/browse/SBR-3) | [#8](https://github.com/Varaahgroup-llc/codex-secret-bridge/issues/8) | Complete Varaahgroup publisher verification and local MCP submission eligibility |
| [SBR-4](https://varaahgroup.atlassian.net/browse/SBR-4) | [#9](https://github.com/Varaahgroup-llc/codex-secret-bridge/issues/9) | Validate the native Codex install, chat UI and extension lifecycle |
| [SBR-5](https://varaahgroup.atlassian.net/browse/SBR-5) | [#10](https://github.com/Varaahgroup-llc/codex-secret-bridge/issues/10) | Implement and verify credential-safe contextual destination setup |
| [SBR-6](https://varaahgroup.atlassian.net/browse/SBR-6) | [#11](https://github.com/Varaahgroup-llc/codex-secret-bridge/issues/11) | Complete independent security review and disposable provider validation |
| [SBR-7](https://varaahgroup.atlassian.net/browse/SBR-7) | [#12](https://github.com/Varaahgroup-llc/codex-secret-bridge/issues/12) | Prepare reviewer evidence and submit the native directory listing |
| [SBR-8](https://varaahgroup.atlassian.net/browse/SBR-8) | [#13](https://github.com/Varaahgroup-llc/codex-secret-bridge/issues/13) | Maintain standalone release, issue and dependency governance |

## Authority and maintenance

Jira records delivery status, dependencies and approval evidence. GitHub contains source, implementation PRs and public issue counterparts. Keep both sides linked during authorized work; this is not an unattended synchronization service. Open GitHub issues may correspond to To Do or In Progress in Jira. Do not mark a planned feature as completed because the tracking issue exists.

Reference SBR issue keys in related branches, commits and PRs. Keep releases, changelogs, publisher records and review evidence scoped to Secret Bridge. Do not place this product's work in another product's repository, Jira project or release ledger.

## Release gates

The initial v0.1.0 prerelease remains a draft. The raw-credential-entry prototype is not a directory-ready submission under the current restricted-data rule. SBR-2 must resolve the policy/architecture decision; SBR-3 must establish verified publisher/local-MCP eligibility; native Codex rendering and security/provider evidence must be completed before SBR-7 can claim submission/readiness. No directory approval or listing currently exists.

Keep passwords, keys, tokens, private organization IDs, reviewer credentials and verification documents out of public source and GitHub issues. Use the private reporting/verification channels where appropriate.

