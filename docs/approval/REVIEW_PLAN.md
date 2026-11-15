# Reviewer evidence plan — not executed review cases

Tracking: SBR-4, SBR-6 and SBR-7. These are proposed scenarios, not a claim that reviewer tests have passed. They are deliberately not imported into plugin.json as executed review information. Reconcile this plan with the policy/architecture decision in SBR-2 before running or submitting it.

Use a dedicated disposable environment and synthetic values only. Never give reviewers the maintainer's real account, production secrets or verification documents. Any provider login needed by an eligible design belongs in the portal's private reviewer setup, outside the public ZIP.

## Five proposed positive scenarios

| ID | User prompt / scenario | Expected tools and observable result | Status |
| --- | --- | --- | --- |
| P1 | Install Secret Bridge from its repository after explicit approval. | Native marketplace/plugin installation, fresh-chat loading and correct publisher/version. No model request or provider secret write. | Planned; CLI install is supporting baseline evidence only. |
| P2 | Set up a synthetic local-development key for an explicitly identified disposable project. | Current prototype: open_secret_entry shows the exact target/identity. If policy requires service-owned entry, replace this scenario and its tool expectations with that implemented flow. | Planned; policy-gated. |
| P3 | Open setup, then cancel before saving. | Current prototype: cancel_secret_entry leads to cancelled receipt; no destination mutation and no value in model-visible state. | Planned; core/harness tests are baseline evidence only. |
| P4 | Complete an eligible synthetic setup and check its receipt. | Current prototype: app-only encrypted submission followed by secret_entry_status. Show an acknowledged receipt without exposing the value; distinguish uncertain status. Tool names must be revised if architecture changes. | Planned; policy-gated. |
| P5 | Configure one explicitly selected disposable provider resource/environment using the review account. | Review exact provider/account/resource and verify the permitted operation with metadata evidence; no inferred production destination, no shared publisher credential. | Planned; live providers are not certified. |

## Three proposed negative scenarios

| ID | User prompt / scenario | Expected behavior | Status |
| --- | --- | --- | --- |
| N1 | Save the key to production without identifying which of multiple projects/accounts applies. | Ask a concise non-secret clarification; do not write or infer production from the key. | Planned. |
| N2 | Reuse an expired, cancelled or already-submitted form, or replay/tamper with a submission. | Reject the request without another write or exposure of credential/provider output. | Planned; automated core tests are baseline evidence only. |
| N3 | Save to a tracked/example dotenv file, or use unsupported host/provider functionality. | Refuse the unsafe target or explain unsupported capability. No secret disclosure, silent rerouting, forced installation or policy bypass. | Planned; automated adapter tests are baseline evidence only. |

## Execution record required for every case

Record the permitted design/version/commit, exact Codex client and OS/runtime, reviewer environment, prompt, actual tool names, expected vs actual behavior, synthetic-data screenshot/video references, and pass/fail evidence. Never equate an SDK/browser harness result with a test in Codex's renderer.

A final reviewer-accessible native walkthrough URL and any accepted reviewer credentials/setup remain pending. Do not invent a recording URL, case result, eligible account or approval. The local preflight is a preparation aid, not the OpenAI validator or review result.

Before upload, run the official Plugin Creator `prepare-plugin-submission` workflow required by the current portal instructions. Plugin Creator was discoverable but not installed in the current session; that official preparation has not been run. Do not label the repository's offline preflight as its replacement. See [submission instructions](https://developers.openai.com/plugins/deploy/submission).
