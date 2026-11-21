# Release baseline · 21 November 2026

GG-9 audit before changing release infrastructure. The GitHub API returned the canonical repository, admin access, default branch main at `7cc8c1dff3b1959037d73586f8a138bd749d75eb`, twelve branches (main, five project branches and six dependency branches), no rulesets and no classic protection for main. All four macOS/Linux × Node 22/24 jobs passed on this main SHA. The previous local tracking ref was behind the merged PR #20. [Exact CI run](https://github.com/Varaahgroup-llc/codex-golden-gate/actions/runs/43762850051)

## Product and distribution

One version covers the local stdio MCP server, inline MCP Apps UI, bundled skill, four destination adapters, plugin ZIP and local marketplace source ZIP. Users install the repository marketplace or a reviewed source archive in a compatible local client. There is no separately deployed credential broker, hosted staging or production service. The GitHub release-draft approval environment has required reviewers and admin bypass disabled. The tag workflow can prepare a draft. Publication and directory submission require separate decisions.

| Evidence | Interpretation |
| --- | --- |
| v0.1.0 at `79e902d630fb96e90179303ac4c242eca15b44d8` | Original Secret Bridge tag, one draft prerelease, no publication date. Preserve this identity. |
| PR #14, prepared 0.2.0 | Rename, marketplace migration, review materials. No corresponding tag or release. |
| PR #17, #18, #19 | Guarded draft staging and test evidence, contextual setup requirements, browser isolation tests. GG-5 implementation and GG-6 independent review are outstanding. |
| PR #20, main package/plugin/lock at 0.3.0 | Inline slot, resource and protocol/browser regression coverage. Merged and tested in CI. Native host acceptance outstanding. |
| Open PRs #1–5, #15 | Unmerged dependency proposals. Excluded. |

## Tracker and acceptance

The GG software project exposes To Do, In Progress and Done for Tasks. Live JQL returned nine issues, eight In Progress and GG-5 To Do. Zero resolved/closed issues, zero Fix Versions assigned and zero project versions at discovery. GG-8 owns standing governance and GG-9 owns this implementation. Use the existing crosswalk for individual issues. [GG crosswalk](../TRACKING.md)

Native CLI installation and synthetic MCP/browser/provider-boundary tests have evidence. GG-2 architecture eligibility is blocked. GG-3 publisher verification and allowlisting, GG-4 native UI and lifecycle, GG-5 contextual setup, GG-6 independent review and disposable provider execution, and GG-7 reviewer/legal evidence remain open. There is no certified multi-tenant broker, hosted access-token revocation service or production distribution. [Acceptance record](../approval/readiness.json)

## Implementation order

1. Preserve the existing v0.1.0 history. Use the inline feature and rename migrations to propose 0.3.0, with 0.3.0-rc.1 for internal validation.
2. Extend existing CI, packaging and protected draft flow with change records, security scanning, reproducible ZIPs and exact-source candidate evidence. Require reviewed PRs and matrix checks on main.
3. Associate the planning version with GG-9. Track implemented slices of broader issues in the bundle while their acceptance work stays open.
4. Exercise isolated packaging, synthetic tests and recovery. Record gates and hashes. Obtain independent review, native/provider evidence and explicit owner decisions before any distribution.

The previous ZIP writer incorporated local timestamps and permissions. The baseline lacked a release manifest, enforced PR traceability, dependency audit and secret scan. The existing preflight distinguishes technical test execution from outstanding directory gates. [Baseline workflows and source](https://github.com/Varaahgroup-llc/codex-golden-gate/tree/7cc8c1dff3b1959037d73586f8a138bd749d75eb)
