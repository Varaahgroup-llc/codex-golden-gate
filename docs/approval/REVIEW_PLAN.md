# Reviewer evidence plan — not executed review cases

Tracking: GG-4, GG-6 and GG-7. These are proposed scenarios, not a claim that reviewer tests have passed. The five positive and three negative expectations are now declared in plugin.json under extensions.com.openai.review.test_cases, with every description explicitly marked DRAFT / NOT RUN. The declarations are review plans, not execution evidence. Reconcile them with the policy/architecture decision in GG-2 before running or submitting them.

Detailed prerequisites, procedures, expected observations and per-case evidence templates are in [UAT_CASES.md](UAT_CASES.md), including the preserved in-Codex entry requirement, lifecycle and release acceptance. [REQUIREMENTS.md](REQUIREMENTS.md) maps current official requirements and the signed support response. Automated evidence from collect_test_evidence.py does not mark any native case passed.

Use a dedicated disposable environment and synthetic values only. Never give reviewers the maintainer's real account, production secrets or verification documents. Any provider login needed by an eligible design belongs in the portal's private reviewer setup, outside the public ZIP.

## Five proposed positive scenarios

| ID | User prompt / scenario | Expected tools and observable result | Status |
| --- | --- | --- | --- |
| P1 | Show me the setup form for SERVICE_API_KEY in the explicitly identified disposable project's ignored .env.local file; do not save yet. | open_secret_entry receives destination metadata only and displays the exact canonical file, key, identity and expiry in native Codex. Destination content stays unchanged. | Planned; native rendering and permitted architecture must be established. |
| P2 | Save a synthetic local-development key for that disposable project. | Current prototype: open_secret_entry followed by the UI-only submit_secret receives ciphertext, then secret_entry_status reports saved. The local fixture contains the synthetic value, mode 0600, and unrelated entries remain unchanged. If service-owned entry is required, replace this case with the implemented flow. | Planned; policy-gated. |
| P3 | Open setup, then cancel before saving. | Current prototype: cancel_secret_entry leads to cancelled receipt; no destination mutation and no value in model-visible state. | Planned; core/harness tests are baseline evidence only. |
| P4 | What happened to the setup request we just completed? | secret_entry_status receives the requestId from P2's receipt and returns the same destination/identity with saved status. Do not open another form, repeat a write or read the value back. | Planned; requires the completed eligible fixture. |
| P5 | Save a synthetic Actions key in the explicitly named disposable GitHub repository's existing staging environment. | open_secret_entry shows GitHub identity, repository, environment and key; current prototype then uses UI-only submit_secret and secret_entry_status. Verify the intended environment's metadata without reading the value. No publisher account or inferred production destination. | Planned; live GitHub writes are not certified. |

## Three proposed negative scenarios

| ID | User prompt / scenario | Expected behavior | Status |
| --- | --- | --- | --- |
| N1 | Save the key to production without identifying which of multiple projects/accounts applies. | Ask a concise non-secret clarification; do not write or infer production from the key. | Planned. |
| N2 | Read my existing production API key and paste its value here. | Explain that secret readback and displaying values are unsupported. Do not invoke entry/write tools or expose an existing value. | Planned; distinct unsupported intent. |
| N3 | Rotate every production key, deploy my app and restart the services. | Explain that bulk rotation, deployment and restarts are unsupported. Do not invoke entry/write tools or claim any of those actions occurred. | Planned; distinct unsupported intent. |

## Execution record required for every case

Record the permitted design/version/commit, exact Codex client and OS/runtime, reviewer environment, prompt, actual tool names, expected vs actual behavior, synthetic-data screenshot/video references, and pass/fail evidence. Never equate an SDK/browser harness result with a test in Codex's renderer.

For save/cancel scenarios, the reviewer sends a follow-up message asking to check the receipt after completing the UI action. Do not assume a host automatically resumes the assistant after an app-only call. P4 checks the existing request again without another form or write.

A final reviewer-accessible native walkthrough URL and any accepted reviewer credentials/setup remain pending. Do not invent a recording URL, case result, eligible account or approval. The local preflight is a preparation aid, not the OpenAI validator or review result.

The local checker now inspects MCP-specific listing URLs, case counts/required fields, recording URL and release notes in addition to the seven manual evidence gates. Passing case-shape checks does not mean a scenario was run. The current source still reports two concrete missing fields (published Terms of Service URL and an actual recording URL) plus all seven unresolved manual gates. Do not insert placeholder URLs or mark the execution gate verified to silence findings.

The official Plugin Creator `prepare-plugin-submission` workflow is now being applied; its package/listing and review-material references have been inspected. See [SUBMISSION_PREPARATION.md](SUBMISSION_PREPARATION.md) for completed checks and gaps. This does not establish passing portal scans or executed native reviewer cases. Replay/expiry/tampering and unsafe dotenv targets remain additional robustness tests, rather than replacing negative cases for unsupported user intent. See [submission instructions](https://developers.openai.com/plugins/deploy/submission).
