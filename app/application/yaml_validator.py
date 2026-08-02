"""Validate Stage 4C output: parses as YAML, correct root key, required fields."""

import yaml

REQUIRED_TOP_LEVEL_KEYS: frozenset[str] = frozenset(
    {
        "metadata",
        "project",
        "assistant_roles",
        "current_objective",
        "current_task",
        "confirmed_requirements",
        "constraints",
        "active_decisions",
        "completed_work",
        "current_working_state",
        "artifacts",
        "rejected_and_superseded_directions",
        "open_questions",
        "risks_and_uncertainties",
        "next_actions",
        "user_preferences",
        "do_not_forget",
        "do_not_assume",
        "sensitive_information",
        "verification_status",
        "resume_instruction",
    }
)


def validate_yaml_state(yaml_text: str) -> list[str]:
    """Return a list of validation problems; an empty list means valid."""
    try:
        data = yaml.safe_load(yaml_text)
    except yaml.YAMLError as exc:
        return [f"YAML parse error: {exc}"]
    if not isinstance(data, dict) or "context_bridge" not in data:
        return ["missing root key: context_bridge"]
    body = data["context_bridge"]
    if not isinstance(body, dict):
        return ["context_bridge must be a mapping"]
    missing = REQUIRED_TOP_LEVEL_KEYS - set(body)
    if missing:
        return [f"missing keys: {sorted(missing)}"]
    return []
