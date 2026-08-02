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
Log hikes with date, trail name, distance, elevation gain, notes (M03).
Offline support eventually (M03; timing unspecified).

5. CONSTRAINTS
Privacy first: no cloud sync in v1 (M07).

6. DECISIONS MADE
SQLite for storage — explicitly approved (M04-M05).

7. WORK COMPLETED
schema.sql v2 including elevation_gain (M11). Log form with date/distance
validation (M17).

8. CURRENT WORKING STATE
Schema and log form done; CSV export not started.

9. ARTIFACT REGISTER
schema.sql — v2 — location not supplied (M11).

10. REJECTED OR SUPERSEDED DIRECTIONS
Cloud sync rejected for v1 (M07) — privacy rationale; revisit in v2.
[Restored per audit correction 1.]
