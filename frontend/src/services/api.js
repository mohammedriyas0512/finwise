import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  headers: { 'Content-Type': 'application/json' },
})

// Attach JWT from localStorage to every request.
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('finwise_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Normalize errors so callers can show friendly messages.
api.interceptors.response.use(
  (response) => response,
  (error) => {
    const message =
      error.response?.data?.detail ||
      (typeof error.response?.data?.errors === 'object'
        ? JSON.stringify(error.response.data.errors)
        : null) ||
      error.message ||
      'Something went wrong'
    return Promise.reject(new Error(message))
  },
)

export default api
