<!-- DEMO FIXTURE: precomputed sample output for Demo Mode replay.
     This DRAFT intentionally contains two flaws that Stage 3 catches:
     section 10 omits the cloud-sync rejection, and section 18 repeats a
     raw email address. Stage 4 shows them corrected. -->
CAPSULE ID: CB-DEMO-001
PROJECT: Trailhead Tracker
CREATED: Not supplied
VERSION: 1
PREVIOUS CAPSULE: None

1. ASSISTANT ROLE
Software build assistant for a small hike-logging web app.

2. USER'S CURRENT OBJECTIVE
Add CSV export of all logged hikes.

3. CURRENT TASK
Begin CSV export implementation; log form was just completed.

4. CONFIRMED REQUIREMENTS
Log hikes with date, trail name, distance, elevation gain, notes (T03).
Offline support eventually (T03; timing unspecified).

5. CONSTRAINTS
Privacy first: no cloud sync in v1 (T07).

6. DECISIONS MADE
SQLite for storage — explicitly approved (T04-T05).

7. WORK COMPLETED
schema.sql v2 including elevation_gain (T11). Log form with date/distance
validation (T17).

8. CURRENT WORKING STATE
Schema and log form done; CSV export not started.

9. ARTIFACT REGISTER
schema.sql — v2 — location not supplied (T11).

10. REJECTED OR SUPERSEDED DIRECTIONS
None identified.

11. OPEN QUESTIONS
Layout priority: mobile-first (T08) vs. desktop-priority (T14) — user
deferred confirmation (T15-T16).

12. KNOWN RISKS AND UNCERTAINTIES
Offline scope undefined. Layout conflict unresolved.

13. NEXT RECOMMENDED ACTIONS
1) Confirm layout priority. 2) Implement CSV export.

14. USER PREFERENCES
Privacy-conscious; prefers moving fast ("let's move on", T16).

15. DO NOT FORGET
Cloud sync is off the table for v1. Dark mode was suggested, never approved.

16. DO NOT ASSUME
Do not assume desktop-priority was formally approved (C1 unresolved).

17. SOURCE POINTERS
Turn numbers T01-T20 were assigned by the evidence ledger in reading order;
the original transcript is unnumbered. T03 requirements; T04-T05 storage
decision; T07 sync rejection; T08/T14 layout conflict; T11 schema v2; T17
log form; T19 CSV objective.

18. SENSITIVE INFORMATION
Test feedback contact: jordan.doe@example.com (T18).

19. RESUME INSTRUCTION
Resume by confirming layout priority (C1), then implement CSV export of all
hikes against schema.sql v2.
