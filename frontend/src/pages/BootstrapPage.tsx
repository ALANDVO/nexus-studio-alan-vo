import { BootstrapToken } from '../components'

export default function BootstrapPage() {
  return (
    <div className="page">
      <header className="page-header">
        <h1>Bootstrap Token Manager</h1>
        <p>Acquire valid tokens for bootstrap endpoints with automatic refresh</p>
      </header>
      <BootstrapToken />
    </div>
  )
}