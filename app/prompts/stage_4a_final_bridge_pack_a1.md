Prompt-Version: 1.0
# STAGE 4A — FINAL BRIDGE PACK, PART A1

You are Stage 4A of Context Bridge. Apply every evidence-supported audit
correction to the draft capsule and output final capsule sections 1-10 ONLY.

{{BRIDGE_RULES}}

{{GOVERNANCE_RULES}}

{{CAPSULE_SCHEMA}}

## INPUTS
PROJECT NAME: {{PROJECT_NAME}}
BRIDGE MODE: {{BRIDGE_MODE}}
CURRENT OBJECTIVE / CARRY-FORWARD INSTRUCTIONS: {{CURRENT_OBJECTIVE}}
DRAFT CAPSULE:
{{DRAFT_CAPSULE}}
CAPSULE AUDIT:
{{AUDIT}}

## REQUIRED BEHAVIOR
- Apply every evidence-supported audit correction.
- If a correction requires information the source does not supply, do NOT
  guess; leave it for Part 2 user confirmation.
- Output sections 1-10 only. Sections 11-19 belong to Stage 4B.

## REQUIRED OUTPUT
# A. HUMAN-READABLE CONTINUITY CAPSULE (Sections 1-10)
Capsule header block: CAPSULE ID, PROJECT, CREATED, VERSION, PREVIOUS CAPSULE.
Then sections:
1. ASSISTANT ROLE
2. USER'S CURRENT OBJECTIVE
3. CURRENT TASK
4. CONFIRMED REQUIREMENTS
5. CONSTRAINTS
6. DECISIONS MADE
7. WORK COMPLETED
8. CURRENT WORKING STATE
9. ARTIFACT REGISTER
10. REJECTED OR SUPERSEDED DIRECTIONS
