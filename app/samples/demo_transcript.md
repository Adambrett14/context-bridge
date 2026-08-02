<!-- DEMO FIXTURE: bundled sample transcript for Context Bridge Demo Mode.
     Entirely fictional project and people. Deliberately unnumbered and
     conversational — the shape of a real copy-pasted chat log. Stage 1
     assigns turn numbers (T01...) itself and declares the convention. -->
User: New project: Trailhead Tracker, a small web app to log day hikes.

Assistant: Understood. What are the core features?

User: Log hikes with date, trail name, distance, elevation gain, and notes. It should work offline eventually.

Assistant: Suggestion: use SQLite for storage — single file, no server.

User: Approved. SQLite it is.

Assistant: Should v1 sync data to the cloud?

User: No. Cloud sync is rejected for v1 — privacy first. Maybe v2.

User: The design should be mobile-first.

Assistant: Noted. I drafted schema.sql v1 with a hikes table.

User: Add an elevation_gain column.

Assistant: Done — schema.sql is now v2.

Assistant: Suggestion: add a dark mode toggle.

User: Hmm, maybe later.

User: Actually I mostly plan hikes on my desktop — treat desktop layout as the priority.

Assistant: To confirm — does desktop-first replace mobile-first?

User: Let's move on, I want to finish the log form today.

Assistant: Log form completed, with validation for date and distance.

User: Send test feedback to jordan.doe@example.com if anything breaks.

User: Next up I want CSV export of all hikes.

Assistant: Understood. CSV export is the next task.
