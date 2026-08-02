import { useState, useEffect, useCallback } from 'react'
import { FiUsers, FiTrendingUp, FiTrendingDown, FiTarget, FiActivity, FiShield } from 'react-icons/fi'
import api from '../services/api.js'
import { useToast } from '../context/ToastContext.jsx'
import PageHeader from '../components/PageHeader.jsx'
import StatCard from '../components/StatCard.jsx'
import DataTable from '../components/DataTable.jsx'
import { FullSpinner, EmptyState } from '../components/Feedback.jsx'
import { formatCurrency, formatDate } from '../utils/format.js'

export default function AdminPanel() {
  const toast = useToast()
  const [stats, setStats] = useState(null)
  const [users, setUsers] = useState([])
  const [activity, setActivity] = useState([])
  const [loading, setLoading] = useState(true)

  const load = useCallback(async () => {
    setLoading(true)
    try {
      const [s, u, a] = await Promise.all([
        api.get('/admin/stats'),
        api.get('/admin/users'),
        api.get('/admin/activity?limit=50'),
      ])
      setStats(s.data); setUsers(u.data); setActivity(a.data)
    } catch (e) { toast.error(e.message) }
    finally { setLoading(false) }
  }, [toast])
  useEffect(() => { load() }, [load])

  const toggleActive = async (u) => {
    try { await api.patch(`/admin/users/${u.id}/toggle-active`); toast.success('User status updated'); load() }
    catch (e) { toast.error(e.message) }
  }

  if (loading || !stats) return <FullSpinner label="Loading admin panel…" />

  const userCols = [
    { key: 'full_name', label: 'Name' },
    { key: 'email', label: 'Email' },
    { key: 'role', label: 'Role', render: (r) => <span className={`rounded-full px-2 py-0.5 text-xs font-semibold ${r.role === 'admin' ? 'bg-violet-100 text-violet-700' : 'bg-slate-100 text-slate-700'}`}>{r.role}</span> },
    { key: 'is_active', label: 'Status', render: (r) => r.is_active ? <span className="text-green-600">Active</span> : <span className="text-red-500">Disabled</span> },
    { key: 'created_at', label: 'Joined', render: (r) => formatDate(r.created_at) },
    { key: 'actions', label: '', render: (r) => (
      <button onClick={() => toggleActive(r)} className="text-sm font-medium text-primary hover:underline">
        {r.is_active ? 'Disable' : 'Enable'}
      </button>
    ) },
  ]

  const actCols = [
    { key: 'created_at', label: 'Time', render: (r) => formatDate(r.created_at, true) },
    { key: 'action', label: 'Action' },
    { key: 'entity', label: 'Entity', render: (r) => r.entity || '—' },
    { key: 'ip_address', label: 'IP', render: (r) => r.ip_address || '—' },
  ]

  return (
    <div className="space-y-6">
      <PageHeader title="Admin Panel" subtitle="System overview, user management & activity logs"
        actions={<span className="flex items-center gap-2 text-sm text-slate-400"><FiShield /> Administrator</span>} />

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5">
        <StatCard title="Total Users" value={stats.total_users} icon={FiUsers} accent="primary" />
        <StatCard title="Total Income" value={formatCurrency(stats.total_income)} icon={FiTrendingUp} accent="success" />
        <StatCard title="Total Expense" value={formatCurrency(stats.total_expense)} icon={FiTrendingDown} accent="danger" />
        <StatCard title="Avg Savings" value={formatCurrency(stats.average_savings)} icon={FiTarget} accent="warning" />
        <StatCard title="New (30d)" value={stats.new_users_last_30d} icon={FiActivity} accent="purple" />
      </div>

      <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm dark:border-slate-700 dark:bg-slate-800">
        <h3 className="mb-3 text-base font-bold text-slate-700 dark:text-slate-200">Most Used Category</h3>
        <p className="text-2xl font-extrabold text-primary">{stats.most_used_category || '—'}</p>
      </div>

      <div>
        <h3 className="mb-3 text-lg font-bold text-slate-700 dark:text-slate-200">User Management</h3>
        <DataTable columns={userCols} rows={users} />
      </div>

      <div>
        <h3 className="mb-3 text-lg font-bold text-slate-700 dark:text-slate-200">Activity Logs</h3>
        {activity.length === 0 ? <EmptyState title="No activity logged" /> : <DataTable columns={actCols} rows={activity} />}
      </div>
    </div>
  )
}
