import json

from clerk_backend_api.security.types import AuthStatus
from fastapi.testclient import TestClient

from app.config import Settings
from app.main import create_app


def make_client(clerk_settings, clerk_state_factory, fake_clerk_factory, provider):
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
    return TestClient(application)


def test_authorized_request_returns_only_valid_scenario_once(
    clerk_settings,
    clerk_state_factory,
    fake_clerk_factory,
    fake_openrouter_client,
):
    fake_openrouter_client.generate_json.return_value = json.dumps(
        {
            "narrative": "La historia cambia de rumbo.",
            "consequences": [
                "Primera consecuencia",
                "Segunda consecuencia",
                "Tercera consecuencia",
            ],
            "internal": "must not be returned",
        }
    )
    client = make_client(
        clerk_settings, clerk_state_factory, fake_clerk_factory, fake_openrouter_client
    )

    response = client.post(
        "/api/procesar",
        json={
            "question": "¿Y si...",
            "year": 1492,
            "unrealismLevel": "realista",
        },
        headers={"Authorization": "Bearer fake-token"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "narrative": "La historia cambia de rumbo.",
        "consequences": [
            "Primera consecuencia",
            "Segunda consecuencia",
            "Tercera consecuencia",
        ],
    }
    fake_openrouter_client.generate_json.assert_awaited_once()


def test_invalid_request_returns_422_without_calling_provider(
    clerk_settings,
    clerk_state_factory,
    fake_clerk_factory,
    fake_openrouter_client,
):
    client = make_client(
        clerk_settings, clerk_state_factory, fake_clerk_factory, fake_openrouter_client
    )

    response = client.post(
        "/api/procesar",
        json={
            "question": "Pregunta válida",
            "year": True,
            "unrealismLevel": "realista",
        },
        headers={"Authorization": "Bearer fake-token"},
    )

    assert response.status_code == 422
    assert response.json() == {
        "error": {
            "code": "ENTRADA_INVALIDA",
            "message": "Revisa los datos e inténtalo de nuevo.",
        }
    }
    fake_openrouter_client.generate_json.assert_not_awaited()