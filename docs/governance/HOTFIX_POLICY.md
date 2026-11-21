# Emergency changes

For an outage, suspected exposure, critical authorization flaw or severe regression, open a restricted incident and link a safe GG summary. Identify affected immutable releases, permissions and exposure window. The owner authorizes containment, including disabling a destination if required. Coordinate credential response privately with the credential owner.

Branch from the affected reviewed version, implement the smallest fix, classify compatibility and run focused security/regression tests plus the normal candidate pipeline. Record any expedited review, responsible owner and expiration. Obtain emergency owner authorization tied to checksums, issue a new version, verify it in the target channel, archive evidence and reconcile the fix into main. [Recovery procedure](ROLLBACK_POLICY.md)
