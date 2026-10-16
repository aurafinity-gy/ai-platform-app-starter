import { createFileRoute } from '@tanstack/react-router'
import { upstream, relay } from '../server/proxy'

export const Route = createFileRoute('/bff/items')({
  server: { handlers: {
    GET: async ({ request }) => {
      const tenant = new URL(request.url).searchParams.get('tenant')
      if (!tenant || !/^[0-9a-f-]{36}$/i.test(tenant)) return Response.json({ detail: 'invalid_tenant' }, { status: 400 })
      return relay(await upstream(request, `/tenants/${tenant}/items`))
    },
    POST: async ({ request }) => {
      const tenant = new URL(request.url).searchParams.get('tenant')
      if (!tenant || !/^[0-9a-f-]{36}$/i.test(tenant)) return Response.json({ detail: 'invalid_tenant' }, { status: 400 })
      return relay(await upstream(request, `/tenants/${tenant}/items`, 'POST'))
    },
  } },
})
