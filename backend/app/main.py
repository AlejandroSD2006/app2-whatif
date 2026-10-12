from clerk_backend_api import Clerk
import httpx
from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.auth import ClerkVerifier, verify_clerk_request
from app.config import Settings
from app.models import ScenarioRequest, ScenarioResult
from app.providers.openrouter import OpenRouterProvider, ScenarioProvider
from app.services.scenario import ScenarioService

PROVIDER_ERROR = {
    "error": {
        "code": "ERROR_PROVEEDOR",
        "message": "No se pudo generar la respuesta. Inténtalo de nuevo.",
    }
}
PROVIDER_TIMEOUT = {
    "error": {
        "code": "TIEMPO_AGOTADO",
        "message": "La generación tardó demasiado. Inténtalo de nuevo.",
    }
}


def get_settings(request: Request) -> Settings:
    return request.app.state.settings


def get_clerk_client(request: Request) -> ClerkVerifier:
    return request.app.state.clerk_client


def get_scenario_service(request: Request) -> ScenarioService:
    return request.app.state.scenario_service


def require_authenticated_request(
    request: Request,
    settings: Settings = Depends(get_settings),
    clerk_client: ClerkVerifier = Depends(get_clerk_client),
) -> None:
    verify_clerk_request(request, settings, clerk_client)


def create_app(
    settings: Settings | None = None,
    clerk_client: ClerkVerifier | None = None,
    scenario_provider: ScenarioProvider | None = None,
) -> FastAPI:
    configured_settings = settings or Settings()
    configured_clerk = clerk_client or Clerk(
        bearer_auth=configured_settings.clerk_secret_key
    )
    configured_provider = scenario_provider or OpenRouterProvider(configured_settings)

    application = FastAPI()
    application.state.settings = configured_settings
    application.state.clerk_client = configured_clerk
    application.state.scenario_service = ScenarioService(configured_provider)
    application.add_middleware(
        CORSMiddleware,
        allow_origins=configured_settings.cors_origins,
        allow_methods=["POST"],
        allow_headers=["Authorization", "Content-Type"],
    )

    @application.exception_handler(RequestValidationError)
    async def validation_error_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=422,
            content={
                "error": {
                    "code": "ENTRADA_INVALIDA",
                    "message": "Revisa los datos e inténtalo de nuevo.",
                }
            },
        )

    @application.exception_handler(HTTPException)
    async def http_error_handler(
        request: Request, exc: HTTPException
    ) -> JSONResponse:
        content = (
            exc.detail
            if isinstance(exc.detail, dict) and "error" in exc.detail
            else {"detail": exc.detail}
        )
        return JSONResponse(
            status_code=exc.status_code,
            content=content,
            headers=exc.headers,
        )

    @application.post(
        "/api/procesar",
        response_model=ScenarioResult,
        dependencies=[Depends(require_authenticated_request)],
    )
    async def process_scenario(
        payload: ScenarioRequest,
        service: ScenarioService = Depends(get_scenario_service),
    ) -> ScenarioResult:
        try:
            return await service.generate(payload)
        except (httpx.TimeoutException, TimeoutError):
            raise HTTPException(status_code=504, detail=PROVIDER_TIMEOUT) from None
        except Exception:
            raise HTTPException(status_code=502, detail=PROVIDER_ERROR) from None

    return application


app = create_app()