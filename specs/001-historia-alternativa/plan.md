<!-- Speckit plan for the reviewed specification. This is a design artifact, not product code. -->
# Implementation Plan: Generación de historia alternativa

**Branch**: `001-historia-alternativa` (identificador documental; no se crea rama Git)  
**Date**: 2026-10-12  
**Spec**: [spec.md](spec.md)

## Summary

Construir una SPA Vue de una sola pantalla que envíe una hipótesis a FastAPI. FastAPI validará el
Bearer token de Clerk antes de invocar una sola vez al SDK oficial Python de OpenRouter; la salida
se validará y se devolverá con el contrato definido en la especificación. No habrá persistencia ni
historial. Las pruebas automatizadas sustituirán tanto la verificación de Clerk como el cliente de
OpenRouter.

## Technical Context

**Language/Version**: Python 3.12; JavaScript/TypeScript del ecosistema Node.js 22.18.0.  
**Primary Dependencies**: FastAPI 0.143.0, Pydantic 2.12.5, pydantic-settings 2.15.0, Uvicorn
0.54.0, Clerk Backend SDK `clerk-backend-api` 7.0.0, OpenRouter SDK `openrouter` 1.3.43;
Vue 3.5.43, Vite 8.3.4, `@vitejs/plugin-vue` 6.0.10, Tailwind CSS 4.3.3 con
`@tailwindcss/vite` 4.3.3 y Clerk Vue SDK `@clerk/vue` 2.5.12. Desarrollo y tests: pytest
9.1.1 y HTTPX 0.28.1; gestión/lock Python con uv 0.13.0. Son versiones candidatas consultadas
en fuentes oficiales el 2026-10-12; se fijarán en los manifiestos y lockfiles del proyecto antes
de instalar dependencias.
**Storage**: Ninguno. Hipótesis, token recibido, narración y consecuencias solo viven en memoria
durante el procesamiento y la vista activa.
**Testing**: pytest + FastAPI TestClient/HTTPX; mocks del verificador Clerk y del adaptador
OpenRouter. Pruebas de interfaz/build sin servicios reales; Clerk real se comprueba manualmente.
**Target Platform**: Desarrollo local en Windows; producción en Vercel (dos proyectos separados)
y alternativa Docker Compose sobre Linux/EC2 detrás de proxy HTTPS.
**Project Type**: Aplicación web con backend API y frontend SPA.
**Performance Goals**: Un envío válido produce una sola petición al proveedor; la llamada al
proveedor tiene timeout de 25 segundos. El endpoint no almacena trabajos ni resultados.
**Constraints**: Pregunta de 1–280 caracteres después de quitar espacios exteriores; año entero
0–3000 inclusive; tres niveles exactos; salida con narración y de 3 a 5 consecuencias no vacías.
Respuestas HTTP 200/401/422/502/504. No reintentos del SDK de OpenRouter. El presupuesto de
ejecución de cada plataforma debe permitir completar o cancelar la llamada de 25 s; verificar el
límite disponible al configurar Vercel y documentar cualquier ajuste por plataforma.
**Scale/Scope**: Una pantalla, un formulario, una ruta de procesamiento, una API de IA; sin
cuentas propias, persistencia, historial, chat ni rutas de navegación.

## Constitution Check

| Principio | Resultado | Aplicación en el plan |
|---|---|---|
| Alcance mínimo e inmutable | PASS | Una SPA, una función, un proveedor; sin almacenamiento ni historial. |
| Contratos explícitos y stack obligatorio | PASS | FastAPI/Pydantic y Vue/Vite/Tailwind; contrato HTTP definido antes de tareas. |
| Pruebas rutinarias sin servicios reales | PASS | Mocks de Clerk/OpenRouter; integraciones reales solo manuales. |
| Seguridad antes del procesamiento | PASS | Verificar token y claims antes del servicio IA; secretos solo en backend. |
| Flujo simple, accesible y revisable | PASS | Estados en una pantalla, bloqueo de duplicados y texto seguro; revisión al cierre de fase. |

No hay excepciones constitucionales que requieran justificación.

## Architecture and Request Flow

1. La SPA presenta `<SignIn>` de Clerk integrado en la misma pantalla cuando no hay sesión; con
  sesión, muestra formulario y acción de cierre de sesión. No se usa vue-router.
2. Ante un envío, el cliente valida para dar feedback, obtiene un token mediante
  `useAuth().getToken()` y manda `Authorization: Bearer <token>` junto con el JSON. Deshabilita
  el envío mientras espera y mantiene solo el resultado actual en memoria.
3. FastAPI valida el cuerpo con Pydantic y procesa errores 422. La dependencia de autenticación
  adapta la petición de Starlette al formato requerido por Clerk y usa
  `authenticate_request`; luego exige issuer configurado (`iss`) y claims de audiencia/parte
  autorizada (`aud`/`azp`) según configuración. Ninguna ruta de IA se alcanza antes de esa
  comprobación.
4. Un servicio de dominio prepara la instrucción en español y llama al adaptador OpenRouter una
  vez con salida JSON. Configura timeout de 25 000 ms y
  `RetryConfig(strategy="none", ...)`; no usa retries predeterminados del SDK. Valida la salida
  en un modelo Pydantic y solo devuelve `narrative` y `consequences`.
5. Un manejador central traduce fallos del proveedor y respuestas inservibles a 502 y timeout a
  504 con el esquema de error estable, sin texto del proveedor ni datos de entrada.

El frontend enviará CORS solo desde los orígenes locales/de producción configurados y con
`Authorization`/`Content-Type`. Las variables públicas `VITE_CLERK_PUBLISHABLE_KEY` y el origen
público del backend no son secretos. La clave secreta Clerk, el issuer esperado y la clave/modelo
OpenRouter permanecen en el entorno del backend.

## Deployment Design

- **Vercel**: proyecto frontend con raíz `frontend/`, comando de build Vite y salida `dist/`;
  proyecto backend con raíz `backend/`, función Python FastAPI y configuración/secretos propios.
  Mantener `pyproject.toml` + `uv.lock`; exportar requirements bloqueados para detección Python
  con `uv export --frozen --no-dev --no-emit-project -o requirements.txt` desde la raíz backend.
  Solo la publishable key Clerk se expone al bundle. Confirmar el límite de duración de funciones
  habilitado para la cuenta y el plan al hacer el despliegue.
- **Docker/EC2**: Docker Compose con frontend estático y backend en servicios separados, proxy
  de mismo origen que enruta `/api` al backend por nombre de servicio. Secretos se inyectan en
  runtime desde el entorno/gestor de secretos; no se copian a imágenes, argumentos de build ni
  volúmenes persistentes. EC2 expone HTTPS mediante proxy y Security Group limitado a tráfico
  web/administración necesaria; no se añade base de datos.

## Project Structure

```text
backend/
├── api/
│   └── index.py             # adaptador de entrada de función Vercel
├── app/
│   ├── main.py              # creación FastAPI, middleware y ruta
│   ├── config.py            # configuración por entorno
│   ├── models.py            # esquemas request/response/error
│   ├── auth.py              # adaptador/verificador Clerk
│   ├── services/
│   │   └── scenario.py      # caso de uso
│   └── providers/
│       └── openrouter.py    # cliente aislado, timeout y retries desactivados
├── tests/
│   ├── unit/
│   └── integration/
├── pyproject.toml
├── uv.lock
└── requirements.txt         # export bloqueado para Vercel
frontend/
├── src/
│   ├── App.vue               # pantalla única y estados
│   ├── components/           # formulario, acceso y resultado
│   └── services/api.js       # fetch a POST /api/procesar
├── index.html
├── package.json
└── vite.config.js
deploy/
├── docker-compose.yml
└── proxy.conf                # proxy /api y frontend estático
```

**Structure Decision**: Monorepo liviano con `backend/` y `frontend/` para mantener separadas las
raíces de los dos proyectos Vercel, y `deploy/` para el único despliegue en contenedores. Los
tests del proveedor y la autenticación se inyectan en el backend; no se crea un paquete compartido
ni una capa de datos.

## Implementation Sequence

1. Fase 5: generar tareas pequeñas y revisar correspondencia tarea/spec/constitución; backend y
  pruebas antes de frontend.
2. Fase 6: implementar modelos/configuración, auth mockeable, servicio IA y errores; ejecutar
  pytest enfocado después de cada lote. Después construir SPA, integración con Clerk, manejo de
  estados y build local.
3. Fase 7: escribir guía de ejecución/configuración, pruebas y despliegues; diagramas y ERS solo
  con la plantilla requerida por el usuario (no se encontró `plantillaERS.md`).
4. Fase 8: añadir archivos/configuración de Vercel y Docker/EC2, validar builds/configuración sin
  publicar despliegues; el usuario realiza despliegues reales.

## Verification Gates

- Backend: casos request en límites 280/281, vacío, años 0/3000 y fuera de rango, nivel admitido
  y desconocido; coerciones no permitidas; 401 para token ausente/inválido/caducado; asserts de
  cero llamadas ante rechazo y exactamente una ante éxito.
- Proveedor: timeout simulado, error, respuesta vacía/malformada y consecuencias fuera de rango;
  comprobar 504/502 sin filtrar datos sensibles.
- Frontend: build Vite, estados de acceso/espera/éxito/error, bloqueo de duplicados, logout y que
  salida se inserte como texto; revisar que no haya almacenamiento web ni llamadas IA directas.
- Despliegue: comprobar export de uv congelado, build estático y configuración del proxy/Compose;
  no desplegar en cuentas reales desde esta fase.
