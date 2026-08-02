<!-- DEMO FIXTURE: precomputed sample output for Demo Mode replay. -->
# A. HUMAN-READABLE CONTINUITY CAPSULE (Sections 1-10)

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
Cloud sync rejected for v1 (T07) — privacy rationale; revisit in v2.
[Restored per audit correction 1.]
