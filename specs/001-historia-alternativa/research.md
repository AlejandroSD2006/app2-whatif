# Investigación técnica

**Fecha de consulta**: 2026-10-12  
**Estado**: decisiones para revisión de plan; no se han instalado dependencias ni ejecutado
integraciones.

## Decisiones

| Tema | Decisión | Motivo / consecuencia |
|---|---|---|
| Framework backend | FastAPI + Pydantic | Validación declarativa del JSON, errores 422 y testeo HTTP sin servidor externo. |
| Autenticación | SDKs oficiales `@clerk/vue` y `clerk-backend-api` | La SPA obtiene el Bearer token; el servidor verifica criptográficamente antes del caso de uso. Mock de la frontera SDK en pytest. |
| Claims Clerk | Validar `iss` configurado además de la verificación SDK; revisar `aud`/`azp` con `authorized_parties` | El verificador Python inspeccionado no comprueba automáticamente issuer; solo se inspeccionan claims tras validar firma y expiración. Nunca decodificar para autorizar. |
| Proveedor IA | SDK oficial Python `openrouter` | Tiene respuesta estructurada JSON y timeout configurable; cliente aislado tras un adaptador reemplazable en tests. |
| Llamada exactamente una vez | Pasar `RetryConfig(strategy="none", ...)` en cada llamada | La configuración predeterminada del SDK reintenta errores 5xx; ello podría convertir un envío en varias peticiones. Con estrategia `none`, la petición sigue una única invocación sin retries automáticos. |
| Timeout | 25 000 ms para la petición de OpenRouter | Limita espera y permite probar diferenciación de 504; el despliegue debe permitir al menos ese margen. Verificar el límite efectivo del plan Vercel antes de desplegar. |
| Lock de dependencias | `pyproject.toml`/`uv.lock` como fuente; export `requirements.txt` para Vercel | uv documenta export desde el lockfile y exclusión del grupo dev; congelar export para evitar resolver versiones distintas durante deploy. |
| Vercel | Dos proyectos: Vite estático y FastAPI Function | Permite roots y variables por runtime; el cliente solo recibe claves públicas. No hay una API de IA desde el navegador. |
| Docker/EC2 | Compose, proxy de mismo origen y servicios por nombre | Simplifica CORS en el despliegue propio; proxy HTTPS al frente y secretos en runtime, sin volúmenes de datos. |

## Versiones candidatas consultadas

| Componente | Versión candidata |
|---|---:|
| Python | 3.12 |
| FastAPI | 0.143.0 |
| Pydantic | 2.12.5 (compatible with OpenRouter SDK's `<2.13` requirement) |
| pydantic-settings | 2.15.0 |
| Uvicorn | 0.54.0 |
| `clerk-backend-api` | 7.0.0 |
| `openrouter` | 1.3.43 |
| pytest | 9.1.1 |
| HTTPX | 0.28.1 |
| Node.js | 22.18.0 |
| Vue | 3.5.43 |
| Vite | 8.3.4 |
| `@vitejs/plugin-vue` | 6.0.10 |
| Tailwind CSS / `@tailwindcss/vite` | 4.3.3 / 4.3.3 |
| `@clerk/vue` | 2.5.12 |
| uv | 0.13.0 |
| Vercel CLI | 63.1.2 (referencia de consulta; no dependencia de runtime) |

Estas versiones son candidatas, no instalaciones comprobadas en este repositorio. En Fase 6 se
validará compatibilidad al resolver los lockfiles; un conflicto exige revisar el plan antes de
cambiar el stack requerido.

## Fuentes oficiales consultadas

- OpenRouter Python SDK: <https://github.com/OpenRouterTeam/python-sdk> y
  <https://openrouter.ai/docs/sdks/python> (argumentos JSON/timeout; retries por defecto; estrategia `none`).
- Clerk Vue: <https://clerk.com/docs/quickstarts/vue> y
  <https://clerk.com/docs/references/vue/overview> (SDK, componente de acceso y `useAuth`).
- Clerk Backend Python SDK: <https://github.com/clerk/clerk-sdk-python> (verificación de request,
  authorized parties y claims; issuer requiere comparación explícita después de validar token).
- Vercel FastAPI: <https://vercel.com/docs/frameworks/backend/fastapi> (funciones Python y
  configuración de despliegue); <https://vercel.com/docs/functions/runtimes/python> (dependencias
  desde manifests Python).
- Vercel Vite: <https://vercel.com/docs/frameworks/frontend/vite> (build estático y `dist`).
- uv export: <https://docs.astral.sh/uv/reference/cli/#uv-export> (export del lockfile,
  `--frozen`, `--no-dev`, `--no-emit-project`).
- Docker Compose: <https://docs.docker.com/compose/how-tos/networking/> (resolución por nombre de
  servicio/red de Compose).
- AWS EC2 Security Groups: <https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-security-groups.html>
  (firewall stateful asociado a instancias).

## Riesgos pendientes de validación

- El límite de duración de Vercel depende de la configuración y del plan de la cuenta; confirmar
  que permite el timeout elegido y ajustar el timeout documentado antes de habilitar producción.
- Verificar en Fase 6 las firmas concretas de SDKs para `RetryConfig`, `authenticate_request`,
  `authorized_parties` y el componente Vue. Los tests deben fijar el comportamiento observable,
  no depender de red externa.
- El modelo de OpenRouter se elegirá por `OPENROUTER_MODEL`; no se fija un slug de modelo ni se
  hace una petición real durante pruebas rutinarias.