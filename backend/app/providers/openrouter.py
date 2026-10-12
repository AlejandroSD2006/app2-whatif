from typing import Protocol

from openrouter import OpenRouter, RetryConfig
from openrouter.utils.retries import BackoffStrategy

from app.config import Settings


class ScenarioProvider(Protocol):
    async def generate_json(self, messages: list[dict[str, str]]) -> str | None: ...


class OpenRouterProvider:
    def __init__(self, settings: Settings, client: OpenRouter | None = None) -> None:
        self._client = client or OpenRouter(api_key=settings.openrouter_api_key)
        self._model = settings.openrouter_model
        self._timeout_ms = settings.openrouter_timeout_ms
        self._retries = RetryConfig(
            strategy="none",
            backoff=BackoffStrategy(
                initial_interval=500,
                max_interval=5_000,
                exponent=2,
                max_elapsed_time=25_000,
            ),
            retry_connection_errors=False,
        )

    async def generate_json(self, messages: list[dict[str, str]]) -> str | None:
        completion = await self._client.chat.send_async(
            model=self._model,
            messages=messages,
            temperature=0.8,
            response_format={"type": "json_object"},
            timeout_ms=self._timeout_ms,
            retries=self._retries,
        )
        if not completion.choices:
            return None
        content = completion.choices[0].message.content
        return content if isinstance(content, str) else None