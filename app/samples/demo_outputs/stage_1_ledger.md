<!-- DEMO FIXTURE: precomputed sample output for Demo Mode replay. -->
# SOURCE CHECK
Usable source found: pasted conversation transcript (unnumbered chat log),
20 turns, plus a current objective. The transcript carries no message IDs,
so this ledger assigns sequential turn numbers T01-T20 in reading order and
uses them as source pointers throughout. Project name supplied: Trailhead
Tracker. Bridge mode: Standard.

# EPISODE MAP
- E1 Scoping (T01-T08): features, storage decision, cloud-sync rejection.
- E2 Build (T09-T17): schema v1→v2, layout conflict emerges, log form done.
- E3 Handoff point (T18-T20): contact info shared, CSV export queued.

# ATOMIC MEMORY LEDGER
| ID | Class | Statement | Status | Confidence | Source | Notes |
|---|---|---|---|---|---|---|
| R1 | requirement | Log hikes: date, trail, distance, elevation gain, notes | active | confirmed | T03 | Core feature set |
| R2 | requirement | Offline support "eventually" | active | confirmed | T03 | Timing unspecified |
| R3 | decision | SQLite for storage | active | confirmed | T04-T05 | Explicit user approval |
| R4 | decision | Cloud sync rejected for v1 | rejected | confirmed | T06-T07 | Privacy rationale; "maybe v2" |
| R5 | requirement | Mobile-first design | disputed | confirmed | T08 | See conflict C1 |
| R6 | artifact | schema.sql updated to v2 (adds elevation_gain) | completed | confirmed | T09-T11 | |
| R7 | suggestion | Dark mode toggle | uncertain | inferred | T12-T13 | "Maybe later" is not approval |
| R8 | requirement | Desktop layout priority | disputed | confirmed | T14 | See conflict C1 |
| R9 | action | Log form completed with date/distance validation | completed | confirmed | T17 | |
| R10 | sensitive | Contact email shared for test feedback | active | confirmed | T18 | Minimize; do not repeat verbatim |
| R11 | priority | Next task: CSV export of all hikes | active | confirmed | T19-T20 | Current objective |

# CONFLICTS AND POSSIBLE SUPERSESSION
- C1: Mobile-first (T08) vs. desktop-priority (T14). Assistant asked for
  confirmation (T15); user deferred (T16). No explicit approval of
  supersession. Likely current state: desktop-priority. User confirmation
  required.

# ARTIFACT REGISTER
- schema.sql — database schema — v2 — referenced in conversation (T11);
  location not supplied.

# MISSING OR UNCERTAIN INFORMATION
- Deployment target: Not supplied.
- Offline support timing/scope: uncertain (T03).

# SENSITIVE OR EXCLUDED INFORMATION
- One personal email address at T18. Excluded from carry-forward; refer to
  source pointer T18 if needed.

# HANDOFF PRIORITIES
1. Confirm layout priority (C1).
2. Build CSV export of all hikes (R11).
3. Preserve v1 cloud-sync rejection (R4).
