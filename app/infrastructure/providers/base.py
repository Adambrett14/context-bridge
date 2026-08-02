"""Provider interface (M2 seed). M3 extends with error classification and streaming."""

from typing import Protocol

from app.domain.enums import ProviderMode, StageName


class Provider(Protocol):
    """Anything that can produce raw output text for one pipeline stage.

    Implementations must never log, echo, or export credentials.
    """

    provider_name: str
    provider_mode: ProviderMode
    model_name: str
    credential_source: str

    def generate_stage_output(
        self,
        stage_name: StageName,
        assembled_prompt: str,
        run_metadata: dict[str, str],
    ) -> str:
        """Return raw stage output text."""
        ...
