from spececho_diff.adapters.http import UnsafeTargetError, ensure_allowed
from spececho_diff.domain.models import redact_headers


def test_rejects_unlisted_hosts() -> None:
    try:
        ensure_allowed("https://api.example.com", {"localhost"})
    except UnsafeTargetError as exc:
        assert "not in the safety whitelist" in str(exc)
    else:
        raise AssertionError("expected UnsafeTargetError")


def test_redacts_sensitive_headers() -> None:
    assert redact_headers({"Authorization": "secret", "Accept": "application/json"}) == {
        "Authorization": "***",
        "Accept": "application/json",
    }
