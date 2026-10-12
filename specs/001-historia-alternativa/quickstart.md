# Quickstart de implementación

Este documento fija comandos previstos para la implementación. No implica que dependencias estén
instaladas ni que se hayan ejecutado tests o builds.

## Requisitos locales

- Python 3.12 y uv 0.13.0.
- Node.js 22.18.0 y npm.
- Proyecto Clerk de desarrollo y clave OpenRouter para la ejecución manual real. No se necesitan
  credenciales externas para los tests rutinarios.

## Variables de entorno

Backend: `CLERK_SECRET_KEY`, `CLERK_ISSUER`, `CLERK_AUTHORIZED_PARTIES`, `OPENROUTER_API_KEY`,
`OPENROUTER_MODEL`, `OPENROUTER_TIMEOUT_MS=25000` y `CORS_ORIGINS`.

Frontend: `VITE_CLERK_PUBLISHABLE_KEY` y `VITE_API_BASE_URL` (vacío/mismo origen en el despliegue
con proxy). Solo `VITE_CLERK_PUBLISHABLE_KEY` es una clave; es pública y puede compilarse en el
bundle. Ninguna clave secreta se configura con prefijo `VITE_`.

Los archivos `.env.example` tendrán valores ficticios y nunca credenciales utilizables.

## Comandos previstos

Desde `backend/`:

```powershell
uv sync --locked
uv run pytest
uv run uvicorn app.main:app --reload
```

Desde `frontend/`:

```powershell
npm ci
npm run dev
npm run build
```

La interfaz local usa la URL del backend configurada en `VITE_API_BASE_URL`; el backend permite
solo los orígenes de desarrollo configurados en `CORS_ORIGINS`.

## Verificación prevista

1. pytest unitario/HTTP con Clerk y OpenRouter simulados: no debe haber acceso de red externo.
2. `npm run build` y pruebas de estados del formulario.
3. Prueba manual separada de login/logout Clerk y solicitud autenticada; no se ejecutará desde la
   suite automatizada ni se enviarán secretos a logs.
4. Revisar que el body de éxito tenga solo `narrative` y `consequences`, y que un timeout simulado
   termina en 504 a los 25 segundos configurados sin retries.

## Despliegues previstos

- **Vercel**: desplegar `frontend/` como sitio Vite estático y `backend/` como proyecto FastAPI
  separado. Configurar variables en cada proyecto. Antes de aceptar tráfico, comprobar que el
  timeout de la función configurado por el plan de Vercel es compatible con el timeout del
  proveedor.
- **Docker/EC2**: construir y ejecutar con Docker Compose en Linux; el proxy sirve `dist/` y
  enruta `/api` al servicio backend. Terminar TLS en el proxy y restringir Security Groups. Las
  variables secretas se suministran solo en runtime. No crear almacenamiento persistente.