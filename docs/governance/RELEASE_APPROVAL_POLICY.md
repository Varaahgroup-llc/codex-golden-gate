# Approval and security acceptance

The maintainer records PASS, FAIL, BLOCKED, NOT_APPLICABLE or NOT_VERIFIED for each gate in the release record. Each PASS has scoped evidence. NOT_APPLICABLE requires a reason. An applicable FAIL, BLOCKED or NOT_VERIFIED prevents production distribution. Only the owner can authorize the exact channel, version, SHA and checksums after reviewing the record. Record approver, date, scope and durable evidence reference. Distinguish candidate tag authorization, GitHub draft environment approval, public distribution and directory submission.

| Gate | Acceptance evidence |
| --- | --- |
| Functional, regression and compatibility | Core, adapter, stdio and UI CI, plus native install, restart, update, disable/uninstall and target-client UAT. |
| Security | Synthetic secret isolation across UI/tool/log/receipt channels, authenticated ciphertext, expiry, cancellation, one use, destination binding, identity recheck, permission limits and private dotenv handling. Dependency and source secret scans. Independent review and disposable provider tests under GG-6. |
| Architecture and publisher | Written GG-2 disposition and GG-3 eligibility before directory progression. Retain restricted decisions privately. GG-7 supplies executed reviewer, legal and listing evidence. |
| Build, version and documentation | Clean exact SHA, green main CI, version agreement, immutable tag, reproducible allowlisted ZIPs, checksum readback, accurate notes and reviewed limitations. |
| Distribution and recovery | Authorized channel, disposable-profile smoke and rollback results, matching archived artifacts, owner decision. |

Cancellation and expiry concern one-use form capabilities. Upstream provider revocation, tenant isolation in a hosted broker and centralized audit logging have no implemented service here. Evaluate user-scoped CLI authorization and metadata receipts within the actual local boundary. Never claim those hosted controls passed. Use only synthetic fixtures in CI. Keep private evidence out of candidate artifacts.

Record an exceptional process decision with owner, rationale, affected gate, mitigating control, approval reference and expiry. Escalate eligibility, independent security and production authorization to their actual decision makers. Tests cannot grant those decisions. Production publication is a manual owner action. Repository owners must also control write/admin access and review GitHub audit events.
