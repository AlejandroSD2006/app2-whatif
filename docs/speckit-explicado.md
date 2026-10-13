# ¿Qué es Spec Kit? (explicado sin tecnicismos)

Este documento explica, de forma sencilla, qué es Spec Kit (también llamado "speckit"), para qué sirve y cómo se ha usado en este proyecto. No hace falta saber nada de IA ni de programación avanzada para entenderlo; es la explicación "para principiantes" que no cabía en el README.

## La idea en una frase

Spec Kit obliga a escribir primero, en lenguaje normal, **qué** tiene que hacer el programa y **por qué**, antes de escribir ni una línea de código. Solo cuando esos documentos están claros y aprobados, se pasa a decidir **cómo** se va a construir y, por último, a programarlo.

A este orden de trabajo se le llama **desarrollo guiado por especificaciones** (en inglés, *Spec-Driven Development* o SDD). Spec Kit es simplemente la herramienta que ayuda a seguir ese orden paso a paso, usando una IA (en este proyecto, GitHub Copilot) como ayudante para escribir los documentos y, después, el código.

## Una analogía

Es parecido a hacer un trabajo de clase bien organizado:

1. Primero decides **qué** vas a contar y **para quién** (como una especificación).
2. Luego haces un **guion o plan** de cómo lo vas a desarrollar.
3. Después haces una **lista de tareas** concretas, en orden.
4. Y solo al final te sientas a **escribir** el trabajo, siguiendo esa lista.

Si cambias de orden (por ejemplo, empiezas a escribir sin saber bien qué quieres contar), es fácil que el trabajo salga desordenado o que tengas que rehacer partes. Spec Kit impone ese orden también para programar.

## Las piezas que vas a ver en la carpeta del proyecto

| Carpeta o archivo | Para qué sirve |
|---|---|
| `.specify/` | Es la "caja de herramientas" interna de Spec Kit: plantillas, configuración y scripts. No se edita a mano normalmente. |
| `.specify/memory/constitution.md` | Las reglas fijas del proyecto: lo que no se puede romper en ningún caso (por ejemplo, "no se guarda ningún dato"). |
| `.github/skills/speckit-*` | Las "skills" (comandos) que puedes pedirle a la IA para que siga cada paso del proceso. Cada una corresponde a una fase distinta. |
| `specs/<nombre-de-la-funcionalidad>/` | Aquí se van guardando los documentos que se generan para cada funcionalidad concreta (en este proyecto, `specs/001-historia-alternativa/`). |

## Los pasos, en orden, explicados uno a uno

Cada paso es un comando (una "skill") que le escribes a la IA, como si fuera una instrucción de un menú. La IA lee el documento anterior, hace su trabajo y genera (o actualiza) un documento nuevo. Tú revisas ese documento antes de pasar al siguiente paso.

### Paso 0. Instalar Spec Kit

Se instala una sola vez por proyecto con un comando de terminal, por ejemplo:

```bash
specify init nombre-del-proyecto --integration copilot
```

Esto crea las carpetas `.specify/` y `.github/skills/` y deja listos los comandos que se explican a continuación. `--integration copilot` indica que se va a usar GitHub Copilot como IA; también existen integraciones para otras herramientas.

### Paso 1. `/speckit-constitution` — las reglas del proyecto

Se le pide a la IA que escriba la **constitución**: las normas que no se pueden romper durante todo el proyecto. Por ejemplo: "este proyecto no guarda datos en ninguna base de datos", "todo el texto de la interfaz debe estar en español", "el backend tiene que ser con tal tecnología". Es como las reglas del juego, antes de empezar a jugar.

En este proyecto, esa constitución está en [`.specify/memory/constitution.md`](../.specify/memory/constitution.md).

### Paso 2. `/speckit-specify` — qué se quiere construir

Le describes a la IA, en una frase, qué quieres construir (por ejemplo: "una pantalla para proponer una hipótesis histórica y recibir una historia alternativa generada por IA"). La IA convierte esa idea en un documento `spec.md` con:

- Historias de usuario (quién hace qué y por qué).
- Requisitos: lo que el sistema **debe** hacer, sin decir todavía con qué tecnología.
- Criterios de éxito: cómo se sabrá que algo funciona como se esperaba.

Importante: en este paso **todavía no se habla de código ni de herramientas concretas**. Solo de lo que el sistema tiene que hacer.

### Paso 3. `/speckit-clarify` — resolver dudas antes de seguir

La IA relee la especificación y detecta huecos o ambigüedades (por ejemplo: "¿cuántas consecuencias debe tener como mínimo la respuesta?"). Te hace preguntas concretas, tú respondes, y el documento `spec.md` se actualiza con esas decisiones, dejando constancia de cuándo y por qué se tomaron. Así se evita que la IA se invente una respuesta sin que nadie la haya acordado.

En este proyecto, estas aclaraciones quedaron registradas dentro de `specs/001-historia-alternativa/spec.md`, en el apartado "Clarifications".

### Paso 4. `/speckit-plan` — cómo se va a construir

Con la especificación ya aprobada, ahora sí se decide la parte técnica: lenguajes, librerías, arquitectura, cómo se despliega, etc. Se genera un documento `plan.md`, y normalmente también documentos de apoyo como:

- `research.md`: comparación de opciones técnicas y por qué se elige una.
- `data-model.md`: qué datos maneja el sistema.
- `contracts/`: cómo es exactamente la comunicación entre frontend y backend.
- `quickstart.md`: los comandos para poner el proyecto en marcha.

### Paso 5. `/speckit-tasks` — convertir el plan en tareas pequeñas

El plan se convierte en una lista de tareas muy concretas (`tasks.md`), cada una indicando qué archivo hay que crear o modificar y de qué parte del proyecto depende. Esto permite programar poco a poco, en pasos pequeños y comprobables, en vez de intentarlo todo de una vez.

### Paso 6. `/speckit-analyze` — revisar que todo cuadra

Antes de ponerse a programar, se revisa que la especificación, el plan y las tareas no se contradigan entre sí y que no falte nada importante. Es una especie de repaso final antes del examen.

### (Opcional) `/speckit-checklist`

Genera listas de comprobación de calidad sobre la propia especificación (por ejemplo, para revisar que no falten casos límite). No es obligatorio usarlo, pero ayuda a pulir el documento antes de implementar.

### Paso 7. `/speckit-implement` — ahora sí, programar

Con todo lo anterior aprobado, la IA empieza a escribir el código real, tarea por tarea, siguiendo `tasks.md` en el orden indicado, y marcando cada tarea como hecha (`[X]`) a medida que se completa.

### (Opcionales, no usados en este proyecto)

- `/speckit-taskstoissues`: convierte las tareas de `tasks.md` en issues de un repositorio de GitHub, para gestionarlas como un tablero.
- `/speckit-converge`: ayuda a unificar o cerrar variantes cuando se han probado varios caminos distintos para la misma funcionalidad.

## Por qué se para entre cada paso

Lo más importante de todo el proceso no es la lista de comandos, sino que **entre cada paso hay que parar y revisar**. La IA no decide sola todo el proyecto de principio a fin: en cada fase, una persona (en este caso, el equipo de desarrollo) lee el documento generado, lo corrige si hace falta, y solo entonces autoriza pasar a la siguiente fase. Así la IA ayuda a escribir más rápido, pero las decisiones importantes las sigue tomando el equipo.

## Cómo se usó exactamente en este proyecto

Aquí tienes el resumen real de lo que pasó en `app2-whatif`, fase por fase (el detalle completo, con la instrucción exacta que se usó en cada fase, está en [uso-ia.md](uso-ia.md)):

| Fase | Comando usado | Qué se generó |
|---|---|---|
| 1 | `specify init app2-whatif --integration copilot` | La estructura base del proyecto y los comandos para Copilot. |
| 2 | `/speckit-constitution` | Las reglas fijas del proyecto: alcance mínimo, stack obligatorio, seguridad, pruebas simuladas, idioma. |
| 3 | `/speckit-specify` y `/speckit-clarify` | La especificación (`spec.md`) con historias de usuario y requisitos, y tres aclaraciones resueltas con el equipo. |
| 4 | `/speckit-plan` | El plan técnico (`plan.md`): FastAPI + Clerk + OpenRouter en el backend, Vue 3 + Vite + Tailwind en el frontend, y cómo desplegarlo. |
| 5 | `/speckit-tasks` y `/speckit-analyze` | La lista de tareas (`tasks.md`, 33 tareas) y una revisión de que todo encajaba con la especificación. |
| Implementación | `/speckit-implement` | El código del backend y del frontend, siguiendo las tareas aprobadas, con pruebas que sustituyen a Clerk y a OpenRouter. |

## Dónde mirar si quieres ver los documentos reales

- [`specs/001-historia-alternativa/spec.md`](../specs/001-historia-alternativa/spec.md) — la especificación completa.
- [`specs/001-historia-alternativa/plan.md`](../specs/001-historia-alternativa/plan.md) — el plan técnico.
- [`specs/001-historia-alternativa/tasks.md`](../specs/001-historia-alternativa/tasks.md) — la lista de tareas.
- [`.specify/memory/constitution.md`](../.specify/memory/constitution.md) — las reglas fijas del proyecto.
- [`uso-ia.md`](uso-ia.md) — qué se le pidió exactamente a la IA en cada fase y qué se decidió.

## Glosario rápido

| Término | Significado sencillo |
|---|---|
| SDD (Spec-Driven Development) | La forma de trabajar: primero especificar, luego planificar, luego programar. |
| Feature (funcionalidad) | Cada bloque de trabajo que se documenta por separado dentro de `specs/`; en este proyecto solo hay una: `001-historia-alternativa`. |
| Skill / comando | Cada uno de los pasos de Spec Kit (`/speckit-specify`, `/speckit-plan`, etc.) que le puedes pedir a la IA. |
| Constitución | El documento con las reglas que no se pueden romper en todo el proyecto. |
| Spec (especificación) | El documento que dice qué debe hacer el sistema, sin hablar todavía de tecnología. |
| Plan | El documento que decide la tecnología y la arquitectura concretas. |
| Tasks (tareas) | La lista de pasos pequeños y concretos con los que se programa el sistema. |
| Clarify (aclarar) | El paso en el que se resuelven dudas de la especificación antes de seguir. |
| Analyze (analizar) | El paso en el que se revisa que todo encaje antes de programar. |
| Implement (implementar) | El paso en el que la IA escribe el código real siguiendo las tareas aprobadas. |
