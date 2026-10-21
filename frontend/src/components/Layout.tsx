import { ReactNode } from 'react'
import { Link, useLocation, NavLink } from 'react-router-dom'
import { TABS, TabConfig } from '../types'

interface LayoutProps {
  children: ReactNode
}

export function Layout({ children }: LayoutProps) {
  const location = useLocation()

  return (
    <div className="layout">
      <header className="header">
        <div className="container header-content">
          <Link to="/" className="logo" aria-label="Nexus Studio Home">
            <span className="logo-icon">🔬</span>
            <span className="logo-text">Nexus Studio</span>
          </Link>
          <nav className="main-nav" aria-label="Main navigation">
            <ul className="nav-tabs">
              {TABS.map((tab: TabConfig) => (
                <li key={tab.id}>
                  <NavLink
                    to={`/${tab.id}`}
                    className={({ isActive }) =>
                      `nav-tab ${isActive ? 'active' : ''}`
                    }
                    aria-current={location.pathname === `/${tab.id}` ? 'page' : undefined}
                  >
                    <span className="tab-icon" aria-hidden="true">{tab.icon}</span>
                    <span className="tab-label">{tab.label}</span>
                  </NavLink>
                </li>
              ))}
            </ul>
          </nav>
        </div>
      </header>
      <main className="main" role="main">
        <div className="container">{children}</div>
      </main>
      <footer className="footer">
        <div className="container">
          <p>
            Nexus Studio &mdash; AI/ML Developer Tools &middot; Alan Vo &middot; alanvo@gmail.com
          </p>
        </div>
      </footer>
    </div>
  )
}