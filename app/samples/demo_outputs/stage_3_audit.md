<!-- DEMO FIXTURE: precomputed sample output for Demo Mode replay. -->
| Check | PASS, WARN, or FAIL | Evidence | Required correction |
|---|---|---|---|
| Source coverage | PASS | All episodes E1-E3 represented | None |
| Classification integrity | PASS | Dark mode kept as suggestion (R7) | None |
| Conflict integrity | PASS | C1 preserved in sections 11/16 | None |
| Supersession integrity | PASS | No unapproved supersession applied | None |
| Rejection preservation | FAIL | Cloud-sync rejection (T07, R4) missing from section 10, which reads "None identified." | Restore rejection to section 10 with rationale |
| Completion accuracy | PASS | Only T11/T17 work marked completed | None |
| Current-state accuracy | PASS | Matches T17-T20 | None |
| Next-action accuracy | PASS | CSV export per T19 | None |
| Provenance honesty | PASS | Pointers use ledger-assigned turn numbers T01-T20; convention declared in SOURCE CHECK; all point to real turns | None |
| Privacy minimization | WARN | Raw email repeated verbatim in section 18 (T18) | Replace with masked reference to source pointer T18 |
| Artifact integrity | PASS | schema.sql v2 status matches T11 | None |
| Capability honesty | PASS | No storage/persistence claims | None |
| Resume usability | PASS | Section 19 is one precise instruction | None |

# REQUIRED CORRECTIONS
1. Section 10: restore "Cloud sync rejected for v1 (T07), privacy rationale,
   revisit in v2."
2. Section 18: remove verbatim email; use masked reference "test-feedback
   contact on file — see source T18."

# UNRESOLVED USER CONFIRMATIONS
1. Layout priority: does desktop-priority (T14) supersede mobile-first (T08)?

# AUDIT VERDICT
PASS WITH WARNINGS — usable with identified confirmations
