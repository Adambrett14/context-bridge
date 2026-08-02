"""Safe Streamlit-secrets access: missing secrets file yields an empty
mapping instead of an exception. Values are never logged."""

from collections.abc import Mapping


def read_app_secrets() -> Mapping[str, object]:
    try:
        import streamlit as st

        return dict(st.secrets)
    except Exception:
        return {}
