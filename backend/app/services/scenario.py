from pydantic import ValidationError

from app.models import ProviderScenarioOutput, ScenarioRequest, ScenarioResult
from app.providers.openrouter import ScenarioProvider

LEVEL_DESCRIPTIONS = {
    "realista": "realista y ceñido a lo históricamente plausible",
    "ilusionante": "optimista e ilusionante, con cierta exageración",
    "descerebrado": "deliberadamente disparatado y llevado al extremo",
}


class InvalidScenarioOutput(Exception):
    pass


class ScenarioService:
    def __init__(self, provider: ScenarioProvider) -> None:
        self._provider = provider

    async def generate(self, request: ScenarioRequest) -> ScenarioResult:
        messages = [
            {
                "role": "system",
                "content": (
                    "Eres una IA que explora historia alternativa en español. "
                    'Devuelve únicamente un objeto JSON válido con "narrative", '
                    "un relato claro de uno o dos párrafos, y "
                    '"consequences", una lista de entre 3 y 5 consecuencias breves.'
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Hipótesis: {request.question}\n"
                    f"Año de referencia: {request.year}\n"
                    "Estilo: "
                    f"{LEVEL_DESCRIPTIONS[request.unrealismLevel]}"
                ),
            },
        ]
        content = await self._provider.generate_json(messages)
        if not content:
            raise InvalidScenarioOutput

        try:
            provider_output = ProviderScenarioOutput.model_validate_json(content)
        except ValidationError:
            raise InvalidScenarioOutput from None

        return ScenarioResult.model_validate(provider_output.model_dump())