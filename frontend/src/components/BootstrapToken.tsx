import { useState } from 'react'
import { useBootstrapToken, validateBootstrapForm } from '../hooks/useApi'
import { BootstrapResponse } from '../types'

export function BootstrapToken() {
  const [bootstrapUrl, setBootstrapUrl] = useState('')
  const [clientId, setClientId] = useState('')
  const [tenantId, setTenantId] = useState('')
  const [scopes, setScopes] = useState('https://cognitiveservices.azure.com/.default')
  const [account, setAccount] = useState('')
  const [result, setResult] = useState<BootstrapResponse | null>(null)
  const [errors, setErrors] = useState<string[]>([])

  const { mutate, isPending, error } = useBootstrapToken()

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    const formErrors = validateBootstrapForm({ bootstrapUrl, clientId, tenantId, scopes, account })
    if (formErrors.length > 0) {
      setErrors(formErrors)
      return
    }
    setErrors([])
    mutate(
      { bootstrapUrl, clientId, tenantId, scopes, account },
      {
        onSuccess: (data) => setResult(data),
        onError: (err) => setErrors([err.message]),
      }
    )
  }

  const getSourceBadge = (source: string) => {
    switch (source) {
      case 'cache': return 'bg-blue-100 text-blue-800'
      case 'silent_refresh': return 'bg-green-100 text-green-800'
      case 'interactive': return 'bg-orange-100 text-orange-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  const formatExpiry = (timestamp: number) => {
    return new Date(timestamp * 1000).toLocaleString()
  }

  return (
    <section className="card" aria-labelledby="bootstrap-heading">
      <h2 id="bootstrap-heading" className="section-title">
        Bootstrap Token Manager
      </h2>
      <div className="section-description">
        <p>Acquire valid tokens for bootstrap endpoint calls. Implements the correct flow:</p>
        <ol className="inline-list">
          <li>Try <code>acquireTokenSilent()</code> first (uses refresh token)</li>
          <li>Fall back to interactive login if silent auth fails</li>
          <li>Use fresh token for bootstrap endpoint call</li>
        </ol>
        <p>This prevents the <code>401</code> error caused by sending expired Entra tokens.</p>
      </div>

      <form onSubmit={handleSubmit} className="form-grid" noValidate>
        <div className="form-group">
          <label htmlFor="bootstrap-url" className="label">Bootstrap Endpoint URL</label>
          <input
            id="bootstrap-url"
            type="url"
            value={bootstrapUrl}
            onChange={(e) => setBootstrapUrl(e.target.value)}
            className="input"
            placeholder="https://your-gateway.com/bootstrap"
            required
          />
        </div>

        <div className="form-group">
          <label htmlFor="client-id" className="label">Azure AD Client ID</label>
          <input
            id="client-id"
            type="text"
            value={clientId}
            onChange={(e) => setClientId(e.target.value)}
            className="input"
            placeholder="xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
            required
          />
        </div>

        <div className="form-group">
          <label htmlFor="tenant-id" className="label">Azure AD Tenant ID</label>
          <input
            id="tenant-id"
            type="text"
            value={tenantId}
            onChange={(e) => setTenantId(e.target.value)}
            className="input"
            placeholder="xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
            required
          />
        </div>

        <div className="form-group">
          <label htmlFor="scopes" className="label">Scopes (comma-separated)</label>
          <input
            id="scopes"
            type="text"
            value={scopes}
            onChange={(e) => setScopes(e.target.value)}
            className="input"
            placeholder="https://cognitiveservices.azure.com/.default"
          />
        </div>

        <div className="form-group">
          <label htmlFor="account" className="label">Account (optional)</label>
          <input
            id="account"
            type="text"
            value={account}
            onChange={(e) => setAccount(e.target.value)}
            className="input"
            placeholder="user@domain.com"
          />
        </div>

        <div className="form-group form-actions">
          <button type="submit" className="btn btn-primary" disabled={isPending}>
            {isPending ? 'Acquiring Token...' : 'Get Bootstrap Token'}
          </button>
        </div>
      </form>

      {errors.length > 0 && (
        <div className="alert alert-error" role="alert">
          <ul>
            {errors.map((err, i) => <li key={i}>{err}</li>)}
          </ul>
        </div>
      )}

      {error && (
        <div className="alert alert-error" role="alert">
          {error.message}
        </div>
      )}

      {result && (
        <div className="result-card" aria-live="polite">
          <h3 className="result-title">Bootstrap Result</h3>
          <dl className="result-grid">
            <dt>Gateway Token</dt>
            <dd><code className="token-display">{result.gateway_token}</code></dd>

            <dt>Token Source</dt>
            <dd>
              <span className={`badge ${getSourceBadge(result.token_source)}`}>
                {result.token_source.replace('_', ' ')}
              </span>
            </dd>

            <dt>Token Expires In</dt>
            <dd>{result.token_expires_in} seconds</dd>

            <dt>Bootstrap Expires At</dt>
            <dd>{formatExpiry(result.bootstrap_expires_at)}</dd>
          </dl>

          <div className="result-actions">
            <button
              className="btn btn-secondary"
              onClick={() => navigator.clipboard.writeText(result.gateway_token)}
              aria-label="Copy gateway token to clipboard"
            >
              Copy Token
            </button>
          </div>
        </div>
      )}

      <div className="info-box">
        <h4>How This Fixes the 401 Error</h4>
        <p>
          The Anthropic Office add-in was sending expired Azure AD access tokens to the bootstrap endpoint.
          This tool implements the correct MSAL flow: <code>acquireTokenSilent()</code> before each bootstrap call,
          falling back to interactive login only when silent refresh fails.
        </p>
      </div>
    </section>
  )
}