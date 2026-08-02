"""Owner provider: disabled by default, enabled only when fully configured."""

from app.domain.enums import ProviderMode
from app.infrastructure.providers.owner_secret_provider import build_owner_provider

FULL_CONFIG = {
    "OWNER_PROVIDER_ENABLED": True,
    "OWNER_PROVIDER_NAME": "Owner test provider",
    "OWNER_PROVIDER_BASE_URL": "https://api.example.test/v1",
    "OWNER_PROVIDER_MODEL": "owner-model",
    "OWNER_PROVIDER_API_KEY": "sk-FAKE-owner-key",
}


def test_absent_or_incomplete_config_disables_owner_mode() -> None:
    assert build_owner_provider({}) is None
    incomplete = dict(FULL_CONFIG)
    incomplete["OWNER_PROVIDER_API_KEY"] = ""
    assert build_owner_provider(incomplete) is None


def test_enabled_config_builds_provider() -> None:
    provider = build_owner_provider(FULL_CONFIG)
    assert provider is not None
    assert provider.provider_mode is ProviderMode.OWNER_SECRET
    assert provider.credential_source == "deployment_secret"
    assert provider.model_name == "owner-model"


def test_string_false_stays_disabled() -> None:
    config = dict(FULL_CONFIG)
    config["OWNER_PROVIDER_ENABLED"] = "false"
    assert build_owner_provider(config) is None
