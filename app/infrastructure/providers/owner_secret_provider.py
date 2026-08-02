"""Owner-secret provider: OPTIONAL and disabled by default (CHP).

Built only from deployment/local secrets. Returns None unless explicitly
enabled AND fully configured. The key never appears in UI, logs, or state.
"""

from collections.abc import Mapping

from app.domain.enums import ProviderMode
from app.infrastructure.providers.base import Provider
from app.infrastructure.providers.openai_compatible_provider import (
    OpenAICompatibleProvider,
)


def _is_enabled(value: object) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in {"true", "1", "yes"}
    return False


def build_owner_provider(secrets: Mapping[str, object]) -> Provider | None:
    if not _is_enabled(secrets.get("OWNER_PROVIDER_ENABLED")):
        return None
    base_url = str(secrets.get("OWNER_PROVIDER_BASE_URL") or "").strip()
    model_name = str(secrets.get("OWNER_PROVIDER_MODEL") or "").strip()
    api_key = str(secrets.get("OWNER_PROVIDER_API_KEY") or "").strip()
    if not (base_url and model_name and api_key):
        return None
    return OpenAICompatibleProvider(
        base_url=base_url,
        model_name=model_name,
        api_key=api_key,
        provider_name=str(
            secrets.get("OWNER_PROVIDER_NAME") or "Owner-configured provider"
        ),
        provider_mode=ProviderMode.OWNER_SECRET,
        credential_source="deployment_secret",
    )
