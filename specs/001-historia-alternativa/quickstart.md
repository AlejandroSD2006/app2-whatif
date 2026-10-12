# Quickstart

Comandos comprobados para desarrollo local. El login real de Clerk y las llamadas reales a OpenRouter
requieren credenciales propias; la suite rutinaria usa servicios simulados.

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

Los `.env.example` tienen valores ficticios. No pongas secretos en archivos con prefijo `VITE_` ni
en `.env.example`.

## Backend

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

## Frontend

Desde `frontend/`:

```powershell
npm ci
npm run dev
npm run build
```

Vite sirve la pantalla en `http://localhost:5173` y reenvía `/api` a `http://localhost:8000`.

## Verificación

1. `uv run pytest` ejecuta pruebas con Clerk y OpenRouter simulados; no contacta servicios reales.
2. `npm run build` comprueba el bundle de producción de Vue.
3. El login/logout real de Clerk es manual; sigue [docs/validacion-manual.md](../../docs/validacion-manual.md).
4. Los resultados de comandos ejecutados y límites de la comprobación se registran en
  [docs/validacion.md](../../docs/validacion.md).

## Despliegues previstos

- **Vercel**: desplegar `frontend/` como sitio Vite estático y `backend/` como proyecto FastAPI
  separado. Configurar variables en cada proyecto. Antes de aceptar tráfico, comprobar que el
  timeout de la función configurado por el plan de Vercel es compatible con el timeout del
  proveedor.
- **Docker/EC2**: construir y ejecutar con Docker Compose en Linux; el proxy sirve `dist/` y
  enruta `/api` al servicio backend. Terminar TLS en el proxy y restringir Security Groups. Las
  variables secretas se suministran solo en runtime. No crear almacenamiento persistente.