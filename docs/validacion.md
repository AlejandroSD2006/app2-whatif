# Validación

Comprobaciones ejecutadas localmente el 2026-10-12:

| Comprobación | Resultado |
|---|---|
| `backend/`: `uv run pytest` | 40 pruebas aprobadas. La suite sustituye Clerk y OpenRouter; no realiza llamadas externas. |
| `frontend/`: `npm run build` | Correcto con Vite 8.3.4; bundle producido en `frontend/dist/`. |
| `backend/`: `uv export --frozen --no-dev --no-emit-project -o requirements.txt` | Correcto; export bloqueado con hashes en `backend/requirements.txt`. |
| `docker compose -f deploy/docker-compose.yml config --quiet` | Correcto con Docker Compose 5.0.2. No se construyeron ni publicaron imágenes. |
| Petición aislada a `openrouter/free` | Correcta con una hipótesis ficticia; respuesta validada con narración y 5 consecuencias. No se imprimió el contenido. |
| `git diff --check` | Sin errores de whitespace. |
| Auditoría de almacenamiento en `backend/app/` y `frontend/src/` | Sin uso de `localStorage`, `sessionStorage`, IndexedDB o base de datos. |
| Auditoría de secretos en fuente y `frontend/dist/` | Sin claves `sk_test_`/`sk_live_`, `CLERK_SECRET_KEY` ni `OPENROUTER_API_KEY`. Los `.env` locales están ignorados por Git. |

## Pendiente manual

- No se validó un inicio de sesión Clerk real ni el rechazo del backend con una sesión real: falta
  una `CLERK_SECRET_KEY` de desarrollo válida en `backend/.env`. El valor no reconocible que se
  había puesto en `.env.example` se sustituyó por su placeholder.
- No se probó el recorrido autenticado de extremo a extremo. Aunque OpenRouter respondió, queda
  iniciar sesión en Clerk desde el navegador y enviar la hipótesis desde la interfaz.
- No se ejecutó `docker compose up` ni se hizo un despliegue real a Vercel o AWS.

Las comprobaciones manuales de acceso están enumeradas en
[validacion-manual.md](validacion-manual.md). No se registraron credenciales ni datos de prueba
personales.