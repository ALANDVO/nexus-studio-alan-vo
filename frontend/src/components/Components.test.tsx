import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { BrowserRouter } from 'react-router-dom'
import { BedrockResolver } from '../components/BedrockResolver'
import { IAMPolicyGenerator } from '../components/IAMPolicyGenerator'
import { PluginValidator } from '../components/PluginValidator'
import { BootstrapToken } from '../components/BootstrapToken'

// Mock API client
vi.mock('../api/client', () => ({
  apiClient: {
    resolveModel: vi.fn().mockResolvedValue({
      region: 'ap-southeast-2',
      foundation_model_id: 'anthropic.claude-3-sonnet-20240229-v1:0',
      inference_profile_id: 'au.anthropic.claude-3-sonnet-20240229-v1:0',
      prefix: 'au',
      inference_types_supported: ['INFERENCE_PROFILE'],
      is_valid: true,
    }),
    generateIamPolicy: vi.fn().mockResolvedValue({
      policy_json: JSON.stringify({
        Version: '2012-10-17',
        Statement: [{ Sid: 'BedrockInvokeAccess', Effect: 'Allow', Action: ['bedrock:InvokeModel'], Resource: ['*'] }],
      }, null, 2),
    }),
    validatePlugins: vi.fn().mockResolvedValue({
      results: [
        {
          plugin_name: 'financial-analysis',
          plugin_version: '0.1.0',
          validation_type: 'hooks',
          status: 'failed',
          file_path: '/plugins/financial-analysis/hooks/hooks.json',
          errors: ['Root must be an object'],
          fixed_content: '{"hooks": {}}',
        },
      ],
    }),
    fixPlugins: vi.fn().mockResolvedValue({
      results: [
        {
          plugin_name: 'financial-analysis',
          plugin_version: '0.1.0',
          validation_type: 'hooks',
          status: 'fixed',
          file_path: '/plugins/financial-analysis/hooks/hooks.json',
          errors: ['Root must be an object'],
          fixed_content: '{"hooks": {}}',
        },
      ],
    }),
    bootstrapToken: vi.fn().mockResolvedValue({
      gateway_token: 'mock-token-12345',
      bootstrap_expires_at: Date.now() + 3600000,
      token_source: 'silent_refresh',
      token_expires_in: 3600,
    }),
    healthCheck: vi.fn().mockResolvedValue({ status: 'healthy', service: 'nexus-studio' }),
  },
}))

const createWrapper = () => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
      mutations: { retry: false },
    },
  })
  return ({ children }: { children: React.ReactNode }) => (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        {children}
      </BrowserRouter>
    </QueryClientProvider>
  )
}

describe('BedrockResolver', () => {
  it('renders form with region and model selectors', () => {
    render(<BedrockResolver />, { wrapper: createWrapper() })
    expect(screen.getByLabelText('AWS Region')).toBeInTheDocument()
    expect(screen.getByLabelText('Foundation Model ID')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Resolve Model' })).toBeInTheDocument()
  })

  it('shows result after successful resolution', async () => {
    render(<BedrockResolver />, { wrapper: createWrapper() })
    fireEvent.click(screen.getByRole('button', { name: 'Resolve Model' }))

    await waitFor(() => {
      expect(screen.getByText('au.anthropic.claude-3-sonnet-20240229-v1:0')).toBeInTheDocument()
    })
    expect(screen.getByText('✓ Valid')).toBeInTheDocument()
  })
})

describe('IAMPolicyGenerator', () => {
  it('renders form with region and role ARN inputs', () => {
    render(<IAMPolicyGenerator />, { wrapper: createWrapper() })
    expect(screen.getByLabelText('AWS Region')).toBeInTheDocument()
    expect(screen.getByLabelText('IAM Role ARN')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Generate Policy' })).toBeInTheDocument()
  })

  it('displays generated policy JSON', async () => {
    render(<IAMPolicyGenerator />, { wrapper: createWrapper() })
    fireEvent.change(screen.getByLabelText('IAM Role ARN'), {
      target: { value: 'arn:aws:iam::123456789012:role/TestRole' },
    })
    fireEvent.click(screen.getByRole('button', { name: 'Generate Policy' }))

    await waitFor(() => {
      expect(document.body).toHaveTextContent('BedrockInvokeAccess')
    })
  })
})

describe('PluginValidator', () => {
  it('renders form with plugins root input', () => {
    render(<PluginValidator />, { wrapper: createWrapper() })
    expect(screen.getByLabelText('Plugins Root Directory')).toBeInTheDocument()
    expect(screen.getByRole('tab', { name: 'Validate' })).toBeInTheDocument()
    expect(screen.getByRole('tab', { name: 'Validate & Fix' })).toBeInTheDocument()
  })

  it('shows validation results in table', async () => {
    render(<PluginValidator />, { wrapper: createWrapper() })
    fireEvent.change(screen.getByLabelText('Plugins Root Directory'), {
      target: { value: '/tmp/plugins' },
    })
    fireEvent.click(screen.getByRole('tab', { name: 'Validate' }))

    await waitFor(() => {
      expect(screen.getByText('financial-analysis')).toBeInTheDocument()
      expect(screen.getByText('failed')).toBeInTheDocument()
      expect(screen.getByText('Root must be an object')).toBeInTheDocument()
    })
  })
})

describe('BootstrapToken', () => {
  it('renders form with all required fields', () => {
    render(<BootstrapToken />, { wrapper: createWrapper() })
    expect(screen.getByLabelText('Bootstrap Endpoint URL')).toBeInTheDocument()
    expect(screen.getByLabelText('Azure AD Client ID')).toBeInTheDocument()
    expect(screen.getByLabelText('Azure AD Tenant ID')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Get Bootstrap Token' })).toBeInTheDocument()
  })

  it('displays token result with source', async () => {
    render(<BootstrapToken />, { wrapper: createWrapper() })
    fireEvent.change(screen.getByLabelText('Bootstrap Endpoint URL'), {
      target: { value: 'https://example.com/bootstrap' },
    })
    fireEvent.change(screen.getByLabelText('Azure AD Client ID'), {
      target: { value: 'client-id' },
    })
    fireEvent.change(screen.getByLabelText('Azure AD Tenant ID'), {
      target: { value: 'tenant-id' },
    })
    fireEvent.click(screen.getByRole('button', { name: 'Get Bootstrap Token' }))

    await waitFor(() => {
      expect(screen.getByText('mock-token-12345')).toBeInTheDocument()
      expect(screen.getByText('silent refresh')).toBeInTheDocument()
    })
  })
})