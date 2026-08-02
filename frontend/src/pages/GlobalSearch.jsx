import { useState, useEffect } from 'react'
import { useForm } from 'react-hook-form'
import { FiSearch, FiTrendingUp, FiTrendingDown } from 'react-icons/fi'
import api from '../services/api.js'
import { useToast } from '../context/ToastContext.jsx'
import { useAuth } from '../context/AuthContext.jsx'
import PageHeader, { SearchBar } from '../components/PageHeader.jsx'
import { Input, Select, Button } from '../components/Form.jsx'
import DataTable from '../components/DataTable.jsx'
import { FullSpinner, EmptyState } from '../components/Feedback.jsx'
import { formatCurrency, formatDate } from '../utils/format.js'

export default function GlobalSearch() {
  const toast = useToast()
  const { user } = useAuth()
  const currency = user?.currency || 'INR'
  const [rows, setRows] = useState([])
  const [loading, setLoading] = useState(false)
  const [filters, setFilters] = useState({ q: '', txn_type: '', category: '', min_amount: '', max_amount: '' })
  const [expanded, setExpanded] = useState(false)

  const search = async () => {
    setLoading(true)
    try {
      const params = new URLSearchParams()
      if (filters.q) params.set('q', filters.q)
      if (filters.txn_type) params.set('txn_type', filters.txn_type)
      if (filters.category) params.set('category', filters.category)
      if (filters.min_amount) params.set('min_amount', filters.min_amount)
      if (filters.max_amount) params.set('max_amount', filters.max_amount)
      const res = await api.get(`/transactions?${params}`)
      setRows(res.data)
    } catch (e) { toast.error(e.message) }
    finally { setLoading(false) }
  }

  useEffect(() => { search() }, []) // initial load (all)

  const columns = [
    { key: 'date', label: 'Date', render: (r) => formatDate(r.date) },
    { key: 'txn_type', label: 'Type', render: (r) => <span className={`rounded-full px-2 py-0.5 text-xs font-semibold ${r.txn_type === 'income' ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'}`}>{r.txn_type}</span> },
    { key: 'category', label: 'Category' },
    { key: 'description', label: 'Description', render: (r) => r.description || '—' },
    { key: 'amount', label: 'Amount', render: (r) => <span className={`font-semibold ${r.txn_type === 'income' ? 'text-green-600' : 'text-red-600'}`}>{formatCurrency(r.amount, currency)}</span> },
  ]

  return (
    <div className="space-y-6">
      <PageHeader title="Global Search" subtitle="Search & filter all your transactions" />

      <div className="space-y-3 rounded-2xl border border-slate-200 bg-white p-5 shadow-sm dark:border-slate-700 dark:bg-slate-800">
        <SearchBar value={filters.q} onChange={(v) => { setFilters((f) => ({ ...f, q: v })); setTimeout(search, 300) }} />
        <button onClick={() => setExpanded((e) => !e)} className="text-sm font-medium text-primary hover:underline">
          {expanded ? 'Hide filters' : 'Advanced filters'}
        </button>
        {expanded && (
          <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-4">
            <Select value={filters.txn_type} onChange={(e) => { setFilters((f) => ({ ...f, txn_type: e.target.value })); setTimeout(search, 50) }}>
              <option value="">All Types</option>
              <option value="income">Income</option>
              <option value="expense">Expense</option>
            </Select>
            <Input placeholder="Category" value={filters.category} onChange={(e) => { setFilters((f) => ({ ...f, category: e.target.value })); setTimeout(search, 200) }} />
            <Input type="number" placeholder="Min amount" value={filters.min_amount} onChange={(e) => { setFilters((f) => ({ ...f, min_amount: e.target.value })); setTimeout(search, 300) }} />
            <Input type="number" placeholder="Max amount" value={filters.max_amount} onChange={(e) => { setFilters((f) => ({ ...f, max_amount: e.target.value })); setTimeout(search, 300) }} />
          </div>
        )}
      </div>

      {loading ? <FullSpinner /> : rows.length === 0 ? <EmptyState icon={FiSearch} title="No transactions found" />
        : <DataTable columns={columns} rows={rows} />}
    </div>
  )
}
