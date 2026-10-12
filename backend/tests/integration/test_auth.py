import pytest
from clerk_backend_api.security.types import AuthStatus
from fastapi import Depends
from fastapi.testclient import TestClient

from app.config import Settings
from app.main import create_app, require_authenticated_request


def make_settings(clerk_settings) -> Settings:
    return Settings(
        clerk_secret_key=clerk_settings.clerk_secret_key,
        clerk_issuer=clerk_settings.clerk_issuer,
        clerk_authorized_parties=clerk_settings.clerk_authorized_parties,
        openrouter_api_key="sk-or-test",
        openrouter_model="test-model",
        cors_origins=clerk_settings.clerk_authorized_parties,
    )


@pytest.mark.parametrize("failure", ["missing", "invalid", "expired", "issuer", "party"])
def test_rejected_auth_never_calls_provider(
    failure,
    clerk_settings,
    clerk_state_factory,
    fake_clerk_factory,
    fake_openrouter_client,
):
    payload = {
        "iss": clerk_settings.clerk_issuer,
        "azp": clerk_settings.clerk_authorized_parties[0],
    }
    error = None
    if failure == "issuer":
        payload["iss"] = "https://unexpected.example"
    elif failure == "party":
        payload["azp"] = "https://unexpected.example"
    elif failure in {"invalid", "expired"}:
        error = ValueError(f"fake {failure} token")

    clerk = fake_clerk_factory(
        clerk_state_factory(AuthStatus.SIGNED_IN, payload), error=error
    )
    application = create_app(make_settings(clerk_settings), clerk)

    @application.post("/protected")
    async def protected(_: None = Depends(require_authenticated_request)):
        await fake_openrouter_client.generate()
        return {"ok": True}

    headers = {} if failure == "missing" else {"Authorization": "Bearer fake-token"}
    response = TestClient(application).post("/protected", headers=headers)

    assert response.status_code == 401
    assert response.json() == {
        "error": {
            "code": "NO_AUTORIZADO",
            "message": "Inicia sesión para continuar.",
        }
    }
    fake_openrouter_client.generate.assert_not_awaited()
    assert len(clerk.calls) == (0 if failure == "missing" else 1)


def test_authorized_request_reaches_provider_once(
    clerk_settings,
    clerk_state_factory,
    fake_clerk_factory,
    fake_openrouter_client,
):
    clerk = fake_clerk_factory(
        clerk_state_factory(
            AuthStatus.SIGNED_IN,
            {
                "iss": clerk_settings.clerk_issuer,
                "azp": clerk_settings.clerk_authorized_parties[0],
            },
        )
    )
    application = create_app(make_settings(clerk_settings), clerk)

    @application.post("/protected")
    async def protected(_: None = Depends(require_authenticated_request)):
        await fake_openrouter_client.generate()
        return {"ok": True}

    response = TestClient(application).post(
        "/protected", headers={"Authorization": "Bearer fake-token"}
    )

    assert response.status_code == 200
    fake_openrouter_client.generate.assert_awaited_once()