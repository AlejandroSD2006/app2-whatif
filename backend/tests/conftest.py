import os
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest
from clerk_backend_api.security.types import AuthStatus, RequestState

os.environ.update(
    {
        "CLERK_SECRET_KEY": "sk_test_never_used",
        "CLERK_ISSUER": "https://example.clerk.accounts.dev",
        "CLERK_AUTHORIZED_PARTIES": '["http://localhost:5173"]',
        "OPENROUTER_API_KEY": "sk-or-test-never-used",
        "OPENROUTER_MODEL": "test-model",
        "CORS_ORIGINS": '["http://localhost:5173"]',
    }
)


@pytest.fixture
def clerk_settings() -> SimpleNamespace:
    return SimpleNamespace(
        clerk_secret_key="sk_test_not_a_real_key",
        clerk_issuer="https://example.clerk.accounts.dev",
        clerk_authorized_parties=["http://localhost:5173"],
        clerk_audience=None,
    )


@pytest.fixture
def clerk_state_factory():
    def create(status: AuthStatus, payload: dict[str, object] | None = None) -> RequestState:
        return RequestState(status=status, payload=payload)

    return create


@pytest.fixture
def fake_clerk_factory():
    class FakeClerk:
        def __init__(self, state: RequestState, error: Exception | None = None):
            self.state = state
            self.error = error
            self.calls: list[tuple[object, object]] = []

        def authenticate_request(self, request: object, options: object) -> RequestState:
            self.calls.append((request, options))
            if self.error is not None:
                raise self.error
            return self.state

    def create(state: RequestState, error: Exception | None = None) -> FakeClerk:
        return FakeClerk(state, error)

    return create


@pytest.fixture
def fake_openrouter_client() -> AsyncMock:
    return AsyncMock()