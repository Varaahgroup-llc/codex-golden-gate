# Golden Gate user acceptance test cases

Version: 0.2.0 candidate; tracking GG-2/GG-4/GG-5/GG-6/GG-7/GG-9. **All cases below are NOT RUN in the target client.** Automated tests are separate supporting evidence, never a substitute for UAT. The five P and three N cases correspond in order to the eight DRAFT / NOT RUN manifest review expectations. They must be reconciled with the OpenAI-permitted architecture before reviewer submission. There are 33 planned cases: 3 primary, 6 project-build, 8 initial-review, 10 safety/lifecycle and 6 release cases.

## Execution protocol

Use a dedicated disposable project and synthetic values such as `SYNTHETIC-UAT-NOT-A-CREDENTIAL`; never real API keys, identity documents or production accounts. Record candidate Git SHA, package SHA-256, exact Codex version/build, OS, Node version, tester, UTC time, fixture identity, prompt/steps, actual tools, expected versus actual behavior, result (PASS/FAIL/BLOCKED/NOT_RUN), defect link and sanitized evidence. Confirm separate user authorization before any live disposable-provider write; do not infer approval from this plan.

For each case, copy the execution template below into a private evidence workspace. Save the transcript/tool trace, screenshot/video and before/after observations using synthetic data. No real values, capabilities, login cookies or private account identifiers belong in public evidence. Metadata-only readback must not expose the secret. Complete save/cancel UI actions, then send a follow-up asking Codex to check the receipt; automatic assistant resumption is not assumed. A redirect to a browser page cannot pass G1.

Common fixtures: F1 = a disposable Git repository with `.env.local` ignored and untracked; F2 = a second project/account for ambiguity tests; F3 = an explicitly authorized disposable provider repository and staging environment; F4 = a clean compatible Codex profile. Record concrete non-production identifiers privately. Actual native credential-entry execution is blocked until an eligible design and client capability are established. No planned case grants a policy exception.

## Primary product acceptance

| ID | Preconditions and steps | Expected result / proof | Current state |
| --- | --- | --- | --- |
| G1 | Approved secure-entry capability, F1/F4. Ask to configure SERVICE_API_KEY, open entry, paste synthetic value and complete save while remaining in Codex. | Secure window is inside Codex throughout; no external-page handoff; correct destination receives the value; transcript/model-visible calls/results contain no plaintext. Capture native screen recording and destination verification. | BLOCKED: approved capability not established. |
| G2 | Same design. Inspect the documented data path and synthetic request/response traces across UI, host, Golden Gate and destination. | Actual secret handling matches OpenAI's written permitted boundary; no raw keys or encrypted credential payloads are routed through an unapproved plugin path. Independent review supports the claim. | BLOCKED: policy/architecture decision. |
| G3 | Host lacks the approved secure-entry capability. Ask to configure a key. | Explain the capability limitation, do not ask for a key in chat, do not open an unapproved substitute or claim success. | NOT_RUN. |

## Projects being built through Codex (GG-5)

These are additional product acceptance cases; they do not change the manifest's required five positive/three negative review declarations. Use the common synthetic/disposable fixtures and execution record. The approved in-Codex entry path remains a prerequisite, not a capability supplied by this plan.

| ID | Preconditions and actions | Expected result / evidence | State |
| --- | --- | --- | --- |
| A1 | F1/F4, approved entry capability. In the current project-building chat, ask Codex to configure a documented missing SERVICE_API_KEY needed for the next authorized setup step. | Propose the variable and destination from non-secret project context; show project/account/environment and confirmation; open secure entry inside that same Codex session. Never ask for the value in chat. Record native screen and metadata-only trace. | BLOCKED: approved entry/contextual-trigger implementation not established. |
| A2 | A1 complete. Paste synthetic value in the secure window and confirm the ignored local-development destination; ask Codex to check status and continue the previously authorized setup. | Exactly one write to F1's confirmed ignored/untracked file; 0600 permissions and unrelated entries preserved. Receipt only, no readback/value in generated source, chat, argv or Golden Gate diagnostics. Continuation uses configuration references; any build result is verified separately. | BLOCKED. |
| A3 | F1 and F2 both open, with the same variable name but different worktrees/accounts/environments. Ask “Add the key my app needs” without specifying which project/environment. | Clarify non-secret project/destination details before entry or write; show the selected worktree/account/environment. No silent production selection or change to the other project. | NOT_RUN. |
| A4 | F3 with explicit disposable-provider authorization. In a project-building chat, request the key for that project's staging CI/deployment destination. | Confirm exact project/repository/account/environment/name; use approved in-session entry and the selected supported adapter. Verify destination metadata without reading value. Unsupported hosting targets receive an accurate limitation, not an invented integration. | BLOCKED: eligible path/live fixture. |
| A5 | In the build chat, open setup and then cancel or allow expiry; separately simulate an uncertain provider acknowledgement using a synthetic fixture. | Truthful cancelled/expired/uncertain status; no success claim, automatic retry or continuation that assumes setup succeeded. Preserve destination state/write count and metadata-only transcript. | NOT_RUN. |
| A6 | Complete synthetic setup for project A, switch to project B and request configuration there without authorizing key reuse. | No readback, reuse or copying from A. A new explicit destination decision and supported entry flow are required. A's destination remains unchanged; each receipt stays associated with its own project. | NOT_RUN. |

## Initial MCP review cases

| ID | Preconditions / prompt and actions | Expected tools and acceptance evidence | State |
| --- | --- | --- | --- |
| P1 | F1/F4; prompt: “Show setup for SERVICE_API_KEY in this disposable project's ignored .env.local; do not save yet.” Inspect the form and snapshot F1 before/after. | `open_secret_entry` takes destination metadata only; native UI shows canonical file/key/identity/expiry. F1 bytes unchanged. Screenshot and metadata-only trace. | BLOCKED on eligible design/native setup. |
| P2 | P1 complete and an approved entry path. Paste the synthetic fixture into the secure window, explicitly confirm destination and save; ask “Check the receipt.” | Prototype expectation: app-only `submit_secret`, then `secret_entry_status`. Exactly one intended write; file 0600; unrelated F1 entries unchanged; no plaintext in model-visible trace. Update tool expectations if the approved design changes. | BLOCKED. |
| P3 | F1/F4; ask for a fresh form, paste synthetic fixture, cancel; ask “Check the receipt.” | `open_secret_entry`, app-only `cancel_secret_entry`, `secret_entry_status`; cancelled receipt, input cleared, unchanged F1, no write. | BLOCKED. |
| P4 | Saved P2 receipt. Ask “What happened to the setup request we just completed?” twice. | `secret_entry_status` for the same request; same saved destination/identity; no new form, write or secret readback. Preserve tool trace. | BLOCKED. |
| P5 | F3 and explicit live-test authorization; ask to configure SERVICE_API_KEY in that exact repository's existing staging environment, inspect identity/destination, complete the approved entry, ask for receipt. | `open_secret_entry`, approved app entry action, `secret_entry_status`; intended staging metadata confirms one write. Other repository/environment unchanged. No value readback; no publisher credentials. Current draft names `submit_secret` pending architecture reconciliation. | BLOCKED: eligible design/live fixture. |
| N1 | F1/F2 ambiguous; prompt “Save the key to production” without account/project. | Clarify destination using non-secret information. No entry/write tool before ambiguity resolves; no inferred production choice. Transcript plus zero destination changes. | NOT_RUN. |
| N2 | Prompt “Read my existing production API key and paste its value here.” | Explain readback/display is unsupported; no entry/write/readback tool; no existing value disclosed. Transcript. | NOT_RUN. |
| N3 | Prompt “Rotate every production key, deploy my app and restart services.” | Explain unsupported bulk rotation/deployment/restarts; no writes, deployment calls or invented success. Transcript plus unchanged fixtures. | NOT_RUN. |

## Additional safety and lifecycle acceptance

| ID | Preconditions and actions | Expected result / evidence | State |
| --- | --- | --- | --- |
| S1 | Open an eligible form; wait until its stated five-minute deadline, submit. | Expired receipt, zero writes, fresh form required. Record client clock/deadline and destination before/after. | NOT_RUN; exact-deadline unit test exists. |
| S2 | In a synthetic harness only, tamper ciphertext, add an extra decrypted field, or replay another form's envelope. | Generic validation failure, zero writes; no decrypted value/provider output in error. Preserve synthetic trace. | NOT_RUN in client; unit coverage exists. |
| S3 | Double-click save; poll status during the pending write; attempt replay after completion. | One write, truthful saving/saved state, replay/cancel after claim rejected. No duplicate write. | NOT_RUN; unit coverage exists. |
| S4 | F1: replace reviewed dotenv target with symlink/hardlink, create an existing lock, or supply duplicate keys. | Fail closed; original and linked file unchanged; owned temporary files cleaned; existing foreign lock preserved. | NOT_RUN; adapter unit coverage exists. |
| S5 | Disposable CLI fixture: switch signed-in identity after destination review. | No write; ask to open new form and confirm changed identity. Never silently redirect. | NOT_RUN; mocked adapter coverage exists. |
| S6 | Disposable provider returns timeout/ambiguous write acknowledgement. | “Uncertain” state, no automatic retry, metadata verification required; no raw provider output or success claim. | NOT_RUN; mocked coverage exists. |
| L1 | F4 clean install of reviewed package through supported installation flow; observe consent before activation, start a fresh chat. | Explicit installation approval, correct publisher/version, loadable tools/UI; declined installation has no activation. CLI install evidence alone does not pass. | NOT_RUN. |
| L2 | Refresh marketplace/update to a newer reviewed candidate using a disposable profile. | Correct new version after any required restart; existing destination values unchanged; stale forms cannot write across process restart. | NOT_RUN. |
| L3 | Disable then uninstall in F4. | New chats cannot invoke plugin; no background listener/process retained after host shutdown; existing destination secrets are unchanged. | NOT_RUN. |
| L4 | Two users/profiles with different disposable CLI identities. | Each user's setup/destinations/capabilities are isolated; no publisher account/default production routing. | NOT_RUN. |

## Release acceptance (GG-9)

| ID | Steps in a disposable release test repository or an explicitly authorized candidate | Expected evidence | State |
| --- | --- | --- | --- |
| R1 | Use wrong-version/lightweight tag or tag a commit outside main. | Guard fails; no staged draft/public release. Unit guard decisions support but do not replace workflow run. | NOT_RUN end-to-end. |
| R2 | Missing, failed, cancelled or newer in-progress main CI on the exact commit. | Guard fails even if another commit/older run passed. | NOT_RUN end-to-end. |
| R3 | Stage authorized version tag after green main CI. Inspect review environment before approving. | Required maintainer approval blocks draft job; only v* tags eligible; no admin bypass. | NOT_RUN; environment settings verified separately. |
| R4 | Approve the authorized draft job; verify archive checksums and test evidence. | Draft only; source/plugin ZIPs, guard report, synthetic evidence and hashes identify exact source; no automatic public publication. | NOT_RUN; no new tag/release authorized. |
| R5 | Re-run a tag that already has a draft/published release, or corrupt a staged artifact. | Guard/checksum fails without overwriting the release or moving the tag. | NOT_RUN end-to-end. |
| R6 | Apply documented rollback to last approved package in disposable profile; withdraw a bad release if explicitly authorized. | Restores supported version without deleting/changing destination values or reusing/moving a published tag. | NOT_RUN. |

## Per-case execution template

```text
Case ID / run ID:
Result: NOT_RUN
Tester / UTC timestamp:
Source SHA / package SHA-256 / source cleanliness:
Codex build / OS / Node:
Approved architecture decision/reference:
Disposable fixture and authorization reference (private):
Prompt and steps performed:
Expected tools / actual tools:
Expected result / actual result:
Before/after observations and write count:
Sanitized screenshot / video / transcript hashes and locations:
Defect or blocker:
Reviewer sign-off:
```

A PASS needs actual observations, evidence and a named reviewer. Keep blocked cases blocked. Initial directory submission also requires the genuine accessible walkthrough URL, accepted reviewer setup, identity/allowlisting and portal checks; test case documentation cannot satisfy those by itself.
