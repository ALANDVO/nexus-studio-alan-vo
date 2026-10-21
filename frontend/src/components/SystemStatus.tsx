import { useQuery } from '@tanstack/react-query'
import { apiClient } from '../api/client'
import { HealthResponse } from '../types'

export function SystemStatus() {
  const { data, isLoading, error, refetch } = useQuery<HealthResponse, Error>({
    queryKey: ['health'],
    queryFn: () => apiClient.healthCheck(),
    refetchInterval: 30000,
  })

  if (isLoading) {
    return (
      <div className="status-bar loading">
        <span className="spinner" aria-hidden="true"></span>
        <span>Checking system status...</span>
      </div>
    )
  }

  if (error) {
    return (
      <div className="status-bar error" role="alert">
        <span className="status-indicator" aria-hidden="true">●</span>
        <span>System unhealthy: {error.message}</span>
        <button className="btn btn-sm btn-secondary" onClick={() => refetch()}>Retry</button>
      </div>
    )
  }

  return (
    <div className="status-bar healthy">
      <span className="status-indicator" aria-hidden="true">●</span>
      <span>{data?.service} is {data?.status}</span>
      <span className="status-time">Last checked: {new Date().toLocaleTimeString()}</span>
    </div>
  )
}