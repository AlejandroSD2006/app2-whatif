# Comprobación manual del flujo

Ejecutar con Clerk configurado y un backend de prueba que permita controlar la respuesta del
proveedor. No usar datos personales ni guardar capturas con tokens.

- [ ] Enviar una hipótesis válida; comprobar que el botón queda desactivado y el panel muestra el estado de espera.
- [ ] Intentar enviar otra vez mientras espera; comprobar que no inicia una segunda petición.
- [ ] Completar la primera petición y comprobar que aparece una narración y entre 3 y 5 consecuencias.
- [ ] Iniciar una segunda petición válida; comprobar que el resultado anterior desaparece durante la espera y se sustituye al terminar.
- [ ] Probar pregunta vacía, 281 caracteres y año fuera de 0–3000; confirmar mensajes en español y que no se envía una petición.
- [ ] Simular respuestas 401, 422, 502, 504 y fallo de red; comprobar mensajes seguros, sin cuerpo del proveedor, token ni texto enviado.