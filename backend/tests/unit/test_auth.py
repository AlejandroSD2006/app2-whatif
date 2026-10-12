from fastapi import HTTPException
from starlette.requests import Request
from clerk_backend_api.security.types import AuthStatus

from app.auth import verify_clerk_request


def make_request(authorization: str | None = "Bearer test-token") -> Request:
    headers = []
    if authorization is not None:
        headers.append((b"authorization", authorization.encode()))
    scope = {
        "type": "http",
        "http_version": "1.1",
        "method": "POST",
        "scheme": "http",
        "path": "/api/procesar",
        "raw_path": b"/api/procesar",
        "query_string": b"",
        "headers": headers,
        "client": ("testclient", 50000),
        "server": ("testserver", 80),
    }
    return Request(scope)


def test_signed_out_request_is_rejected_before_returning_identity(
    clerk_settings, clerk_state_factory, fake_clerk_factory
):
    client = fake_clerk_factory(clerk_state_factory(AuthStatus.SIGNED_OUT))

    try:
        verify_clerk_request(make_request(), clerk_settings, client)
    except HTTPException as error:
        assert error.status_code == 401
        assert error.detail == {
            "error": {"code": "NO_AUTORIZADO", "message": "Inicia sesión para continuar."}
        }
    else:
        raise AssertionError("An unauthenticated request must be rejected")


def test_missing_token_is_rejected_without_clerk_verification(
    clerk_settings, clerk_state_factory, fake_clerk_factory
):
    client = fake_clerk_factory(clerk_state_factory(AuthStatus.SIGNED_OUT))

    try:
        verify_clerk_request(make_request(None), clerk_settings, client)
    except HTTPException as error:
        assert error.status_code == 401
    else:
        raise AssertionError("A request without a token must be rejected")

    assert client.calls == []


def test_signed_in_token_with_wrong_issuer_is_rejected(
    clerk_settings, clerk_state_factory, fake_clerk_factory
):
    state = clerk_state_factory(
        AuthStatus.SIGNED_IN,
        {"iss": "https://unexpected.issuer", "azp": "http://localhost:5173"},
    )
    client = fake_clerk_factory(state)

    try:
        verify_clerk_request(make_request(), clerk_settings, client)
    except HTTPException as error:
        assert error.status_code == 401
    else:
        raise AssertionError("A token from an unexpected issuer must be rejected")


def test_signed_in_token_with_wrong_authorized_party_is_rejected(
    clerk_settings, clerk_state_factory, fake_clerk_factory
):
    state = clerk_state_factory(
        AuthStatus.SIGNED_IN,
        {"iss": clerk_settings.clerk_issuer, "azp": "https://unexpected.example"},
    )
    client = fake_clerk_factory(state)

    try:
        verify_clerk_request(make_request(), clerk_settings, client)
    except HTTPException as error:
        assert error.status_code == 401
    else:
        raise AssertionError("A token from an unexpected party must be rejected")


def test_authorized_signed_in_token_is_accepted_and_sdk_checks_parties(
    clerk_settings, clerk_state_factory, fake_clerk_factory
):
    state = clerk_state_factory(
        AuthStatus.SIGNED_IN,
        {"iss": clerk_settings.clerk_issuer, "azp": "http://localhost:5173"},
    )
    client = fake_clerk_factory(state)

    identity = verify_clerk_request(make_request(), clerk_settings, client)

    assert identity is None
    assert len(client.calls) == 1
    request, options = client.calls[0]
    assert request.headers["authorization"] == "Bearer test-token"
    assert options.secret_key == clerk_settings.clerk_secret_key
    assert options.authorized_parties == clerk_settings.clerk_authorized_parties