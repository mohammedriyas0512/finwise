import { useState, useEffect, useCallback } from 'react'
import api from '../services/api.js'
import { useToast } from '../context/ToastContext.jsx'

// Shared list+CRUD state machine used by resource pages (income, expense, debt, goal, bill).
export function useCrud(endpoint) {
  const toast = useToast()
  const [rows, setRows] = useState([])
  const [loading, setLoading] = useState(true)
  const [tick, setTick] = useState(0)
  const refresh = useCallback(() => setTick((t) => t + 1), [])

  const load = useCallback(async () => {
    setLoading(true)
    try {
      const res = await api.get(endpoint)
      setRows(res.data)
    } catch (e) { toast.error(e.message) }
    finally { setLoading(false) }
  }, [endpoint]) // eslint-disable-line react-hooks/exhaustive-deps

  useEffect(() => { load() }, [tick, load])

  const create = async (payload) => {
    await api.post(endpoint, payload)
    refresh()
  }
  const update = async (id, payload) => {
    await api.patch(`${endpoint}/${id}`, payload)
    refresh()
  }
  const remove = async (id) => {
    await api.delete(`${endpoint}/${id}`)
    refresh()
  }

  return { rows, loading, refresh, create, update, remove }
}
