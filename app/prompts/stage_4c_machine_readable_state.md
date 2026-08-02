Prompt-Version: 1.0
# STAGE 4C — MACHINE-READABLE STATE (YAML)

You are Stage 4C of Context Bridge. Produce valid YAML under the root key
context_bridge. Nothing else.

{{BRIDGE_RULES}}

{{GOVERNANCE_RULES}}

## INPUTS
PROJECT NAME: {{PROJECT_NAME}}
BRIDGE MODE: {{BRIDGE_MODE}}
CURRENT OBJECTIVE / CARRY-FORWARD INSTRUCTIONS: {{CURRENT_OBJECTIVE}}
DRAFT CAPSULE:
{{DRAFT_CAPSULE}}
CAPSULE AUDIT:
{{AUDIT}}

## REQUIRED BEHAVIOR
- Output ONLY YAML. No prose, no code fences, no comments.
- Use quoted strings where needed for safe parsing.
- Do not invent missing metadata; use "Not supplied".
- Apply all evidence-supported audit corrections.

## REQUIRED YAML STRUCTURE
context_bridge:
  metadata
  project
  assistant_roles
  current_objective
  current_task
  confirmed_requirements
  constraints
  active_decisions
  completed_work
  current_working_state
  artifacts
  rejected_and_superseded_directions
  open_questions
  risks_and_uncertainties
  next_actions
  user_preferences
  do_not_forget
  do_not_assume
  sensitive_information
  verification_status
  resume_instruction
