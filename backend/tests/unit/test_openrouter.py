import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock

from app.config import Settings
from app.providers.openrouter import OpenRouterProvider


def test_provider_sends_one_json_request_with_timeout_and_no_retries():
    settings = Settings(
        clerk_secret_key="sk_test_never_used",
        clerk_issuer="https://example.clerk.accounts.dev",
        clerk_authorized_parties=["http://localhost:5173"],
        openrouter_api_key="sk-or-test",
        openrouter_model="test/model",
        openrouter_timeout_ms=1234,
        cors_origins=["http://localhost:5173"],
    )
    client = AsyncMock()
    client.chat.send_async.return_value = SimpleNamespace(
        choices=[
            SimpleNamespace(
                message=SimpleNamespace(content='{"narrative":"ok"}')
            )
        ]
    )
    provider = OpenRouterProvider(settings, client)
    messages = [{"role": "user", "content": "Hipótesis"}]

    content = asyncio.run(provider.generate_json(messages))

    assert content == '{"narrative":"ok"}'
    client.chat.send_async.assert_awaited_once_with(
        model="test/model",
        messages=messages,
        temperature=0.8,
        response_format={"type": "json_object"},
        timeout_ms=1234,
        retries=client.chat.send_async.await_args.kwargs["retries"],
    )
    assert client.chat.send_async.await_args.kwargs["retries"].strategy == "none"
    assert client.chat.send_async.await_args.kwargs["retries"].retry_connection_errors is False