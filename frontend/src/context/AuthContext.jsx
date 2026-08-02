import { createContext, useContext, useEffect, useState } from 'react'
import api from '../services/api.js'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  // Bootstrap: if a token exists, fetch the current user.
  useEffect(() => {
    const token = localStorage.getItem('finwise_token')
    if (!token) {
      setLoading(false)
      return
    }
    api
      .get('/auth/me')
      .then((res) => setUser(res.data))
      .catch(() => {
        localStorage.removeItem('finwise_token')
        localStorage.removeItem('finwise_user')
      })
      .finally(() => setLoading(false))
  }, [])

  const login = async (email, password) => {
    const { data } = await api.post('/auth/login', { email, password })
    localStorage.setItem('finwise_token', data.access_token)
    const me = await api.get('/auth/me')
    setUser(me.data)
    localStorage.setItem('finwise_user', JSON.stringify(me.data))
    return me.data
  }

  const register = async (payload) => {
    const { data } = await api.post('/auth/register', payload)
    return data
  }

  const logout = () => {
    localStorage.removeItem('finwise_token')
    localStorage.removeItem('finwise_user')
    setUser(null)
  }

  const updateUser = (next) => setUser(next)

  return (
    <AuthContext.Provider value={{ user, setUser: updateUser, loading, login, register, logout, isAdmin: user?.role === 'admin' }}>
      {children}
    </AuthContext.Provider>
  )
}

export const useAuth = () => useContext(AuthContext)
