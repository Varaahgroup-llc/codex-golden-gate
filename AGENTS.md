# Golden Gate project scope

This repository is the standalone Golden Gate product maintained by Varaahgroup LLC.
Canonical repository: Varaahgroup-llc/codex-golden-gate. Canonical Jira project: GG. See docs/TRACKING.md for the issue crosswalk and release gates.

Future work belongs to this repository and GG, with separate requirements, releases, review evidence and approvals. Do not mix product work with another application's repository or Jira project. Reference the relevant GG issue in implementation branches, commits and PRs.

Use Cloudflare services and tooling wherever they fit Golden Gate’s project requirements.

The desired product is a native Codex plugin with directory discovery, user-approved installation, updates, disable/uninstall and per-user destination setup comparable to an IDE extension. Distinguish this target from verified behavior. Native CLI installation and the MCP/browser test harness are verified; actual Codex chat rendering/modal behavior and live provider flows are not yet certified.

The existing raw-credential-entry prototype conflicts with the directory restricted-data rule as currently documented. Do not submit false attestations, claim an exception, publish an approved listing, or represent the prototype as directory-ready. Resolve GG-2 with written clarification or an authorized architecture decision. Service-owned credential entry is a candidate design, not a shipped feature or guaranteed approval.

Preserve normal user/organization authorization and runtime permissions. Keep actual credentials and private verification/account information out of code, tools, logs, test data, public issues and reviewer ZIPs. Do not start external communications or assume release approval from a tracking update.

For source changes, build and run the relevant checks documented in README.md; commit generated server/third-party notices with runtime changes. Documentation-only changes need link/format consistency checks rather than repeated runtime tests. Follow MAINTAINING.md for versioned releases and retain immutable published tags.


## Permanent release instructions (GG-9)

Before implementing, merging, tagging or preparing distribution, read [software release management](docs/governance/SOFTWARE_RELEASE_MANAGEMENT.md) and its linked policies. Identify the GG work item, classify the change, use a short-lived GG branch and maintain the change record and Unreleased changelog. Record acceptance criteria, security impact, test results, compatibility and target. Run the applicable checks before requesting review.

Report the highest evidenced state separately for each deliverable: PLANNED, IMPLEMENTED, TESTED, MERGED, RELEASE_CANDIDATE, STAGED, RELEASED or VERIFIED. Link the commit, PR, checks and distribution evidence as they become available. Keep Jira open until its actual acceptance criteria are met. Disclose breaking changes and approved, time-limited exceptions. Preserve immutable tags and artifacts. Candidate preparation is authorized by the engineering task. Tagging, production distribution, consequential rollback and directory submission each require explicit authorization for that action.
