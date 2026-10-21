import { useState } from 'react'
import { usePluginValidator, usePluginFixer, validatePluginForm } from '../hooks/useApi'
import { PluginValidationResult } from '../types'

export function PluginValidator() {
  const [pluginsRoot, setPluginsRoot] = useState('')
  const [results, setResults] = useState<PluginValidationResult[]>([])
  const [errors, setErrors] = useState<string[]>([])
  const [activeTab, setActiveTab] = useState<'validate' | 'fix'>('validate')

  const { mutate: validate, isPending: isValidating, error: validateError } = usePluginValidator()
  const { mutate: fix, isPending: isFixing, error: fixError } = usePluginFixer()

  const handleValidate = (e: React.FormEvent) => {
    e.preventDefault()
    const formErrors = validatePluginForm({ pluginsRoot })
    if (formErrors.length > 0) {
      setErrors(formErrors)
      return
    }
    setErrors([])
    validate(
      { pluginsRoot },
      {
        onSuccess: (data) => setResults(data.results),
        onError: (err) => setErrors([err.message]),
      }
    )
  }

  const handleFix = (e: React.FormEvent) => {
    e.preventDefault()
    const formErrors = validatePluginForm({ pluginsRoot })
    if (formErrors.length > 0) {
      setErrors(formErrors)
      return
    }
    setErrors([])
    fix(
      { pluginsRoot },
      {
        onSuccess: (data) => setResults(data.results),
        onError: (err) => setErrors([err.message]),
      }
    )
  }

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'passed': return 'bg-green-100 text-green-800'
      case 'failed': return 'bg-red-100 text-red-800'
      case 'fixed': return 'bg-blue-100 text-blue-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  const getTypeBadge = (type: string) => {
    return type === 'hooks' ? 'bg-purple-100 text-purple-800' : 'bg-teal-100 text-teal-800'
  }

  const formatErrors = (errs: string[]) => errs.join('; ')

  return (
    <section className="card" aria-labelledby="plugin-heading">
      <h2 id="plugin-heading" className="section-title">
        Plugin Configuration Validator
      </h2>
      <p className="section-description">
        Validate and fix plugin configuration files. Detects common issues:
        <ul className="inline-list">
          <li>hooks.json with bare <code>[]</code> instead of <code>{JSON.stringify({"hooks": {}})}</code></li>
          <li>.mcp.json syntax errors (missing commas, unclosed braces)</li>
        </ul>
      </p>

      <form onSubmit={activeTab === 'validate' ? handleValidate : handleFix} className="form-grid" noValidate>
        <div className="form-group">
          <label htmlFor="plugins-root" className="label">Plugins Root Directory</label>
          <input
            id="plugins-root"
            type="text"
            value={pluginsRoot}
            onChange={(e) => setPluginsRoot(e.target.value)}
            className="input"
            placeholder="/path/to/plugins/vertical-plugins"
            required
          />
        </div>

        <div className="form-group form-actions">
          <div className="tab-buttons" role="tablist" aria-label="Validation actions">
            <button
              role="tab"
              aria-selected={activeTab === 'validate'}
              onClick={() => setActiveTab('validate')}
              className={`btn ${activeTab === 'validate' ? 'btn-primary' : 'btn-secondary'}`}
              disabled={isValidating || isFixing}
            >
              Validate
            </button>
            <button
              role="tab"
              aria-selected={activeTab === 'fix'}
              onClick={() => setActiveTab('fix')}
              className={`btn ${activeTab === 'fix' ? 'btn-primary' : 'btn-secondary'}`}
              disabled={isValidating || isFixing}
            >
              Validate & Fix
            </button>
          </div>
        </div>
      </form>

      {errors.length > 0 && (
        <div className="alert alert-error" role="alert">
          <ul>
            {errors.map((err, i) => <li key={i}>{err}</li>)}
          </ul>
        </div>
      )}

      {(validateError || fixError) && (
        <div className="alert alert-error" role="alert">
          {validateError?.message || fixError?.message}
        </div>
      )}

      {results.length > 0 && (
        <div className="result-card" aria-live="polite">
          <h3 className="result-title">
            Validation Results ({results.length})
            <span className="results-summary">
              {results.filter(r => r.status === 'passed').length} passed,
              {results.filter(r => r.status === 'failed').length} failed,
              {results.filter(r => r.status === 'fixed').length} fixed
            </span>
          </h3>

          <div className="results-table-container">
            <table className="results-table">
              <thead>
                <tr>
                  <th scope="col">Plugin</th>
                  <th scope="col">Type</th>
                  <th scope="col">Status</th>
                  <th scope="col">File</th>
                  <th scope="col">Errors</th>
                </tr>
              </thead>
              <tbody>
                {results.map((result, i) => (
                  <tr key={i}>
                    <td>{result.plugin_name}</td>
                    <td>
                      <span className={`badge ${getTypeBadge(result.validation_type)}`}>
                        {result.validation_type}
                      </span>
                    </td>
                    <td>
                      <span className={`badge ${getStatusBadge(result.status)}`}>
                        {result.status}
                      </span>
                    </td>
                    <td><code>{result.file_path}</code></td>
                    <td className="errors-cell">
                      {result.errors.length > 0 ? formatErrors(result.errors) : '—'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {results.some(r => r.fixed_content) && (
            <details className="fixed-content-section">
              <summary>Fixed Content Details</summary>
              {results
                .filter(r => r.fixed_content)
                .map((result, i) => (
                  <div key={i} className="fixed-content-item">
                    <h4>{result.plugin_name} - {result.validation_type}.json</h4>
                    <pre><code>{result.fixed_content}</code></pre>
                  </div>
                ))}
            </details>
          )}
        </div>
      )}
    </section>
  )
}