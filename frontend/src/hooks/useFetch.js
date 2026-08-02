import { useCallback, useEffect, useState } from 'react'
import api from '../services/api.js'
import { useToast } from '../context/ToastContext.jsx'

// Generic fetch hook with loading/error state and manual refetch.
export function useFetch(url, { immediate = true, deps = [] } = {}) {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(immediate)
  const [error, setError] = useState(null)
  const toast = useToast()

  const load = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const res = await api.get(url)
      setData(res.data)
      return res.data
    } catch (err) {
      setError(err.message)
      toast.error(err.message)
      return null
    } finally {
      setLoading(false)
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [url, ...deps])

  useEffect(() => {
    if (immediate) load()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [immediate, load])

  return { data, loading, error, refetch: load }
}
