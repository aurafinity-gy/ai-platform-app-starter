import { getCookie } from '@tanstack/react-start/server'

const base = process.env.API_INTERNAL_URL ?? 'http://api:8000'

export async function upstream(request: Request, path: string, method = 'GET'): Promise<Response> {
  const token = getCookie('starter_session')
  if (!token) return Response.json({ detail: 'unauthenticated' }, { status: 401 })
  return fetch(new URL(path, base), {
    method,
    headers: { Authorization: `Bearer ${token}`, ...(method === 'POST' ? { 'Content-Type': 'application/json' } : {}) },
    body: method === 'POST' ? await request.text() : undefined,
    cache: 'no-store',
  })
}

export async function relay(response: Response): Promise<Response> {
  return new Response(response.body, { status: response.status, headers: { 'Content-Type': 'application/json', 'Cache-Control': 'no-store' } })
}
