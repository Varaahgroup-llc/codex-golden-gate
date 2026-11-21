# Change control and Jira

Use one reviewed JSON record in docs/changes per independently describable change. Follow the GG-9 example. The filename starts with the canonical issue key. Record owner, priority, description, acceptance, validation, security impact, target version (or unassigned) and class. Supported classes are FEATURE, ENHANCEMENT, BUGFIX, SECURITY, PERFORMANCE, REFACTOR, INFRASTRUCTURE, DEPENDENCY, DOCUMENTATION and BREAKING_CHANGE. Add a user-readable Unreleased entry under Added, Changed, Deprecated, Removed, Fixed or Security. Public descriptions contain only safe summaries. Store sensitive details privately.

PR validation checks the change record and changelog against the base revision. Reviewers verify accuracy, actual Jira identity, dependencies, compatibility and security impact. For recurring work on a broad GG issue, record the implemented slice explicitly. Keep unfinished slices outside the acceptance claim.

GG uses To Do, In Progress and Done. Use Fix Version for a planned target, the PR and CI links for review/testing, and the release register for candidate, staging and distribution evidence. Verify project and permission, search before creating records, and read back changes. Record approval references, deployment/download proof and post-release verification before labeling work released. A shared workflow change requires its own impact review.
