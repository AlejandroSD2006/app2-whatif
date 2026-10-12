# Feature Specification: Generación de historia alternativa

**Feature Branch**: `001-historia-alternativa` (identificador documental; no se crea una rama Git)

**Created**: 2026-10-12

**Status**: Draft

**Input**: User description: "Una aplicación de una pantalla para proponer una hipótesis histórica con año y estilo, autenticarse y recibir una narración y consecuencias generadas por IA, equivalente en necesidad a App 1."

## Clarifications

### Session 2026-10-12

- Q: ¿Quieres que una respuesta correcta incluya también `question` con la pregunta normalizada, o solo `narrative` y `consequences`? → A: Solo `narrative` y `consequences`; no se devuelve `question`.
- Q: ¿Cuántas consecuencias debe incluir una respuesta válida de la IA? → A: Entre 3 y 5 consecuencias, ambos límites incluidos.
- Q: ¿Cómo prefieres que aparezca el acceso de Clerk en la única pantalla? → A: Integrado en la pantalla, no en un modal ni en otra ruta.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Explorar una historia alternativa (Priority: P1)

Una persona plantea una hipótesis histórica, elige el año de referencia y el tono, y recibe una
narración con consecuencias posibles.

**Why this priority**: Es la única función útil de la aplicación y resuelve la necesidad de App 1.

**Independent Test**: Enviar una entrada válida con identidad autorizada y comprobar el resultado
en la misma pantalla y una sola solicitud al proveedor.

**Acceptance Scenarios**:

1. **Given** acceso autorizado y datos válidos, **When** la persona envía el formulario,
   **Then** recibe una narración y una lista de consecuencias en la misma pantalla.
2. **Given** una pregunta de 280 caracteres y un año entre 0 y 3000 inclusive, **When** se envía,
   **Then** los límites se aceptan.
3. **Given** una pregunta vacía o de 281 caracteres, un año fuera del intervalo o un estilo
   desconocido, **When** se envía, **Then** la entrada se rechaza sin consultar a la IA.

---

### User Story 2 - Acceder con Clerk (Priority: P1)

Una persona se autentica con Clerk dentro de la única pantalla para poder solicitar el escenario.

**Why this priority**: El procesamiento debe estar protegido y no puede depender solo de ocultar
el botón de envío.

**Independent Test**: Comprobar que una petición sin token, con token inválido o caducado se
rechaza antes de consultar a la IA, y que una petición autorizada puede completar el flujo.

**Acceptance Scenarios**:

1. **Given** una persona sin sesión válida, **When** intenta procesar una hipótesis,
   **Then** recibe un rechazo de acceso y no se consulta a la IA.
2. **Given** una persona autenticada con Clerk, **When** envía datos válidos,
   **Then** la petición se procesa sin crear una cuenta o perfil propio de la aplicación.
3. **Given** que la sesión de Clerk no es válida, **When** se envía una petición directa,
   **Then** el backend la rechaza aunque la interfaz permita intentar el envío.
4. **Given** que una persona aún no está autenticada, **When** abre la pantalla,
   **Then** encuentra el acceso integrado en esa misma pantalla, sin abrir un modal ni cambiar de ruta.
5. **Given** que una persona tiene una sesión activa, **When** elige cerrar sesión en la misma
  pantalla, **Then** Clerk cierra la sesión y la interfaz vuelve al estado de acceso; los envíos
  posteriores sin autenticación se rechazan antes de consultar a la IA.

---

### User Story 3 - Entender y recuperarse de errores (Priority: P2)

La persona recibe un mensaje comprensible si sus datos no son válidos, si falla la IA o si la
respuesta generada no se puede utilizar.

**Why this priority**: Los errores externos y de entrada deben ser distinguibles sin exponer
detalles internos ni perder el control del único flujo.

**Independent Test**: Simular entrada inválida, fallo, timeout y respuesta vacía o mal formada del
proveedor; verificar el estado visible y el código de error acordado.

**Acceptance Scenarios**:

1. **Given** una solicitud pendiente, **When** la persona intenta enviarla de nuevo,
   **Then** el segundo envío se bloquea y no se acumulan solicitudes.
2. **Given** un fallo del proveedor, una respuesta vacía o una respuesta mal formada,
   **When** termina la petición, **Then** se muestra un error seguro y comprensible.
3. **Given** que se muestra un resultado y se completa otra solicitud,
   **When** llega el nuevo resultado, **Then** se sustituye el anterior y no se conserva historial.

### Edge Cases

- Una pregunta formada solo por espacios se considera vacía.
- El máximo de pregunta se evalúa tras quitar espacios exteriores; 280 caracteres se aceptan y
  281 se rechazan.
- Los años 0 y 3000 se aceptan; los años -1, 3001 y los no enteros se rechazan.
- Un nivel distinto de `realista`, `ilusionante` o `descerebrado` se rechaza.
- Un token ausente, inválido o caducado se rechaza antes de cualquier llamada a la IA.
- Un timeout del proveedor se informa como timeout; el proveedor inaccesible o una salida vacía o
  no utilizable se informa como error controlado, sin datos internos.
- La interfaz no inicia envíos duplicados y solo mantiene el resultado actual durante la sesión
  visible; no lo conserva al cerrar o recargar.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: La persona usuaria MUST poder introducir una pregunta no vacía de hasta 280
  caracteres, ignorando espacios exteriores al validarla.
- **FR-002**: La persona usuaria MUST poder elegir un año entero de referencia entre 0 y 3000,
  ambos incluidos.
- **FR-003**: La persona usuaria MUST poder elegir exactamente uno de estos estilos: `realista`,
  `ilusionante` o `descerebrado`.
- **FR-004**: El sistema MUST permitir procesar una hipótesis únicamente con una identidad
  autenticada y autorizada por Clerk.
- **FR-005**: Cada envío válido MUST producir una sola solicitud al proveedor de IA. Los datos
  inválidos, las solicitudes no autorizadas y los envíos duplicados MUST producir cero solicitudes
  adicionales al proveedor.
- **FR-006**: La respuesta de éxito MUST incluir una narración no vacía y una lista de
  consecuencias en español. No MUST incluir la pregunta original.
- **FR-007**: La respuesta MUST contener entre 3 y 5 consecuencias, ambos límites incluidos, y cada
  consecuencia MUST ser texto no vacío. Una lista vacía o fuera del rango MUST rechazarse como
  respuesta no utilizable del modelo.
- **FR-008**: La entrada y el resultado MUST mostrarse en la misma pantalla, en estados distinguibles de entrada, espera, resultado y error. La salida generada MUST mostrarse como texto y nunca ejecutarse como HTML.
- **FR-009**: Mientras una petición esté pendiente, el sistema MUST impedir que un segundo envío inicie otra solicitud. Un resultado nuevo MUST sustituir al anterior.
- **FR-010**: La interfaz MUST mostrar el acceso de Clerk integrado en la misma pantalla, sin
  modal ni navegación a rutas de acceso, registro, perfil o administración.
- **FR-011**: La petición no autorizada MUST devolver HTTP 401 sin consultar a la IA. La entrada inválida MUST devolver HTTP 422. Los errores controlados MUST usar un JSON estable con código y mensaje en español.
- **FR-012**: El sistema MUST distinguir éxito HTTP 200, rechazo de autenticación 401, validación 422, fallo del proveedor o salida no utilizable 502 y timeout 504.
- **FR-013**: El sistema MUST poder utilizarse de nuevo con otra entrada, sin historial ni acumulación de resultados.
- **FR-014**: El sistema MUST evitar conservar entradas y resultados en almacenamiento persistente o registros técnicos. Su presencia transitoria durante el procesamiento y visualización está permitida.
- **FR-015**: Los mensajes visibles de interfaz y error MUST estar en español y no revelar trazas, secretos, tokens, texto enviado, respuesta completa del proveedor ni detalles internos.
- **FR-016**: La persona usuaria MUST poder cerrar su sesión de Clerk desde la misma pantalla. Tras
  cerrar la sesión, cualquier solicitud de procesamiento sin volver a autenticarse MUST recibir
  HTTP 401 antes de consultar a la IA.

### Processing Contract

La operación de procesamiento acepta un objeto JSON con `question` (texto), `year` (entero) y
`unrealismLevel` (uno de los tres valores admitidos). La respuesta de éxito tiene `narrative`
(texto) y `consequences` (entre 3 y 5 textos no vacíos); no incluye la pregunta de entrada. La
forma de acceso HTTP al procesamiento es `POST /api/procesar`.

Los errores usan la forma `{"error":{"code":"CODIGO","message":"Mensaje en español"}}`.
El contrato documenta 401 para identidad ausente o inválida, 422 para entrada inválida, 502 para
fallos o salidas no utilizables del proveedor y 504 para timeout. La respuesta nunca contiene la
respuesta completa del proveedor.

### Key Entities *(include if feature involves data)*

- **Hipótesis**: texto introducido por la persona, año de referencia y estilo elegido; solo existe
  transitoriamente mientras se procesa.
- **Escenario alternativo**: narración y lista de consecuencias generadas; solo existe
  transitoriamente mientras se muestra.
- **Sesión autenticada**: identidad técnica validada por Clerk; no se copia a un sistema propio ni
  se amplía con perfiles o roles de aplicación.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: En todos los casos válidos de prueba, el resultado contiene una narración no vacía,
  una lista de consecuencias de textos y exactamente una solicitud al proveedor.
- **SC-002**: En todos los casos inválidos de límites y valores, la petición se rechaza con el
  resultado documentado y el contador de llamadas al proveedor permanece en cero.
- **SC-003**: En todos los casos de token ausente, inválido o caducado, el sistema devuelve 401
  antes de invocar al proveedor.
- **SC-004**: Los casos simulados de fallo, timeout y salida no utilizable producen respectivamente
  los códigos 502, 504 y 502, sin devolver detalles internos.
- **SC-005**: Una petición pendiente no puede duplicarse desde la interfaz y un resultado nuevo
  reemplaza al anterior sin dejar un historial recuperable.
- **SC-006**: La prueba real manual de Clerk demuestra iniciar sesión, cerrar sesión desde la misma
  pantalla y recibir 401 sin llamada a IA después del cierre.

## Assumptions

- La persona usuaria tiene conexión a internet y puede autenticarse mediante la aplicación Clerk
  configurada para el proyecto.
- OpenRouter es el proveedor único; el nombre concreto del modelo y los valores del timeout se
  decidirán en el plan técnico, no en esta especificación.
- Las pruebas rutinarias simulan Clerk y el proveedor de IA. Una prueba con servicios reales, si se
  añade, queda separada y es manual.
- Se emplean hipótesis ficticias; no se deben introducir datos personales ni confidenciales.
- El servicio no promete exactitud histórica absoluta; presenta escenarios hipotéticos generados.