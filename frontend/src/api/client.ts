import axios, { AxiosInstance, AxiosError, InternalAxiosRequestConfig } from 'axios'

declare global {
  interface ImportMetaEnv {
    readonly VITE_API_BASE_URL: string
  }
  interface ImportMeta {
    readonly env: ImportMetaEnv
  }
}

 const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api/v1'

class ApiClient {
  private client: AxiosInstance

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      headers: {
        'Content-Type': 'application/json',
      },
      timeout: 30000,
      withCredentials: true, // For cookie-based auth
    })

    // Request interceptor for CSRF token
    this.client.interceptors.request.use(
      (config: InternalAxiosRequestConfig) => {
        const csrfToken = this.getCsrfToken()
        if (csrfToken && config.method !== 'get') {
          config.headers['X-CSRF-Token'] = csrfToken
        }
        return config
      },
      (error) => Promise.reject(error)
    )

    // Response interceptor for error handling
    this.client.interceptors.response.use(
      (response) => response,
      (error: AxiosError) => {
        if (error.response?.status === 401) {
          // Handle unauthorized - redirect to login
          window.location.href = '/login'
        }
        return Promise.reject(error)
      }
    )
  }

  private getCsrfToken(): string | null {
    const name = 'csrf_token='
    const decodedCookie = decodeURIComponent(document.cookie)
    const ca = decodedCookie.split(';')
    for (let i = 0; i < ca.length; i++) {
      let c = ca[i].trim()
      if (c.indexOf(name) === 0) {
        return c.substring(name.length, c.length)
      }
    }
    return null
  }

  // Bedrock Model Resolution
  async resolveModel(region: string, foundationModelId: string) {
    const response = await this.client.post('/bedrock/resolve', {
      region,
      foundation_model_id: foundationModelId,
    })
    return response.data
  }

  async generateIamPolicy(region: string, roleArn: string) {
    const response = await this.client.post('/bedrock/iam-policy', {
      region,
      role_arn: roleArn,
    })
    return response.data
  }

  // Plugin Validation
  async validatePlugins(pluginsRoot: string) {
    const response = await this.client.post('/plugins/validate', {
      plugins_root: pluginsRoot,
    })
    return response.data
  }

  async fixPlugins(pluginsRoot: string) {
    const response = await this.client.post('/plugins/fix', {
      plugins_root: pluginsRoot,
    })
    return response.data
  }

  // Bootstrap Token
  async bootstrapToken(
    bootstrapUrl: string,
    clientId: string,
    tenantId: string,
    scopes?: string[],
    account?: string
  ) {
    const response = await this.client.post('/bootstrap/token', {
      bootstrap_url: bootstrapUrl,
      client_id: clientId,
      tenant_id: tenantId,
      scopes,
      account,
    })
    return response.data
  }

  // Health
  async healthCheck() {
    const response = await this.client.get('/health')
    return response.data
  }
}

export const apiClient = new ApiClient()