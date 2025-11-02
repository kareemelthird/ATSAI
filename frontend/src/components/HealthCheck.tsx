import { useState, useEffect } from 'react'

const getAPIBaseURL = () => {
  if (import.meta.env.PROD) {
    return window.location.origin
  }
  return import.meta.env.VITE_API_URL || 'http://localhost:8000'
}

export function HealthCheck() {
  const [status, setStatus] = useState<{
    backend: 'checking' | 'healthy' | 'error'
    database: 'checking' | 'healthy' | 'error'
    message?: string
  }>({
    backend: 'checking',
    database: 'checking'
  })

  useEffect(() => {
    const checkHealth = async () => {
      const apiBaseUrl = getAPIBaseURL()
      
      try {
        console.log('🔍 Checking backend health at:', `${apiBaseUrl}/api/v1/health`)
        
        const response = await fetch(`${apiBaseUrl}/api/v1/health`, {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
          },
        })
        
        if (response.ok) {
          const data = await response.json()
          console.log('✅ Health check response:', data)
          
          setStatus({
            backend: 'healthy',
            database: data.database_status === 'connected' ? 'healthy' : 'error',
            message: data.message || 'System operational'
          })
        } else {
          console.error('❌ Health check failed with status:', response.status)
          const errorText = await response.text()
          console.error('❌ Error response:', errorText)
          
          setStatus({
            backend: 'error',
            database: 'error',
            message: `Backend error: ${response.status} - ${errorText.slice(0, 100)}`
          })
        }
      } catch (error) {
        console.error('❌ Health check error:', error)
        setStatus({
          backend: 'error',
          database: 'error',
          message: `Connection failed: ${error instanceof Error ? error.message : 'Unknown error'}`
        })
      }
    }

    checkHealth()
    
    // Check every 30 seconds
    const interval = setInterval(checkHealth, 30000)
    return () => clearInterval(interval)
  }, [])

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'healthy': return 'text-green-600'
      case 'error': return 'text-red-600'
      default: return 'text-yellow-600'
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'healthy': return '✅'
      case 'error': return '❌'
      default: return '⏳'
    }
  }

  return (
    <div className="bg-white border border-gray-200 rounded-lg p-4 mb-4">
      <h3 className="text-sm font-semibold text-gray-900 mb-3">System Status</h3>
      
      <div className="space-y-2">
        <div className="flex items-center justify-between">
          <span className="text-sm text-gray-600">Backend API</span>
          <span className={`text-sm font-medium ${getStatusColor(status.backend)}`}>
            {getStatusIcon(status.backend)} {status.backend}
          </span>
        </div>
        
        <div className="flex items-center justify-between">
          <span className="text-sm text-gray-600">Database</span>
          <span className={`text-sm font-medium ${getStatusColor(status.database)}`}>
            {getStatusIcon(status.database)} {status.database}
          </span>
        </div>
      </div>
      
      {status.message && (
        <div className="mt-3 p-2 bg-gray-50 rounded text-xs text-gray-600">
          {status.message}
        </div>
      )}
    </div>
  )
}

export default HealthCheck