from typing import Protocol

from clerk_backend_api import AuthenticateRequestOptions
from fastapi import HTTPException, Request

from app.config import Settings


class ClerkVerifier(Protocol):
    def authenticate_request(
        self, request: Request, options: AuthenticateRequestOptions
    ) -> object: ...


def _unauthorized() -> HTTPException:
    return HTTPException(
        status_code=401,
        detail={
            "error": {
                "code": "NO_AUTORIZADO",
                "message": "Inicia sesión para continuar.",
            }
        },
    )


def verify_clerk_request(
    request: Request, settings: Settings, client: ClerkVerifier
) -> None:
    authorization = request.headers.get("authorization", "")
    scheme, separator, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not separator or not token.strip():
        raise _unauthorized()

    options = AuthenticateRequestOptions(
        secret_key=settings.clerk_secret_key,
        audience=settings.clerk_audience,
        authorized_parties=settings.clerk_authorized_parties,
    )
    try:
        state = client.authenticate_request(request, options)
    except Exception:
        raise _unauthorized() from None

    if not getattr(state, "is_signed_in", False):
        raise _unauthorized()

    payload = getattr(state, "payload", None) or {}
    if payload.get("iss") != settings.clerk_issuer:
        raise _unauthorized()

    authorized_parties = settings.clerk_authorized_parties
    if authorized_parties and payload.get("azp") not in authorized_parties:
        raise _unauthorized()

    expected_audience = settings.clerk_audience
    if expected_audience:
        audience = payload.get("aud")
        audiences = audience if isinstance(audience, list) else [audience]
        if expected_audience not in audiences:
            raise _unauthorized()