import json

import httpx
import pytest
from clerk_backend_api.security.types import AuthStatus
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock

from app.config import Settings
from app.main import create_app, require_authenticated_request


@pytest.mark.parametrize(
    ("failure", "status", "code", "message"),
    [
        (
            "provider",
            502,
            "ERROR_PROVEEDOR",
            "No se pudo generar la respuesta. Inténtalo de nuevo.",
        ),
        (
            "timeout",
            504,
            "TIEMPO_AGOTADO",
            "La generación tardó demasiado. Inténtalo de nuevo.",
        ),
        (
            "empty",
            502,
            "ERROR_PROVEEDOR",
            "No se pudo generar la respuesta. Inténtalo de nuevo.",
        ),
        (
            "malformed",
            502,
            "ERROR_PROVEEDOR",
            "No se pudo generar la respuesta. Inténtalo de nuevo.",
        ),
        (
            "consequences",
            502,
            "ERROR_PROVEEDOR",
            "No se pudo generar la respuesta. Inténtalo de nuevo.",
        ),
    ],
)
def test_provider_failures_return_safe_stable_errors(
    failure,
    status,
    code,
    message,
    clerk_settings,
    clerk_state_factory,
    fake_clerk_factory,
):
    provider = AsyncMock()
    if failure == "provider":
        provider.generate_json.side_effect = RuntimeError("secret provider response")
    elif failure == "timeout":
        provider.generate_json.side_effect = httpx.ReadTimeout("private timeout detail")
    elif failure == "empty":
        provider.generate_json.return_value = None
    elif failure == "malformed":
        provider.generate_json.return_value = "not JSON: private response"
    else:
        provider.generate_json.return_value = json.dumps(
            {"narrative": "Texto", "consequences": ["Una", "Dos"]}
        )

    settings = Settings(
        clerk_secret_key=clerk_settings.clerk_secret_key,
        clerk_issuer=clerk_settings.clerk_issuer,
        clerk_authorized_parties=clerk_settings.clerk_authorized_parties,
        openrouter_api_key="sk-or-test",
        openrouter_model="test-model",
        cors_origins=clerk_settings.clerk_authorized_parties,
    )
    clerk = fake_clerk_factory(
        clerk_state_factory(
            AuthStatus.SIGNED_IN,
            {
                "iss": clerk_settings.clerk_issuer,
                "azp": clerk_settings.clerk_authorized_parties[0],
            },
        )
    )
    application = create_app(settings, clerk, scenario_provider=provider)
    application.dependency_overrides[require_authenticated_request] = lambda: None

    response = TestClient(application).post(
        "/api/procesar",
        headers={"Authorization": "Bearer fake-token"},
        json={"question": "Hipótesis", "year": 1492, "unrealismLevel": "realista"},
    )

    assert response.status_code == status
    assert response.json() == {"error": {"code": code, "message": message}}
    assert "private" not in response.text
    assert "secret provider" not in response.text
    provider.generate_json.assert_awaited_once()