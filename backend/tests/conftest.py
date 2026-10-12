from types import SimpleNamespace

import pytest
from clerk_backend_api.security.types import AuthStatus, RequestState


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
        def __init__(self, state: RequestState):
            self.state = state
            self.calls: list[tuple[object, object]] = []

        def authenticate_request(self, request: object, options: object) -> RequestState:
            self.calls.append((request, options))
            return self.state

    return FakeClerk