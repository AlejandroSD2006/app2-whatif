# Modelo de datos transitorio

La aplicación no define entidades persistentes, repositorios ni esquema de base de datos. Los
objetos siguientes existen en memoria durante la petición o mientras se presenta la pantalla; no
se serializan a almacenamiento web ni se escriben en logs.

## Hipótesis de entrada

| Campo | Tipo | Restricción |
|---|---|---|
| `question` | string | Tras `strip()`, entre 1 y 280 caracteres. |
| `year` | integer estricto | Entre 0 y 3000 inclusive; booleanos y conversiones implícitas no se aceptan. |
| `unrealismLevel` | enum/string | Exactamente `realista`, `ilusionante` o `descerebrado`. |

El modelo de entrada Pydantic será la autoridad de validación del backend. La interfaz valida antes
de enviar para ayudar a la persona, pero no sustituye esa frontera. Se ignoran espacios exteriores
al validar y se envía texto normalizado.

## Escenario alternativo

| Campo | Tipo | Restricción |
|---|---|---|
| `narrative` | string | No vacío tras quitar espacios exteriores. |
| `consequences` | array de strings | Entre 3 y 5; todos no vacíos tras quitar espacios exteriores. |

El cuerpo exitoso solo expone estos dos campos. Se descarta cualquier campo adicional del
proveedor y no se incluye la pregunta original.

## Sesión autenticada

El token Bearer solo se pasa al verificador Clerk del backend. Si se valida, la petición continúa;
no se crea un usuario, perfil, rol ni registro propio. El token no se incluye en errores ni logs y
no se persiste.

## Error controlado

Un valor de error se compone de `code` y `message` en español, dentro del objeto `error`. No incluye
request, token, excepción, stack trace ni respuesta completa del proveedor. Los estados HTTP y
códigos funcionales se definen en `contracts/procesar.yaml`.