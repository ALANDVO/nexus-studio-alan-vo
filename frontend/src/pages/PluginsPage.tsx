import { PluginValidator } from '../components'

export default function PluginsPage() {
  return (
    <div className="page">
      <header className="page-header">
        <h1>Plugin Validator</h1>
        <p>Validate and fix plugin configuration files (hooks.json, .mcp.json)</p>
      </header>
      <PluginValidator />
    </div>
  )
}