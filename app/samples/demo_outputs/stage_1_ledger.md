<!-- DEMO FIXTURE: precomputed sample output for Demo Mode replay. -->
# SOURCE CHECK
Usable source found: pasted transcript, 20 numbered messages [M01-M20].
Project name supplied: Trailhead Tracker. Bridge mode: Standard.

# EPISODE MAP
- E1 Scoping (M01-M08): features, storage decision, cloud-sync rejection.
- E2 Build (M09-M17): schema v1→v2, layout conflict emerges, log form done.
- E3 Handoff point (M18-M20): contact info shared, CSV export queued.

# ATOMIC MEMORY LEDGER
| ID | Class | Statement | Status | Confidence | Source | Notes |
|---|---|---|---|---|---|---|
| R1 | requirement | Log hikes: date, trail, distance, elevation gain, notes | active | confirmed | M03 | Core feature set |
| R2 | requirement | Offline support "eventually" | active | confirmed | M03 | Timing unspecified |
| R3 | decision | SQLite for storage | active | confirmed | M04-M05 | Explicit user approval |
| R4 | decision | Cloud sync rejected for v1 | rejected | confirmed | M06-M07 | Privacy rationale; "maybe v2" |
| R5 | requirement | Mobile-first design | disputed | confirmed | M08 | See conflict C1 |
| R6 | artifact | schema.sql updated to v2 (adds elevation_gain) | completed | confirmed | M09-M11 | |
| R7 | suggestion | Dark mode toggle | uncertain | inferred | M12-M13 | "Maybe later" is not approval |
| R8 | requirement | Desktop layout priority | disputed | confirmed | M14 | See conflict C1 |
| R9 | action | Log form completed with date/distance validation | completed | confirmed | M17 | |
| R10 | sensitive | Contact email shared for test feedback | active | confirmed | M18 | Minimize; do not repeat verbatim |
| R11 | priority | Next task: CSV export of all hikes | active | confirmed | M19-M20 | Current objective |

# CONFLICTS AND POSSIBLE SUPERSESSION
- C1: Mobile-first (M08) vs. desktop-priority (M14). Assistant asked for
  confirmation (M15); user deferred (M16). No explicit approval of
  supersession. Likely current state: desktop-priority. User confirmation
  required.

# ARTIFACT REGISTER
- schema.sql — database schema — v2 — referenced in conversation (M11);
  location not supplied.

# MISSING OR UNCERTAIN INFORMATION
- Deployment target: Not supplied.
- Offline support timing/scope: uncertain (M03).

# SENSITIVE OR EXCLUDED INFORMATION
- One personal email address at M18. Excluded from carry-forward; refer to
  source pointer M18 if needed.

# HANDOFF PRIORITIES
1. Confirm layout priority (C1).
2. Build CSV export of all hikes (R11).
3. Preserve v1 cloud-sync rejection (R4).
