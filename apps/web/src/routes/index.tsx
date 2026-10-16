import { createFileRoute } from '@tanstack/react-router'
import { useEffect, useState, type FormEvent } from 'react'

export const Route = createFileRoute('/')({ component: App })

type Tenant = { id: string; name: string }
type Item = { id: string; title: string; revision: number }

function App() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [tenant, setTenant] = useState<Tenant | null>(null)
  const [items, setItems] = useState<Item[]>([])
  const [title, setTitle] = useState('')
  const [status, setStatus] = useState<'loading'|'signed-out'|'ready'|'error'|'denied'|'expired'|'saving'>('loading')
  const [message, setMessage] = useState('')

  async function load() {
    setStatus('loading')
    try {
      const res = await fetch('/bff/tenants', { cache: 'no-store' })
      if (res.status === 401) { setStatus('signed-out'); return }
      if (!res.ok) throw Error('Could not load workspaces')
      const tenants = await res.json() as Tenant[]
      if (!tenants.length) { setStatus('denied'); return }
      const selected = tenants[0]
      setTenant(selected)
      const listing = await fetch(`/bff/items?tenant=${encodeURIComponent(selected.id)}`, { cache: 'no-store' })
      if (listing.status === 401) { setStatus('expired'); return }
      if (listing.status === 403) { setStatus('denied'); return }
      if (!listing.ok) throw Error('Could not load items')
      setItems(await listing.json() as Item[])
      setStatus('ready')
    } catch { setStatus('error'); setMessage('Service unavailable. Please retry.') }
  }

  useEffect(() => { void load() }, [])

  async function login(event: FormEvent) {
    event.preventDefault()
    setStatus('loading')
    try {
      const response = await fetch('/bff/session', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({email,password}) })
      if (!response.ok) { setMessage('Invalid credentials'); setStatus('signed-out'); return }
      setPassword('')
      await load()
    } catch { setMessage('Sign in unavailable'); setStatus('signed-out') }
  }

  async function add(event: FormEvent) {
    event.preventDefault()
    if (!tenant || !title.trim()) return
    setStatus('saving')
    try {
      const response = await fetch(`/bff/items?tenant=${encodeURIComponent(tenant.id)}`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({title}) })
      if (response.status === 401) { setStatus('expired'); return }
      if (response.status === 403) { setStatus('denied'); return }
      if (!response.ok) { setMessage('Could not create item'); setStatus('ready'); return }
      setTitle('')
      await load()
    } catch { setMessage('Service unavailable'); setStatus('error') }
  }

  async function logout() { await fetch('/bff/session', { method: 'DELETE' }); setTenant(null); setItems([]); setStatus('signed-out') }

  return <main id="main" className="shell">
    <header className="header"><strong>Aurafinity</strong><span>Application starter</span></header>
    <h1>Workspace items</h1>
    {status === 'loading' && <p role="status">Loading…</p>}
    {status === 'signed-out' && <form onSubmit={login} className="panel">
      <h2>Sign in</h2><label>Email<input required type="email" autoComplete="username" value={email} onChange={e=>setEmail(e.target.value)}/></label>
      <label>Password<input required type="password" autoComplete="current-password" value={password} onChange={e=>setPassword(e.target.value)}/></label>
      <button type="submit">Sign in</button>{message && <p role="alert">{message}</p>}
    </form>}
    {(status === 'ready' || status === 'saving') && tenant && <section className="panel" aria-label="Workspace">
      <div className="heading"><h2>{tenant.name}</h2><button className="secondary" onClick={logout}>Sign out</button></div>
      <form onSubmit={add}><label htmlFor="item-title">New item</label><div className="formrow">
        <input id="item-title" value={title} maxLength={120} required onChange={e=>setTitle(e.target.value)} placeholder="Item title"/>
        <button disabled={status === 'saving'} type="submit">Add item</button>
      </div></form>
      {items.length === 0 ? <p>No items yet. Add the first one.</p> : <ul>{items.map(item=><li key={item.id}>{item.title}</li>)}</ul>}
      {message && <p role="alert">{message}</p>}
    </section>}
    {(status === 'error' || status === 'expired' || status === 'denied') && <section className="panel" role="alert">
      <p>{status === 'denied' ? 'No workspace access.' : status === 'expired' ? 'Your session expired.' : message}</p>
      <button onClick={() => void load()}>Retry</button>
      {status === 'expired' && <button onClick={logout}>Sign in again</button>}
    </section>}
  </main>
}
