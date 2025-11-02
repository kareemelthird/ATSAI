import axios from 'axios'

// In production, use relative URLs; in development, use localhost
const getAPIBaseURL = () => {
  // Check if we're in production (Vercel deployment)
  if (import.meta.env.PROD) {
    // Use relative URL in production - this will use the same domain
    return window.location.origin
  }
  
  // In development, use the VITE_API_URL or fallback to localhost
  return import.meta.env.VITE_API_URL || 'http://localhost:8000'
}

const API_BASE_URL = getAPIBaseURL()

// Debug: Log the API URL being used
console.log('🔧 API Base URL:', API_BASE_URL)
console.log('🔧 Environment:', import.meta.env.MODE)
console.log('🔧 Production mode:', import.meta.env.PROD)
console.log('🔧 VITE_API_URL from env:', import.meta.env.VITE_API_URL)
console.log('🔧 Window location origin:', window.location.origin)

export const api = axios.create({
  baseURL: `${API_BASE_URL}/api/v1`,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle 401 errors
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    
    // If 401 and not already retrying
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      
      const refreshToken = localStorage.getItem('refresh_token');
      if (refreshToken) {
        try {
          // Try to refresh the token
          const response = await axios.post(`${API_BASE_URL}/api/v1/auth/refresh`, {
            refresh_token: refreshToken
          });
          
          const { access_token } = response.data;
          localStorage.setItem('access_token', access_token);
          
          // Retry the original request
          originalRequest.headers.Authorization = `Bearer ${access_token}`;
          return api(originalRequest);
        } catch (refreshError) {
          // Refresh failed, clear tokens and redirect to login
          localStorage.removeItem('access_token');
          localStorage.removeItem('refresh_token');
          localStorage.removeItem('user');
          window.location.href = '/login';
          return Promise.reject(refreshError);
        }
      } else {
        // No refresh token, redirect to login
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        localStorage.removeItem('user');
        window.location.href = '/login';
      }
    }
    
    return Promise.reject(error);
  }
)

// Candidate APIs
export const candidateApi = {
  getAll: (params?: { skip?: number; limit?: number; status?: string }) =>
    api.get('/candidates/', { params }),
  
  getById: (id: string) =>
    api.get(`/candidates/${id}`),
  
  getComplete: (id: string) =>
    api.get(`/candidates/${id}/complete`),
  
  create: (data: any) =>
    api.post('/candidates/', data),
  
  update: (id: string, data: any) =>
    api.put(`/candidates/${id}`, data),
  
  delete: (id: string) =>
    api.delete(`/candidates/${id}`),
}

// Resume APIs
export const resumeApi = {
  uploadAuto: (file: File) => {
    const formData = new FormData()
    formData.append('file', file)
    return api.post(`/resumes/upload`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
  },
  
  upload: (candidateId: string, file: File) => {
    const formData = new FormData()
    formData.append('file', file)
    return api.post(`/resumes/upload/${candidateId}`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
  },
  
  getByCandidateId: (candidateId: string) =>
    api.get(`/resumes/candidate/${candidateId}`),
  
  getById: (id: string) =>
    api.get(`/resumes/${id}`),
  
  delete: (id: string) =>
    api.delete(`/resumes/${id}`),
}

// Job APIs
export const jobApi = {
  getAll: (params?: { skip?: number; limit?: number; status?: string }) =>
    api.get('/jobs/', { params }),
  
  getById: (id: string) =>
    api.get(`/jobs/${id}`),
  
  create: (data: any) =>
    api.post('/jobs/', data),
  
  update: (id: string, data: any) =>
    api.put(`/jobs/${id}`, data),
  
  delete: (id: string) =>
    api.delete(`/jobs/${id}`),
}

// Application APIs
export const applicationApi = {
  getAll: (params?: { skip?: number; limit?: number; candidate_id?: string; job_id?: string }) =>
    api.get('/applications/', { params }),
  
  getById: (id: string) =>
    api.get(`/applications/${id}`),
  
  create: (data: any) =>
    api.post('/applications/', data),
  
  update: (id: string, data: any) =>
    api.put(`/applications/${id}`, data),
}

// AI APIs
export const aiApi = {
  chat: (query_text: string, conversation_history?: any[], user_id?: string) =>
    api.post('/ai/chat', { query_text, conversation_history, user_id }),
  
  search: (query: string, limit?: number) =>
    api.post('/ai/search', { query, limit: limit || 10 }),
  
  getQueryHistory: (params?: { skip?: number; limit?: number; user_id?: string }) =>
    api.get('/ai/queries', { params }),
  
  deleteAllQueries: (user_id: string = 'anonymous') =>
    api.delete('/ai/queries', { params: { user_id } }),
}
