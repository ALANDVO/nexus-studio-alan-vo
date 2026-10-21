import { useState } from 'react'
import { useIAMPolicyGenerator, REGIONS, validateIAMForm } from '../hooks/useApi'
import { IAMPolicyResponse } from '../types'

export function IAMPolicyGenerator() {
  const [region, setRegion] = useState('us-east-1')
  const [roleArn, setRoleArn] = useState('')
  const [result, setResult] = useState<IAMPolicyResponse | null>(null)
  const [errors, setErrors] = useState<string[]>([])

  const { mutate, isPending, error } = useIAMPolicyGenerator()

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    const formErrors = validateIAMForm({ region, roleArn })
    if (formErrors.length > 0) {
      setErrors(formErrors)
      return
    }
    setErrors([])
    mutate(
      { region, roleArn },
      {
        onSuccess: (data) => setResult(data),
        onError: (err) => setErrors([err.message]),
      }
    )
  }

  const handleCopy = async () => {
    if (result) {
      await navigator.clipboard.writeText(result.policy_json)
    }
  }

  const handleDownload = () => {
    if (result) {
      const blob = new Blob([result.policy_json], { type: 'application/json' })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `bedrock-iam-policy-${region}.json`
      a.click()
      URL.revokeObjectURL(url)
    }
  }

  return (
    <section className="card" aria-labelledby="iam-heading">
      <h2 id="iam-heading" className="section-title">
        IAM Policy Generator
      </h2>
      <p className="section-description">
        Generate region-aware IAM policies for Bedrock access. The policy automatically uses the correct
        geographic prefix (<code>us.*</code>, <code>eu.*</code>, <code>au.*</code>, <code>apac.*</code>)
        based on the selected region.
      </p>

      <form onSubmit={handleSubmit} className="form-grid" noValidate>
        <div className="form-group">
          <label htmlFor="iam-region" className="label">AWS Region</label>
          <select
            id="iam-region"
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
          <label htmlFor="role-arn" className="label">IAM Role ARN</label>
          <input
            id="role-arn"
            type="text"
            value={roleArn}
            onChange={(e) => setRoleArn(e.target.value)}
            className="input"
            placeholder="arn:aws:iam::123456789012:role/BedrockAccessRole"
            required
          />
        </div>

        <div className="form-group form-actions">
          <button type="submit" className="btn btn-primary" disabled={isPending}>
            {isPending ? 'Generating...' : 'Generate Policy'}
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
          <h3 className="result-title">Generated IAM Policy</h3>
          <div className="policy-preview">
            <pre><code>{result.policy_json}</code></pre>
          </div>
          <div className="result-actions">
            <button className="btn btn-secondary" onClick={handleCopy}>
              Copy JSON
            </button>
            <button className="btn btn-secondary" onClick={handleDownload}>
              Download .json
            </button>
          </div>
          <p className="policy-note">
            This policy includes: Bedrock invoke permissions for foundation models and inference profiles,
            list/get permissions, and STS AssumeRole for the specified role ARN.
          </p>
        </div>
      )}
    </section>
  )
}