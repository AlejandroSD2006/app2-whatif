# Despliegue

> **Nota:** el plan actual es desplegar la aplicación completa en AWS (una instancia EC2 con Docker
> Compose). La guía paso a paso está en [despliegue-aws-ec2.md](despliegue-aws-ec2.md). La opción de
> Vercel de este documento se dejó preparada en su momento, pero ya no es la que se va a usar; se
> mantiene aquí solo como referencia.

No se realizan despliegues desde las pruebas. Configura las credenciales y dominios en cada
plataforma antes de aceptar tráfico real.

## Vercel

Usa dos proyectos separados:

1. Backend con raíz `backend/`. Desde esa carpeta genera el manifiesto de dependencias bloqueado:

   ```powershell
   uv sync --locked
   uv export --frozen --no-dev --no-emit-project -o requirements.txt
   ```

   `api/index.py` exporta la aplicación FastAPI. Configura en el proyecto backend `CLERK_SECRET_KEY`,
   `CLERK_ISSUER`, `CLERK_AUTHORIZED_PARTIES`, `CLERK_AUDIENCE` si se ha añadido el claim, y las
   variables `OPENROUTER_*`.

2. Frontend con raíz `frontend/`, build `npm run build` y salida `dist/`. Configura
   `VITE_CLERK_PUBLISHABLE_KEY` y `VITE_API_BASE_URL` con la URL del backend.

Añade el origen exacto del frontend a `CLERK_AUTHORIZED_PARTIES` y `CORS_ORIGINS` del backend.
Comprueba que el plan y el límite de duración de la función permiten completar el timeout OpenRouter
de 25 segundos. La clave publishable puede formar parte del bundle; nunca expongas claves `CLERK_SECRET_KEY`
ni `OPENROUTER_API_KEY` en variables `VITE_*`.

## Docker Compose

1. Crea `backend/.env` a partir de `backend/.env.example` y configura credenciales válidas. Este
   archivo se inyecta al contenedor en runtime y está excluido del contexto de build.
2. En PowerShell, proporciona la clave publishable (es pública) al build y levanta los servicios:

   ```powershell
   $env:VITE_CLERK_PUBLISHABLE_KEY = 'pk_test_...'
   docker compose -f deploy/docker-compose.yml up --build
   ```

3. Abre `http://localhost:8080`. Nginx sirve la SPA y reenvía `/api/` al backend por la red interna
   de Compose. Solo se publica el puerto web del frontend; no hay volúmenes de datos.

Configura `CLERK_AUTHORIZED_PARTIES` con el origen público de la página y `CORS_ORIGINS` con los
orígenes que realmente deban llamar al backend. En un despliegue público, termina TLS delante del
proxy y limita los puertos expuestos. No uses claves de desarrollo en producción.