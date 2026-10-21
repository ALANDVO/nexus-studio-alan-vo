import { IAMPolicyGenerator } from '../components'

export default function IAMPage() {
  return (
    <div className="page">
      <header className="page-header">
        <h1>IAM Policy Generator</h1>
        <p>Generate region-aware IAM policies for Bedrock access</p>
      </header>
      <IAMPolicyGenerator />
    </div>
  )
}