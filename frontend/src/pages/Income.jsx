import { useState, useEffect } from 'react'
import { useForm } from 'react-hook-form'
import { FiPlus, FiEdit2, FiTrash2, FiSearch, FiTrendingUp } from 'react-icons/fi'
import api from '../services/api.js'
import { useToast } from '../context/ToastContext.jsx'
import { useAuth } from '../context/AuthContext.jsx'
import PageHeader, { SearchBar } from '../components/PageHeader.jsx'
import { Input, Select, Button } from '../components/Form.jsx'
import Modal from '../components/Modal.jsx'
import ConfirmDialog from '../components/ConfirmDialog.jsx'
import DataTable from '../components/DataTable.jsx'
import { FullSpinner, EmptyState } from '../components/Feedback.jsx'
import { formatCurrency, formatDate, INCOME_CATEGORIES } from '../utils/format.js'

export default function IncomePage() {
  const toast = useToast()
  const { user } = useAuth()
  const currency = user?.currency || 'INR'
  const [rows, setRows] = useState([])
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState('')
  const [category, setCategory] = useState('')
  const [sortBy, setSortBy] = useState('date')
  const [order, setOrder] = useState('desc')
  const [modalOpen, setModalOpen] = useState(false)
  const [editing, setEditing] = useState(null)
  const [deleting, setDeleting] = useState(null)
  const [saving, setSaving] = useState(false)
  const { register, handleSubmit, reset, formState: { errors } } = useForm()

  // Stable loader reading the latest filter values from refs.
  const [tick, setTick] = useState(0)
  const load = async () => {
    setLoading(true)
    try {
      const params = new URLSearchParams({ sort_by: sortBy, order })
      if (category) params.set('category', category)
      if (search) params.set('search', search)
      const res = await api.get(`/income?${params}`)
      setRows(res.data)
    } catch (e) { toast.error(e.message) }
    finally { setLoading(false) }
  }

  // Reload whenever filters or the manual refresh tick change.
  useEffect(() => { load() }, [tick, category, sortBy, order]) // eslint-disable-line react-hooks/exhaustive-deps
  const refresh = () => setTick((t) => t + 1)

  const openCreate = () => { setEditing(null); reset({ frequency: 'monthly', date: new Date().toISOString().slice(0, 16) }); setModalOpen(true) }
  const openEdit = (row) => { setEditing(row); reset({ ...row, date: new Date(row.date).toISOString().slice(0, 16) }); setModalOpen(true) }

  const onSubmit = async (data) => {
    setSaving(true)
    try {
      const payload = { ...data, amount: parseFloat(data.amount), date: new Date(data.date).toISOString() }
      if (editing) await api.patch(`/income/${editing.id}`, payload)
      else await api.post('/income', payload)
      toast.success(editing ? 'Income updated' : 'Income added')
      setModalOpen(false)
      refresh()
    } catch (e) { toast.error(e.message) }
    finally { setSaving(false) }
  }

  const confirmDelete = async () => {
    try { await api.delete(`/income/${deleting.id}`); toast.success('Income deleted'); setDeleting(null); refresh() }
    catch (e) { toast.error(e.message) }
  }

  const columns = [
    { key: 'date', label: 'Date', render: (r) => formatDate(r.date) },
    { key: 'category', label: 'Category' },
    { key: 'description', label: 'Description', render: (r) => r.description || '—' },
    { key: 'frequency', label: 'Frequency' },
    { key: 'amount', label: 'Amount', render: (r) => <span className="font-semibold text-green-600">{formatCurrency(r.amount, currency)}</span> },
    { key: 'actions', label: '', render: (r) => (
      <div className="flex justify-end gap-1">
        <Button size="sm" variant="ghost" onClick={() => openEdit(r)}><FiEdit2 /></Button>
        <Button size="sm" variant="ghost" className="text-red-600" onClick={() => setDeleting(r)}><FiTrash2 /></Button>
      </div>
    ) },
  ]

  return (
    <div className="space-y-6">
      <PageHeader title="Income Management" subtitle="Track every source of money"
        actions={<Button onClick={openCreate}><FiPlus /> Add Income</Button>} />

      <div className="flex flex-col gap-3 sm:flex-row sm:items-end">
        <div className="flex-1"><SearchBar value={search} onChange={(v) => { setSearch(v); setTimeout(refresh, 300) }} placeholder="Search description…" /></div>
        <Select value={category} onChange={(e) => { setCategory(e.target.value); setTimeout(refresh, 50) }} className="sm:w-48">
          <option value="">All Categories</option>
          {INCOME_CATEGORIES.map((c) => <option key={c} value={c}>{c}</option>)}
        </Select>
        <Select value={`${sortBy}-${order}`} onChange={(e) => { const [s, o] = e.target.value.split('-'); setSortBy(s); setOrder(o); setTimeout(refresh, 50) }} className="sm:w-44">
          <option value="date-desc">Newest</option>
          <option value="date-asc">Oldest</option>
          <option value="amount-desc">Amount ↓</option>
          <option value="amount-asc">Amount ↑</option>
        </Select>
      </div>

      {loading ? <FullSpinner /> : (
        rows.length === 0 ? <EmptyState icon={FiTrendingUp} title="No income records" description="Add your first income to get started." />
        : <DataTable columns={columns} rows={rows} />
      )}

      <Modal open={modalOpen} onClose={() => setModalOpen(false)} title={editing ? 'Edit Income' : 'Add Income'} footer={
        <>
          <Button variant="outline" onClick={() => setModalOpen(false)}>Cancel</Button>
          <Button onClick={handleSubmit(onSubmit)} disabled={saving}>{saving ? 'Saving…' : 'Save'}</Button>
        </>
      }>
        <form className="space-y-4">
          <Input label="Amount" type="number" step="0.01" placeholder="0.00" {...register('amount', { required: 'Required' })} error={errors.amount?.message} />
          <Select label="Category" {...register('category', { required: 'Required' })} error={errors.category?.message}>
            {INCOME_CATEGORIES.map((c) => <option key={c} value={c}>{c}</option>)}
          </Select>
          <Input label="Date" type="datetime-local" {...register('date', { required: 'Required' })} error={errors.date?.message} />
          <Select label="Frequency" {...register('frequency')}>
            <option value="monthly">Monthly</option>
            <option value="weekly">Weekly</option>
            <option value="one_time">One Time</option>
          </Select>
          <Input label="Description (optional)" placeholder="e.g. July salary" {...register('description')} />
        </form>
      </Modal>

      <ConfirmDialog open={!!deleting} message="This income record will be permanently deleted." onConfirm={confirmDelete} onCancel={() => setDeleting(null)} confirmLabel="Delete" />
    </div>
  )
}
