import { BedrockResolver } from '../components'

export default function BedrockPage() {
  return (
    <div className="page">
      <header className="page-header">
        <h1>Bedrock Model Resolver</h1>
        <p>Resolve correct inference profile IDs for AWS Bedrock regions</p>
      </header>
      <BedrockResolver />
    </div>
  )
}