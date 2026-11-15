# Security preparation — November 14, 2026

Tracking: GG-6, GG-7 and GG-8. This is maintainer preparation, not an independent audit, executed native reviewer cases or OpenAI approval.

## Findings addressed in the approval-readiness branch

- The source ZIP builder previously walked the entire working directory. An unrelated untracked account note could therefore enter a source download. Both source and installable ZIPs now use the reviewed exact-file catalog in `scripts/package-files.json`. Unknown files, including unknown files beside runtime/skill files, are excluded. Missing catalog files, symlinks and unsafe paths fail packaging. Tests use synthetic private markers and verify both archives and their checksums. New public files need an explicit catalog update and review; the catalog cannot detect a secret accidentally written inside an approved public file.
- The dependency advisory scan flagged Zod below 4.6.6 under [GHSA-mrhx-c7xc-m3w5](https://github.com/advisories/GHSA-mrhx-c7xc-m3w5). The direct dependency is upgraded to the patched 4.6.7 line supported by the installed MCP SDK. Rebuild the committed server bundle and test the actual MCP schemas after updating. An advisory scan is a point-in-time dependency check, not a security certification.

## Evidence that remains required

An independent reviewer still needs to assess the permitted architecture, local host/CLI trust, temporary-file and memory limits, identity/destination binding, concurrency/replay handling and sanitized failure behavior. Live GitHub/AWS/Azure writes remain untested; use disposable resources and synthetic values when permitted. Do not reuse production accounts as reviewer fixtures.

The existing raw-credential prototype remains blocked by the directory restricted-data requirement. Packaging controls and dependency fixes do not establish an exception. Business verification is being completed by the owner in the official phone flow; it is not recorded as verified until OpenAI confirms that state. The support inquiry remains escalated pending a written specialist response. No private identity documents, inquiry links or account identifiers belong in this repository or the file catalog.
