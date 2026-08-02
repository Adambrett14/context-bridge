Prompt-Version: 1.0
# CONTINUITY CAPSULE SCHEMA

Every capsule begins with this header block:
- CAPSULE ID
- PROJECT
- CREATED
- VERSION
- PREVIOUS CAPSULE

Missing metadata is written as "Not supplied." Empty sections are written as
"None identified."

The 19 capsule sections, in exact order:

1. ASSISTANT ROLE — role(s) the assistant played and should resume.
2. USER'S CURRENT OBJECTIVE — the user's present goal, in their terms.
3. CURRENT TASK — the specific task in progress right now.
4. CONFIRMED REQUIREMENTS — only requirements the user explicitly approved.
5. CONSTRAINTS — limits, rules, and boundaries in force.
6. DECISIONS MADE — explicitly approved decisions, with status.
7. WORK COMPLETED — finished work only; partial work is labeled partial.
8. CURRENT WORKING STATE — where things stand at handoff moment.
9. ARTIFACT REGISTER — artifacts referenced, with type/version/status.
10. REJECTED OR SUPERSEDED DIRECTIONS — paths explicitly closed, and why.
11. OPEN QUESTIONS — unresolved questions needing answers.
12. KNOWN RISKS AND UNCERTAINTIES — honest risk and uncertainty list.
13. NEXT RECOMMENDED ACTIONS — ordered, concrete next steps.
14. USER PREFERENCES — stated working style, tone, format preferences.
15. DO NOT FORGET — critical carry-forward items.
16. DO NOT ASSUME — items a new session must not presume resolved.
17. SOURCE POINTERS — real pointers into the source (e.g., message numbers).
18. SENSITIVE INFORMATION — minimized notes on sensitive content handling.
19. RESUME INSTRUCTION — one precise instruction telling the next session
    exactly how to continue.
