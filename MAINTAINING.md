# Maintenance and releases

Owner: Varaahgroup-llc. Source, issues and downloads live at https://github.com/Varaahgroup-llc/codex-golden-gate.

## Ongoing maintenance

Review incoming issues and dependency update PRs. Validate bug fixes with a regression test when the behavior warrants it. Keep the minimum runtime, supported providers and client compatibility table honest. Review GitHub advisories and dependency updates; never merge an update solely because a bot opened it.

Use protected main-branch pull requests when organization settings permit. Require the CI jobs to pass and maintainer review for changes affecting secret handling, destination routing, dependencies or release scripts. GitHub repository administrators control those settings; this document does not assert protection is enabled.

Only synthetic credentials belong in tests, screenshots, issues and examples. Security reports go through GitHub private vulnerability reporting. Patch an affected maintained version, record the fix and coordinate disclosure with the reporter. Do not promise response times the maintainers have not adopted.

## Release a version

1. Complete review and CI. Verify a clean installation in the target Codex client before claiming that host/version is supported. Validate providers using disposable resources before claiming live compatibility.
2. Run `python3 scripts/version.py X.Y.Z`, update CHANGELOG.md and any compatibility evidence, then build and test. The script updates plugin.json, package.json and the lockfile; the server and form get their version from package.json at build time.
3. Commit the source and regenerated bundle, merge the reviewed change to main and wait for green CI.
4. Create an immutable annotated tag `vX.Y.Z` at that exact commit and push it. Never move or reuse a published tag.
5. The release workflow rebuilds, checks the committed bundle, runs the core/browser tests, validates tag/version consistency and packages the assets. It creates a **draft prerelease** for 0.x versions, or a draft release for 1.x+. If a command fails it stops before creating a new release.
6. Review the draft's assets, SHA-256 checksums, changelog and compatibility notes. Publish it from GitHub when ready. Initial v0.1.0 is an explicitly labeled preview.

Users install the repository's Codex marketplace and refresh it with `codex plugin marketplace upgrade varaahgroup-golden-gate`. They may need to update/re-enable the installed plugin and restart the client. A marketplace refresh is not a forced update or a remote change to anyone's credentials.

For universal-directory distribution, follow PUBLISHING.md. A public GitHub release does not confer OpenAI directory approval.
