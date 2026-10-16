import { createFileRoute } from '@tanstack/react-router'
import { upstream, relay } from '../server/proxy'

export const Route = createFileRoute('/bff/tenants')({
  server: { handlers: { GET: async ({ request }) => relay(await upstream(request, '/tenants')) } },
})
