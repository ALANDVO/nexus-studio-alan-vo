import { useMutation, useQuery } from '@tanstack/react-query'
import { apiClient } from '../api/client'
import {
  BedrockResolveResponse,
  IAMPolicyResponse,
  PluginValidateResponse,
  BootstrapResponse,
  BedrockResolverFormData,
  IAMPolicyFormData,
  PluginValidatorFormData,
  BootstrapFormData,
  REGIONS,
  MODELS,
} from '../types'

// Bedrock Resolver Hook
export function useBedrockResolver() {
  return useMutation<BedrockResolveResponse, Error, BedrockResolverFormData>({
    mutationFn: ({ region, foundationModelId }) =>
      apiClient.resolveModel(region, foundationModelId),
  })
}

// IAM Policy Generator Hook
export function useIAMPolicyGenerator() {
  return useMutation<IAMPolicyResponse, Error, IAMPolicyFormData>({
    mutationFn: ({ region, roleArn }) =>
      apiClient.generateIamPolicy(region, roleArn),
  })
}

// Plugin Validator Hooks
export function usePluginValidator() {
  return useMutation<PluginValidateResponse, Error, PluginValidatorFormData>({
    mutationFn: ({ pluginsRoot }) => apiClient.validatePlugins(pluginsRoot),
  })
}

export function usePluginFixer() {
  return useMutation<PluginValidateResponse, Error, PluginValidatorFormData>({
    mutationFn: ({ pluginsRoot }) => apiClient.fixPlugins(pluginsRoot),
  })
}

// Bootstrap Token Hook
export function useBootstrapToken() {
  return useMutation<BootstrapResponse, Error, BootstrapFormData>({
    mutationFn: ({ bootstrapUrl, clientId, tenantId, scopes, account }) =>
      apiClient.bootstrapToken(bootstrapUrl, clientId, tenantId, scopes?.split(',').map(s => s.trim()), account),
  })
}

// Health Check Hook
export function useHealthCheck() {
  return useQuery({
    queryKey: ['health'],
    queryFn: () => apiClient.healthCheck(),
    refetchInterval: 30000,
  })
}

// Form validation helpers
export function validateBedrockForm(data: BedrockResolverFormData): string[] {
  const errors: string[] = []
  if (!data.region) errors.push('Region is required')
  if (!data.foundationModelId) errors.push('Foundation model ID is required')
  return errors
}

export function validateIAMForm(data: IAMPolicyFormData): string[] {
  const errors: string[] = []
  if (!data.region) errors.push('Region is required')
  if (!data.roleArn) errors.push('Role ARN is required')
  if (data.roleArn && !data.roleArn.startsWith('arn:aws:iam::')) {
    errors.push('Role ARN must start with arn:aws:iam::')
  }
  return errors
}

export function validatePluginForm(data: PluginValidatorFormData): string[] {
  const errors: string[] = []
  if (!data.pluginsRoot) errors.push('Plugins root path is required')
  return errors
}

export function validateBootstrapForm(data: BootstrapFormData): string[] {
  const errors: string[] = []
  if (!data.bootstrapUrl) errors.push('Bootstrap URL is required')
  if (!data.clientId) errors.push('Client ID is required')
  if (!data.tenantId) errors.push('Tenant ID is required')
  return errors
}

// Constants
export { REGIONS, MODELS }