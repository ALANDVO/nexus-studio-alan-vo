// Nexus Studio - TypeScript Types

export interface BedrockResolveRequest {
  region: string
  foundation_model_id: string
}

export interface BedrockResolveResponse {
  region: string
  foundation_model_id: string
  inference_profile_id: string
  prefix: string
  inference_types_supported: string[]
  is_valid: boolean
  error_message?: string
}

export interface IAMPolicyRequest {
  region: string
  role_arn: string
}

export interface IAMPolicyResponse {
  policy_json: string
}

export interface PluginValidationResult {
  plugin_name: string
  plugin_version: string
  validation_type: 'hooks' | 'mcp'
  status: 'passed' | 'failed' | 'fixed'
  file_path: string
  errors: string[]
  fixed_content?: string
}

export interface PluginValidateResponse {
  results: PluginValidationResult[]
}

export interface BootstrapRequest {
  bootstrap_url: string
  client_id: string
  tenant_id: string
  scopes?: string[]
  account?: string
}

export interface BootstrapResponse {
  gateway_token: string
  bootstrap_expires_at: number
  token_source: string
  token_expires_in: number
}

export interface HealthResponse {
  status: string
  service: string
}

// Form types
export interface BedrockResolverFormData {
  region: string
  foundationModelId: string
}

export interface IAMPolicyFormData {
  region: string
  roleArn: string
}

export interface PluginValidatorFormData {
  pluginsRoot: string
}

export interface BootstrapFormData {
  bootstrapUrl: string
  clientId: string
  tenantId: string
  scopes: string
  account?: string
}

// UI State types
export type TabId = 'bedrock' | 'iam' | 'plugins' | 'bootstrap'

export interface TabConfig {
  id: TabId
  label: string
  icon: string
}

export const TABS: TabConfig[] = [
  { id: 'bedrock', label: 'Bedrock Resolver', icon: '🔍' },
  { id: 'iam', label: 'IAM Policy Generator', icon: '📋' },
  { id: 'plugins', label: 'Plugin Validator', icon: '✅' },
  { id: 'bootstrap', label: 'Bootstrap Token', icon: '🔐' },
]

// Region options
export const REGIONS = [
  { value: 'us-east-1', label: 'US East (N. Virginia)', prefix: 'us' },
  { value: 'us-west-2', label: 'US West (Oregon)', prefix: 'us' },
  { value: 'eu-west-1', label: 'EU West (Ireland)', prefix: 'eu' },
  { value: 'eu-central-1', label: 'EU Central (Frankfurt)', prefix: 'eu' },
  { value: 'ap-southeast-2', label: 'AP Southeast (Sydney)', prefix: 'au' },
  { value: 'ap-southeast-4', label: 'AP Southeast (Melbourne)', prefix: 'au' },
  { value: 'ap-northeast-1', label: 'AP Northeast (Tokyo)', prefix: 'apac' },
  { value: 'ap-south-1', label: 'AP South (Mumbai)', prefix: 'apac' },
]

// Model options
export const MODELS = [
  { value: 'anthropic.claude-3-opus-20240229-v1:0', label: 'Claude 3 Opus' },
  { value: 'anthropic.claude-3-sonnet-20240229-v1:0', label: 'Claude 3 Sonnet' },
  { value: 'anthropic.claude-3-haiku-20240307-v1:0', label: 'Claude 3 Haiku' },
  { value: 'anthropic.claude-3-5-sonnet-20240620-v1:0', label: 'Claude 3.5 Sonnet' },
  { value: 'anthropic.claude-3-5-haiku-20241022-v1:0', label: 'Claude 3.5 Haiku' },
  { value: 'anthropic.claude-4-opus-20250514-v1:0', label: 'Claude 4 Opus' },
  { value: 'anthropic.claude-4-sonnet-20250514-v1:0', label: 'Claude 4 Sonnet' },
  { value: 'anthropic.claude-4-haiku-20250514-v1:0', label: 'Claude 4 Haiku' },
]