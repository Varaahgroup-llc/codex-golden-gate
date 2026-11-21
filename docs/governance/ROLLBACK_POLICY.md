# Recovery and corrective releases

Record previous known-good commit, artifact, checksum, compatibility and migration constraints before approval. The original v0.1.0 archive uses the old marketplace identity. Review MIGRATION.md before selecting a fallback. A draft or untested predecessor needs validation before use as a fallback.

1. Stop promotion, preserve evidence, scope affected hosts and request approval for consequential containment or recovery.
2. In a disposable profile verify the archived ZIP checksum, extract into a clean directory, verify manifest and bundle, install using the supported marketplace route, restart and test a fresh synthetic form. Record exact host and results. Packaging CI rehearses source restoration and byte-identical repackaging. Native R6 requires separate execution.
3. After authorization disable the affected installation, select the verified fallback and repeat the smoke test. Fresh process-bound forms are required. Preserve destination secret state and provider revocation. No secret restoration, destructive configuration or schema downgrade is implicit in rollback.
4. If migration is irreversible or no safe fallback exists, block distribution until a tested forward recovery exists. Repair through a newly approved version. Archive the incident, hashes, owner decision and verification. Never move the original tag.
