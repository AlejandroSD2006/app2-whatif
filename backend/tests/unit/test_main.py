import pytest
from clerk_backend_api.security.types import AuthStatus
from fastapi import Depends
from fastapi.testclient import TestClient
from pydantic import BaseModel

from app.auth import ClerkVerifier
from app.config import Settings
from app.main import create_app, get_clerk_client, get_settings


class ProbePayload(BaseModel):
    value: int


@pytest.fixture
def configured_app(clerk_settings, clerk_state_factory, fake_clerk_factory):
    settings = Settings(
        clerk_secret_key=clerk_settings.clerk_secret_key,
        clerk_issuer=clerk_settings.clerk_issuer,
        clerk_authorized_parties=clerk_settings.clerk_authorized_parties,
        openrouter_api_key="sk-or-test",
        openrouter_model="test-model",
        cors_origins=clerk_settings.clerk_authorized_parties,
    )
    clerk_client = fake_clerk_factory(clerk_state_factory(AuthStatus.SIGNED_OUT))
    return create_app(settings, clerk_client), clerk_client


def test_app_wires_settings_and_clerk_client(configured_app):
    application, clerk_client = configured_app

    @application.post("/probe")
    async def probe(
        payload: ProbePayload,
        app_settings: Settings = Depends(get_settings),
        clerk: ClerkVerifier = Depends(get_clerk_client),
    ):
        return {
            "value": payload.value,
            "model": app_settings.openrouter_model,
            "fake_clerk": clerk is clerk_client,
        }

    response = TestClient(application).post("/probe", json={"value": 7})

    assert response.status_code == 200
    assert response.json() == {"value": 7, "model": "test-model", "fake_clerk": True}


def test_validation_errors_use_safe_spanish_contract(configured_app):
    application, _ = configured_app

    @application.post("/probe")
    async def probe(payload: ProbePayload):
        return {"value": payload.value}

    response = TestClient(application).post("/probe", json={"value": "invalid"})

    assert response.status_code == 422
    assert response.json() == {
        "error": {
            "code": "ENTRADA_INVALIDA",
            "message": "Revisa los datos e inténtalo de nuevo.",
        }
    }


def test_cors_allows_only_configured_origin(configured_app):
    application, _ = configured_app
    client = TestClient(application)
    preflight_headers = {
        "Origin": "http://localhost:5173",
        "Access-Control-Request-Method": "POST",
        "Access-Control-Request-Headers": "authorization,content-type",
    }

    allowed = client.options("/probe", headers=preflight_headers)
    denied = client.options(
        "/probe", headers={**preflight_headers, "Origin": "https://untrusted.example"}
    )

    assert allowed.status_code == 200
    assert allowed.headers["access-control-allow-origin"] == "http://localhost:5173"
    assert denied.status_code == 400
    assert "access-control-allow-origin" not in denied.headers