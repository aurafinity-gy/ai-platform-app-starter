import { createFileRoute } from '@tanstack/react-router'
import { setCookie, deleteCookie } from '@tanstack/react-start/server'

export const Route = createFileRoute('/bff/session')({
  server: {
    handlers: {
      POST: async ({ request }) => {
        const response = await fetch(new URL('/auth/login', process.env.API_INTERNAL_URL ?? 'http://api:8000'), {
          method: 'POST', headers: { 'Content-Type': 'application/json' }, body: await request.text(),
        })
        if (!response.ok) return Response.json({ detail: 'invalid_credentials' }, { status: 401 })
        const json = await response.json() as { access_token: string }
        setCookie('starter_session', json.access_token, { httpOnly: true, secure: process.env.NODE_ENV === 'production', sameSite: 'lax', path: '/', maxAge: 1800 })
        return Response.json({ ok: true })
      },
      DELETE: async () => { deleteCookie('starter_session', { path: '/' }); return Response.json({ ok: true }) },
    },
  },
})
