"""Domain enums for Context Bridge."""

from enum import StrEnum


class BridgeMode(StrEnum):
    """User-selectable continuity depth."""

    STANDARD = "Standard"
    DETAILED = "Detailed"
    EMERGENCY = "Emergency"


class ProviderMode(StrEnum):
    """Which backend executes the pipeline."""

    DEMO = "demo"
    BYOK_OPENAI_COMPATIBLE = "byok_openai_compatible"
    LOCAL_OLLAMA = "local_ollama"
    OWNER_SECRET = "owner_secret"


class StageName(StrEnum):
    """The six pipeline stages, in canonical order."""

    STAGE_1_LEDGER = "stage_1_atomic_memory_ledger"
    STAGE_2_DRAFT_CAPSULE = "stage_2_draft_capsule"
    STAGE_3_AUDIT = "stage_3_capsule_audit"
    STAGE_4A_FINAL_A1 = "stage_4a_final_bridge_pack_a1"
    STAGE_4B_FINAL_A2 = "stage_4b_final_bridge_pack_a2"
    STAGE_4C_YAML_STATE = "stage_4c_machine_readable_state"


STAGE_ORDER: tuple[StageName, ...] = tuple(StageName)


class StageStatus(StrEnum):
    NOT_STARTED = "not_started"
    RUNNING = "running"
    COMPLETE = "complete"
    FAILED = "failed"


class ErrorCategory(StrEnum):
    SOURCE_REQUIRED = "source_required"
    AUTH_ERROR = "auth_error"
    PROVIDER_LIMIT_ERROR = "provider_limit_error"
    HOST_LIMIT_ERROR = "host_limit_error"
    BROWSER_RENDER_ERROR = "browser_render_error"
    TIMEOUT = "timeout"
    MALFORMED_MODEL_OUTPUT = "malformed_model_output"
    YAML_INVALID = "yaml_invalid"
    UNSUPPORTED_FILE_TYPE = "unsupported_file_type"
    FILE_DECODE_ERROR = "file_decode_error"
    EXTERNAL_PROVIDER_UNAVAILABLE = "external_provider_unavailable"
    UNKNOWN_ERROR = "unknown_error"
