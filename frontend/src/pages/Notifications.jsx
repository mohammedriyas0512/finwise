import { useState, useEffect, useCallback } from 'react'
import { FiBell, FiCheck, FiCheckCircle, FiTrash2 } from 'react-icons/fi'
import api from '../services/api.js'
import { useToast } from '../context/ToastContext.jsx'
import { useAuth } from '../context/AuthContext.jsx'
import PageHeader from '../components/PageHeader.jsx'
import { Button } from '../components/Form.jsx'
import { FullSpinner, EmptyState } from '../components/Feedback.jsx'
import { formatDate } from '../utils/format.js'

const TYPE_COLORS = {
  budget: 'bg-amber-100 text-amber-700 dark:bg-amber-900/40',
  emi: 'bg-blue-100 text-blue-700 dark:bg-blue-900/40',
  debt: 'bg-red-100 text-red-700 dark:bg-red-900/40',
  goal: 'bg-green-100 text-green-700 dark:bg-green-900/40',
  recurring: 'bg-violet-100 text-violet-700 dark:bg-violet-900/40',
  info: 'bg-slate-100 text-slate-700 dark:bg-slate-700',
}

export default function Notifications() {
  const toast = useToast()
  const { user } = useAuth()
  const [rows, setRows] = useState([])
  const [loading, setLoading] = useState(true)

  const load = useCallback(async () => {
    setLoading(true)
    try { const res = await api.get('/notifications?limit=100'); setRows(res.data) }
    catch (e) { toast.error(e.message) } finally { setLoading(false) }
  }, [toast])
  useEffect(() => { load() }, [load])

  const markRead = async (id) => {
    try { await api.post(`/notifications/${id}/read`); load() } catch (e) { toast.error(e.message) }
  }
  const markAll = async () => {
    try { await api.post('/notifications/read-all'); toast.success('All marked read'); load() } catch (e) { toast.error(e.message) }
  }
  const remove = async (id) => {
    try { await api.delete(`/notifications/${id}`); load() } catch (e) { toast.error(e.message) }
  }

  return (
    <div className="space-y-6">
      <PageHeader title="Notifications" subtitle="Reminders for budgets, EMIs, debts & goals"
        actions={<Button variant="outline" onClick={markAll}><FiCheckCircle /> Mark all read</Button>} />
      {loading ? <FullSpinner /> : rows.length === 0 ? <EmptyState icon={FiBell} title="No notifications" />
        : (
          <div className="space-y-3">
            {rows.map((n) => (
              <div key={n.id} className={`flex items-start gap-3 rounded-2xl border p-4 shadow-sm ${n.is_read ? 'border-slate-200 bg-white dark:border-slate-700 dark:bg-slate-800' : 'border-primary/40 bg-blue-50 dark:bg-blue-900/20'}`}>
                <span className={`mt-1 grid h-9 w-9 shrink-0 place-items-center rounded-full ${TYPE_COLORS[n.type] || TYPE_COLORS.info}`}><FiBell size={16} /></span>
                <div className="min-w-0 flex-1">
                  <div className="flex items-center gap-2">
                    <p className="font-semibold text-slate-700 dark:text-slate-200">{n.title}</p>
                    {!n.is_read && <span className="h-2 w-2 rounded-full bg-primary" />}
                  </div>
                  <p className="text-sm text-slate-500">{n.message}</p>
                  <p className="mt-1 text-xs text-slate-400">{formatDate(n.created_at, true)}</p>
                </div>
                <div className="flex flex-col gap-1">
                  {!n.is_read && <Button size="sm" variant="ghost" onClick={() => markRead(n.id)} title="Mark read"><FiCheck /></Button>}
                  <Button size="sm" variant="ghost" className="text-red-600" onClick={() => remove(n.id)} title="Delete"><FiTrash2 /></Button>
                </div>
              </div>
            ))}
          </div>
        )}
    </div>
  )
}
