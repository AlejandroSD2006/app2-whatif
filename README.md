# App2 WhatIf

SPA de una sola pantalla para explorar historias alternativas. Vue 3/Vite presenta el acceso de
Clerk y el formulario; FastAPI valida la sesión y llama una vez a OpenRouter. No hay persistencia.

## Desarrollo local

Requisitos: Python 3.12, uv 0.13.0, Node.js 22.18 y npm.

1. Copia `backend/.env.example` a `backend/.env` y completa las claves del backend. Copia
   `frontend/.env.example` a `frontend/.env.local` y configura la publishable key.
2. En una terminal, desde `backend/`:

   ```powershell
   uv sync --locked
   uv run pytest
   uv run uvicorn app.main:app --reload
   ```

3. En otra terminal, desde `frontend/`:

   ```powershell
   npm ci
   npm run dev
   ```

Vite estará en `http://localhost:5173` y enviará `/api` al backend en `http://localhost:8000`.
Las pruebas rutinarias usan dobles de Clerk y OpenRouter; no necesitan credenciales ni red externa.

## Despliegue

Consulta [docs/despliegue.md](docs/despliegue.md) para las raíces separadas de Vercel y Docker
Compose. La lista de verificación manual de Clerk está en [docs/validacion-manual.md](docs/validacion-manual.md).