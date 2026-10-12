const apiBaseUrl = import.meta.env.VITE_API_BASE_URL ?? ''
const errorMessages = {
  401: 'Tu sesión no es válida. Inicia sesión de nuevo.',
  422: 'Revisa la hipótesis, el año y el tono.',
  502: 'No se pudo generar una respuesta. Inténtalo de nuevo.',
  504: 'La generación tardó demasiado. Inténtalo de nuevo.'
}

export async function processScenario(request, token) {
  if (!token?.trim()) {
    throw new Error('Inicia sesión para generar un escenario.')
  }

  let response
  try {
    response = await fetch(`${apiBaseUrl}/api/procesar`, {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(request)
    })
  } catch {
    throw new Error('No se pudo conectar con el servicio. Inténtalo de nuevo.')
  }

  if (!response.ok) {
    throw new Error(
      errorMessages[response.status]
      ?? 'No se pudo generar el escenario. Inténtalo de nuevo.'
    )
  }

  let result
  try {
    result = await response.json()
  } catch {
    throw new Error('El servicio devolvió una respuesta no válida.')
  }

  if (
    typeof result?.narrative !== 'string'
    || !Array.isArray(result.consequences)
    || result.consequences.some(item => typeof item !== 'string')
  ) {
    throw new Error('El servicio devolvió una respuesta no válida.')
  }

  return {
    narrative: result.narrative,
    consequences: result.consequences
  }
}