<!--
Informe de impacto de sincronización
Versión: sin constitución previa → 1.0.0 (constitución inicial)
Principios modificados: ninguno; se establecen cinco principios iniciales.
Secciones añadidas: Additional Constraints; Development Workflow and Human Review.
Secciones eliminadas: ninguna con contenido previo.
Pendientes: la fecha de ratificación requiere aceptación humana; retirar este informe antes del commit.
-->

# App2 WhatIf Constitution

## Core Principles

### I. Alcance mínimo e inmutable
La aplicación ofrece una sola función: generar y mostrar un escenario de historia alternativa
desde una única pantalla y un único formulario. Cada envío válido realiza exactamente una llamada
a una sola API de IA. No se incorporan bases de datos, persistencia funcional, historial, CRUD,
vistas adicionales, chat con memoria, servicios extra ni gestión propia de usuarios. El alcance del
enunciado prevalece sobre cualquier sugerencia que amplíe estas capacidades.

### II. Contratos explícitos y stack obligatorio
El backend usa Python, FastAPI y validación Pydantic; el frontend es una SPA de Vue 3, Vite y
Tailwind CSS, sin vue-router. OpenRouter es el único proveedor de IA y el modelo se configura por
variable de entorno. La entrada conserva la necesidad de App 1: pregunta de hasta 280 caracteres,
año entero entre 0 y 3000 y nivel `realista`, `ilusionante` o `descerebrado`. La respuesta contiene
la narración y sus consecuencias; la especificación debe resolver si además refleja la pregunta
original antes de fijar el contrato HTTP.

### III. Pruebas rutinarias sin servicios reales
Las pruebas automatizadas usan pytest y sustituyen tanto el cliente de IA como el verificador de
Clerk. Deben demostrar una sola llamada para una entrada válida, ninguna llamada para entradas
inválidas o no autenticadas, límites, fallos del proveedor, timeout y respuestas vacías o inválidas.
La suite rutinaria nunca contacta con OpenRouter ni Clerk reales. Cualquier prueba real de
integración es manual, separada y claramente identificada.

### IV. Seguridad antes del procesamiento
FastAPI verifica realmente el token de Clerk mediante un mecanismo oficial antes de llamar a la IA;
no basta con decodificarlo. La clave de OpenRouter y cualquier clave secreta de Clerk permanecen en
el backend. El navegador envía el token como Bearer y solo recibe la clave publishable de Clerk.
Los registros y errores no exponen entradas, resultados, tokens, secretos, trazas ni respuestas
completas del proveedor.

### V. Flujo simple, accesible y revisable
La interfaz y la documentación para usuarios están en español; los identificadores de código,
en inglés. La SPA presenta entrada, espera, resultado y error en la misma pantalla, bloquea envíos
duplicados, descarta resultados anteriores y representa la salida como texto, nunca como HTML.
La validación frontend ayuda al usuario y no sustituye la validación del backend.

## Additional Constraints

- El backend expone un endpoint de procesamiento y puede exponer uno de salud. Los errores siguen
	un JSON estable y documentan 200, 401, 422, 502 y 504. La respuesta nunca reenvía el objeto
	completo de OpenRouter. Los límites y el timeout se documentan y prueban.
- No se guardan entradas ni resultados en archivos, cachés, bases de datos, localStorage,
	sessionStorage o IndexedDB. Solo se permite su presencia transitoria en memoria durante la
	petición y visualización. La sesión técnica de Clerk se limita a autenticar.
- CORS permite únicamente los orígenes configurados y la cabecera `Authorization`. CORS no
	sustituye a la verificación del token.
- Vercel usa proyectos separados para frontend y backend. Docker/EC2 puede usar un proxy de mismo
	origen para `/api`; no añade servicios de datos ni volúmenes funcionales. Las claves se inyectan
	al ejecutar y nunca se incorporan a imágenes ni argumentos de build. Solo la clave publishable
	de Clerk puede estar en la configuración pública del frontend.
- `.env.example` contiene nombres y valores ficticios. `.gitignore` y `.dockerignore` excluyen
	secretos, entornos virtuales y dependencias locales.

## Development Workflow and Human Review

- La constitución, la especificación y sus aclaraciones deben preceder al plan, las tareas y el
	código. Se detiene el trabajo al terminar cada fase para revisión y autorización humana.
- Se implementa en lotes pequeños, backend y pruebas antes que frontend e integración. Cada lote
	ejecuta su prueba enfocada; se registran resultados reales y decisiones en la documentación.
- Cada fase aprobada mantiene un cambio identificable en Git. Antes de aceptar un cambio se revisa
	su coherencia con la necesidad, esta constitución y el enunciado; cualquier conflicto se resuelve
	a favor del enunciado.
- No se declaran ejecuciones, despliegues, aprobaciones, versiones o resultados que no se hayan
	comprobado. Los despliegues reales de Vercel y AWS corresponden al usuario.

## Governance

Esta constitución gobierna las decisiones del proyecto y no puede ampliar el alcance obligatorio
del enunciado. Una propuesta que contradiga una regla debe rechazarse o aclararse antes de
implementarla. Toda modificación requiere revisión humana, justificación y actualización de la
versión: MAJOR para cambios incompatibles, MINOR para principios o requisitos nuevos y PATCH para
aclaraciones sin cambio de obligación. La revisión de especificación, plan, tareas, código y pruebas
debe comprobar el cumplimiento de estos principios. La fecha de ratificación queda pendiente hasta
que el usuario revise y acepte esta constitución.

**Version**: 1.0.0 | **Ratified**: TODO(RATIFICATION_DATE): pendiente de aceptación humana | **Last Amended**: 2026-10-12
