<!-- DEMO FIXTURE: bundled sample transcript for Context Bridge Demo Mode.
     Entirely fictional project and people. -->
# Sample Transcript — "Trailhead Tracker" project

[M01] USER: New project: Trailhead Tracker, a small web app to log day hikes.
[M02] ASSISTANT: Understood. What are the core features?
[M03] USER: Log hikes with date, trail name, distance, elevation gain, and
notes. It should work offline eventually.
[M04] ASSISTANT: Suggestion: use SQLite for storage — single file, no server.
[M05] USER: Approved. SQLite it is.
[M06] ASSISTANT: Should v1 sync data to the cloud?
[M07] USER: No. Cloud sync is rejected for v1 — privacy first. Maybe v2.
[M08] USER: The design should be mobile-first.
[M09] ASSISTANT: Noted. I drafted schema.sql v1 with a hikes table.
[M10] USER: Add an elevation_gain column.
[M11] ASSISTANT: Done — schema.sql is now v2.
[M12] ASSISTANT: Suggestion: add a dark mode toggle.
[M13] USER: Hmm, maybe later.
[M14] USER: Actually I mostly plan hikes on my desktop — treat desktop
layout as the priority.
[M15] ASSISTANT: To confirm — does desktop-first replace mobile-first?
[M16] USER: Let's move on, I want to finish the log form today.
[M17] ASSISTANT: Log form completed, with validation for date and distance.
[M18] USER: Send test feedback to jordan.doe@example.com if anything breaks.
[M19] USER: Next up I want CSV export of all hikes.
[M20] ASSISTANT: Understood. CSV export is the next task.
