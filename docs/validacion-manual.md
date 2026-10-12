# Validación manual de Clerk

Usa un proyecto Clerk de desarrollo y credenciales locales válidas. Estas verificaciones son
manuales; los tests rutinarios sustituyen el verificador Clerk y OpenRouter.

- [ ] Configurar `VITE_CLERK_PUBLISHABLE_KEY` en `frontend/.env` y `CLERK_SECRET_KEY`, `CLERK_ISSUER` y `CLERK_AUTHORIZED_PARTIES` en `backend/.env`.
- [ ] Iniciar backend y frontend siguiendo el quickstart.
- [ ] Confirmar que el formulario de acceso Clerk aparece dentro de la pantalla, sin modal ni cambio de ruta.
- [ ] Iniciar sesión y confirmar que aparece el formulario de hipótesis y la acción «Cerrar sesión».
- [ ] Enviar una hipótesis válida y verificar que el backend recibe `Authorization: Bearer` y devuelve solo `narrative` y `consequences`.
- [ ] Cerrar sesión desde la pantalla; confirmar que vuelve el estado de acceso y desaparece el resultado.
- [ ] Enviar directamente `POST /api/procesar` sin token; verificar HTTP 401 y que no se invoca OpenRouter.
- [ ] No registrar aquí claves, tokens ni datos de hipótesis reales.