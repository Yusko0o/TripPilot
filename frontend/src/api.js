let csrfToken = null

async function getCsrfToken() {
  if (!csrfToken) {
    const response = await fetch('/api/auth/csrf', { credentials: 'same-origin' })
    if (!response.ok) throw new Error('Impossible d’initialiser la session sécurisée.')
    csrfToken = (await response.json()).csrfToken
  }
  return csrfToken
}

export async function api(path, options = {}) {
  const method = (options.method || 'GET').toUpperCase()
  const headers = { ...options.headers }

  if (options.body && typeof options.body !== 'string') {
    headers['Content-Type'] = 'application/json'
    options.body = JSON.stringify(options.body)
  }
  if (!['GET', 'HEAD', 'OPTIONS'].includes(method)) {
    headers['X-CSRFToken'] = await getCsrfToken()
  }

  const response = await fetch(path, {
    ...options,
    method,
    headers,
    credentials: 'same-origin',
  })
  const data = await response.json().catch(() => ({}))
  if (!response.ok) throw new Error(data.error || 'Une erreur est survenue.')
  if (path.startsWith('/api/auth/') && method !== 'GET') csrfToken = null
  return data
}

