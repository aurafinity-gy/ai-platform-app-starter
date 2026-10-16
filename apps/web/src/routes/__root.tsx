import { createRootRoute, Outlet } from '@tanstack/react-router'
import '../styles.css'

export const Route = createRootRoute({
  component: () => <><a className="skip" href="#main">Skip to main content</a><Outlet /></>,
})
