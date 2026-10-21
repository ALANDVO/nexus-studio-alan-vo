import { useState } from 'react'
import { useBedrockResolver, REGIONS, MODELS, validateBedrockForm } from '../hooks/useApi'
import { BedrockResolveResponse } from '../types'

export function BedrockResolver() {
  const [region, setRegion] = useState('us-east-1')
  const [foundationModelId, setFoundationModelId] = useState(
    'anthropic.claude-3-sonnet-20240229-v1:0'
  )
  const [result, setResult] = useState<BedrockResolveResponse | null>(null)
  const [errors, setErrors] = useState<string[]>([])

  const { mutate, isPending, error } = useBedrockResolver()

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    const formErrors = validateBedrockForm({ region, foundationModelId })
    if (formErrors.length > 0) {
      setErrors(formErrors)
      return
    }
    setErrors([])
    mutate(
      { region, foundationModelId },
      {
        onSuccess: (data) => setResult(data),
        onError: (err) => setErrors([err.message]),
      }
    )
  }

  const getPrefixColor = (prefix: string) => {
    switch (prefix) {
      case 'us': return 'bg-blue-100 text-blue-800'
      case 'eu': return 'bg-green-100 text-green-800'
      case 'au': return 'bg-orange-100 text-orange-800'
      case 'apac': return 'bg-purple-100 text-purple-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  const getStatusColor = (isValid: boolean) => {
    return isValid ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
  }

  return (
    <section className="card" aria-labelledby="bedrock-heading">
      <h2 id="bedrock-heading" className="section-title">
        Bedrock Model Identifier Resolver
      </h2>
      <p className="section-description">
        Resolve the correct inference profile ID for your AWS region. AU regions (ap-southeast-2, ap-southeast-4)
        require <code>au.anthropic.*</code> cross-region inference profiles instead of US foundation model IDs.
      </p>

      <form onSubmit={handleSubmit} className="form-grid" noValidate>
        <div className="form-group">
          <label htmlFor="region" className="label">AWS Region</label>
          <select
            id="region"
            value={region}
            onChange={(e) => setRegion(e.target.value)}
            className="select"
            required
          >
            {REGIONS.map((r) => (
              <option key={r.value} value={r.value}>
                {r.label} <span className="prefix-badge">({r.prefix})</span>
              </option>
            ))}
          </select>
        </div>

        <div className="form-group">
          <label htmlFor="model" className="label">Foundation Model ID</label>
          <select
            id="model"
            value={foundationModelId}
            onChange={(e) => setFoundationModelId(e.target.value)}
            className="select"
            required
          >
            {MODELS.map((m) => (
              <option key={m.value} value={m.value}>{m.label}</option>
            ))}
          </select>
        </div>

        <div className="form-group form-actions">
          <button type="submit" className="btn btn-primary" disabled={isPending}>
            {isPending ? 'Resolving...' : 'Resolve Model'}
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
          <h3 className="result-title">Resolution Result</h3>
          <dl className="result-grid">
            <dt>Region</dt>
            <dd>{result.region}</dd>

            <dt>Foundation Model ID</dt>
            <dd><code>{result.foundation_model_id}</code></dd>

            <dt>Resolved Inference Profile ID</dt>
            <dd><code className="highlight">{result.inference_profile_id}</code></dd>

            <dt>Geographic Prefix</dt>
            <dd>
              <span className={`badge ${getPrefixColor(result.prefix)}`}>{result.prefix}</span>
            </dd>

            <dt>Supported Inference Types</dt>
            <dd>
              <div className="badge-group">
                {result.inference_types_supported.map((type) => (
                  <span key={type} className="badge badge-info">{type}</span>
                ))}
              </div>
            </dd>

            <dt>Valid</dt>
            <dd>
              <span className={`badge ${getStatusColor(result.is_valid)}`}>
                {result.is_valid ? '✓ Valid' : '✗ Invalid'}
              </span>
            </dd>

            {result.error_message && (
              <>
                <dt>Note</dt>
                <dd className="text-warning">{result.error_message}</dd>
              </>
            )}
          </dl>

          <div className="result-actions">
            <button
              className="btn btn-secondary"
              onClick={() => navigator.clipboard.writeText(result.inference_profile_id)}
              aria-label="Copy inference profile ID to clipboard"
            >
              Copy Profile ID
            </button>
          </div>
        </div>
      )}
    </section>
  )
}