# Cómo se creó la aplicación con Spec Kit

## Punto de partida

La aplicación se desarrolló a partir de una necesidad expresada por el usuario: crear una
aplicación de una sola pantalla, equivalente en utilidad a App 1, donde se pueda proponer una
hipótesis histórica con un año y un estilo, autenticarse y recibir una narración y sus consecuencias
generadas por IA. Ese enunciado se registró como entrada de la especificación de la funcionalidad.

Spec Kit ayudó a convertir esa idea en artefactos progresivos antes de implementar el producto:
primero se fijaron los principios del proyecto, después se especificó el comportamiento esperado,
se diseñó la solución técnica, se desglosó el trabajo en tareas y finalmente se implementaron y
validaron esas tareas con GitHub Copilot.

## Flujo de trabajo

1. **Inicialización.** Se utilizó GitHub Spec Kit CLI 1.1.3 para inicializar el repositorio con
   integración para GitHub Copilot y las skills de Spec Kit.
2. **Principios.** Con `speckit-constitution` se establecieron límites para el alcance, el stack, la
   seguridad, las pruebas sin servicios externos y la revisión humana.
3. **Especificación.** Con `speckit-specify` y `speckit-clarify` se transformó el enunciado del
   usuario en historias, requisitos funcionales, casos límite y criterios comprobables. Se
   resolvieron tres preguntas: la respuesta no debía repetir la pregunta original, debía incluir
   entre 3 y 5 consecuencias y el acceso de Clerk debía estar integrado en la misma pantalla.
4. **Planificación.** Con `speckit-plan` se definieron arquitectura, tecnologías, flujo de
   autenticación, contrato HTTP, estrategia de pruebas y opciones de despliegue. Las decisiones
   técnicas se apoyaron en investigación de documentación oficial y quedaron registradas como
   propuestas de implementación, separadas de los requisitos funcionales.
5. **Tareas y análisis.** `speckit-tasks` convirtió el plan en 33 tareas concretas y ordenadas por
   dependencias e historias de usuario. `speckit-analyze` se utilizó para revisar la coherencia y
   cobertura entre especificación, plan y tareas.
6. **Implementación.** Con `speckit-implement` se ejecutaron las tareas: backend FastAPI, frontend
   Vue, autenticación Clerk, integración con OpenRouter, pruebas, configuración de despliegue y
   documentación.
7. **Validación y registro.** Los resultados se anotaron en la documentación del proyecto,
   distinguiendo las pruebas automatizadas de las comprobaciones manuales que requieren servicios
   reales.

## De los requisitos al código

| Necesidad especificada | Resultado en la aplicación |
|---|---|
| Proponer pregunta, año y estilo | Formulario de una pantalla en `frontend/src/components/HypothesisForm.vue`. |
| Autenticarse y cerrar sesión sin cambiar de pantalla | Integración de Clerk en `frontend/src/components/ClerkAccess.vue` y `frontend/src/App.vue`; el backend vuelve a verificar el token. |
| Recibir narración y consecuencias | Servicio de escenario en `backend/app/services/scenario.py`, proveedor aislado en `backend/app/providers/openrouter.py` y resultado en `frontend/src/components/ScenarioResult.vue`. |
| Rechazar entrada inválida y limitar llamadas a IA | Modelos y validación en `backend/app/models.py`; endpoint y autenticación en `backend/app/main.py` y `backend/app/auth.py`. |
| Comunicar errores sin exponer detalles internos | Manejo de errores en backend y frontend, con pruebas de integración en `backend/tests/integration/`. |
| No conservar hipótesis ni resultados | Estado en memoria durante la petición y la sesión visible; no se añadió base de datos ni almacenamiento web. |

La especificación funcional se mantiene independiente del framework; los detalles técnicos aparecen
en el plan y en las tareas. Esta separación permite revisar primero qué debe hacer el producto y,
después, cómo construirlo.

## Artefactos de Spec Kit

Los documentos principales de la funcionalidad están en
[`specs/001-historia-alternativa/`](../specs/001-historia-alternativa/):

- [`spec.md`](../specs/001-historia-alternativa/spec.md): necesidades, historias de usuario,
  aclaraciones, requisitos y criterios de éxito.
- [`checklists/requirements.md`](../specs/001-historia-alternativa/checklists/requirements.md):
  revisión de calidad y preparación de la especificación.
- [`plan.md`](../specs/001-historia-alternativa/plan.md): arquitectura, decisiones técnicas y
  estrategia de verificación.
- [`research.md`](../specs/001-historia-alternativa/research.md): investigación técnica, fuentes y
  riesgos pendientes.
- [`data-model.md`](../specs/001-historia-alternativa/data-model.md) y
  [`contracts/procesar.yaml`](../specs/001-historia-alternativa/contracts/procesar.yaml): datos
  transitorios y contrato de la API.
- [`tasks.md`](../specs/001-historia-alternativa/tasks.md): tareas de implementación y su estado.
- [`quickstart.md`](../specs/001-historia-alternativa/quickstart.md): instrucciones de desarrollo y
  verificación local.

## Verificación y límites

La validación registrada en [`validacion.md`](validacion.md) indica que las 40 pruebas de backend
pasaron, que el build de producción de Vue fue correcto y que se revisaron el empaquetado y la
ausencia de persistencia y secretos en el frontend. Las pruebas rutinarias usan dobles para Clerk y
OpenRouter; no dependen de servicios externos.

La comprobación real de inicio y cierre de sesión con Clerk y el recorrido autenticado desde el
navegador quedaron pendientes, al igual que ejecutar Docker Compose y realizar un despliegue real.
El registro de asistencia de IA en [`uso-ia.md`](uso-ia.md) también deja pendiente la comprobación
humana final. Por tanto, las pruebas automatizadas aprobadas no deben interpretarse como una
validación completa del flujo real con credenciales del usuario.

## Documentación relacionada

- [`README.md`](../README.md): inicio rápido del proyecto.
- [`validacion-manual.md`](validacion-manual.md): lista para probar Clerk manualmente.
- [`despliegue.md`](despliegue.md): alternativas de despliegue.
- [`uso-ia.md`](uso-ia.md): registro de las fases y decisiones de asistencia de IA.