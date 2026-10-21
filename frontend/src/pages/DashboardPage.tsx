import { SystemStatus } from '../components'
import { TABS } from '../types'

export default function DashboardPage() {
  return (
    <div className="page">
      <header className="page-header">
        <h1>Nexus Studio Dashboard</h1>
        <p>AI/ML Developer Tools for Bedrock, Plugins, and Authentication</p>
      </header>

      <SystemStatus />

      <section className="dashboard-grid">
        {TABS.map((tab) => (
          <article key={tab.id} className="dashboard-card">
            <div className="card-icon" aria-hidden="true">{tab.icon}</div>
            <h2>{tab.label}</h2>
            <p>
              {tab.id === 'bedrock' && 'Resolve correct inference profile IDs for AU/EU/APAC regions'}
              {tab.id === 'iam' && 'Generate IAM policies with region-aware geographic prefixes'}
              {tab.id === 'plugins' && 'Validate and fix hooks.json and .mcp.json configuration files'}
              {tab.id === 'bootstrap' && 'Acquire tokens with automatic silent refresh before bootstrap calls'}
            </p>
            <a href={`/${tab.id}`} className="btn btn-primary">
              Open {tab.label}
            </a>
          </article>
        ))}
      </section>

      <section className="card info-section">
        <h2>About Nexus Studio</h2>
        <p>
          Nexus Studio provides AI/ML developer tools for working with AWS Bedrock, Claude plugins,
          and Microsoft Entra ID authentication. The core domain engine implements deterministic
          offline algorithms for:
        </p>
        <ul>
          <li><strong>Bedrock Model Resolution:</strong> Maps regions to correct inference profile prefixes (us/eu/au/apac)</li>
          <li><strong>IAM Policy Generation:</strong> Creates policies with region-aware resource ARNs</li>
          <li><strong>Plugin Validation:</strong> Detects and fixes common schema/syntax errors in plugin configs</li>
          <li><strong>Bootstrap Token Management:</strong> Implements MSAL acquireTokenSilent flow to prevent 401 errors</li>
        </ul>
        <p>
          All core algorithms work offline without any LLM API key. LLM-powered explanations
          are opt-in and clearly labeled as advisory.
        </p>
      </section>
    </div>
  )
}