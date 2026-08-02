import { useState, useEffect, useCallback } from 'react'
import { useForm } from 'react-hook-form'
import { FiPlus, FiEdit2, FiTrash2, FiCreditCard } from 'react-icons/fi'
import api from '../services/api.js'
import { useToast } from '../context/ToastContext.jsx'
import { useAuth } from '../context/AuthContext.jsx'
import PageHeader, { SearchBar } from '../components/PageHeader.jsx'
import { Input, Select, Button } from '../components/Form.jsx'
import Modal from '../components/Modal.jsx'
import ConfirmDialog from '../components/ConfirmDialog.jsx'
import DataTable from '../components/DataTable.jsx'
import { FullSpinner, EmptyState } from '../components/Feedback.jsx'
import { formatCurrency, formatDate, EXPENSE_CATEGORIES } from '../utils/format.js'

export default function ExpensesPage() {
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

  const load = useCallback(async () => {
    setLoading(true)
    try {
      const params = new URLSearchParams({ sort_by: sortBy, order })
      if (category) params.set('category', category)
      if (search) params.set('search', search)
      const res = await api.get(`/expenses?${params}`)
      setRows(res.data)
    } catch (e) { toast.error(e.message) }
    finally { setLoading(false) }
  }, [sortBy, order, category, search, toast])

  const [tick, setTick] = useState(0)
  useEffect(() => { load() }, [tick, load])
  const refresh = useCallback(() => setTick((t) => t + 1), [])

  const openCreate = () => { setEditing(null); reset({ date: new Date().toISOString().slice(0, 16) }); setModalOpen(true) }
  const openEdit = (row) => { setEditing(row); reset({ ...row, date: new Date(row.date).toISOString().slice(0, 16) }); setModalOpen(true) }

  const onSubmit = async (data) => {
    setSaving(true)
    try {
      const payload = { ...data, amount: parseFloat(data.amount), date: new Date(data.date).toISOString() }
      if (editing) await api.patch(`/expenses/${editing.id}`, payload)
      else await api.post('/expenses', payload)
      toast.success(editing ? 'Expense updated' : 'Expense added')
      setModalOpen(false); refresh()
    } catch (e) { toast.error(e.message) }
    finally { setSaving(false) }
  }

  const confirmDelete = async () => {
    try { await api.delete(`/expenses/${deleting.id}`); toast.success('Expense deleted'); setDeleting(null); refresh() }
    catch (e) { toast.error(e.message) }
  }

  const total = rows.reduce((s, r) => s + Number(r.amount), 0)

  const columns = [
    { key: 'date', label: 'Date', render: (r) => formatDate(r.date) },
    { key: 'category', label: 'Category' },
    { key: 'description', label: 'Description', render: (r) => r.description || '—' },
    { key: 'payment_method', label: 'Method', render: (r) => r.payment_method || '—' },
    { key: 'amount', label: 'Amount', render: (r) => <span className="font-semibold text-red-600">{formatCurrency(r.amount, currency)}</span> },
    { key: 'actions', label: '', render: (r) => (
      <div className="flex justify-end gap-1">
        <Button size="sm" variant="ghost" onClick={() => openEdit(r)}><FiEdit2 /></Button>
        <Button size="sm" variant="ghost" className="text-red-600" onClick={() => setDeleting(r)}><FiTrash2 /></Button>
      </div>
    ) },
  ]

  return (
    <div className="space-y-6">
      <PageHeader title="Expense Tracker" subtitle={`${rows.length} records · ${formatCurrency(total, currency)} total`}
        actions={<Button onClick={openCreate}><FiPlus /> Add Expense</Button>} />

      <div className="flex flex-col gap-3 sm:flex-row sm:items-end">
        <div className="flex-1"><SearchBar value={search} onChange={(v) => { setSearch(v); setTimeout(refresh, 300) }} placeholder="Search description…" /></div>
        <Select value={category} onChange={(e) => { setCategory(e.target.value); setTimeout(refresh, 50) }} className="sm:w-48">
          <option value="">All Categories</option>
          {EXPENSE_CATEGORIES.map((c) => <option key={c} value={c}>{c}</option>)}
        </Select>
        <Select value={`${sortBy}-${order}`} onChange={(e) => { const [s, o] = e.target.value.split('-'); setSortBy(s); setOrder(o); setTimeout(refresh, 50) }} className="sm:w-44">
          <option value="date-desc">Newest</option>
          <option value="date-asc">Oldest</option>
          <option value="amount-desc">Amount ↓</option>
          <option value="amount-asc">Amount ↑</option>
        </Select>
      </div>

      {loading ? <FullSpinner /> : (
        rows.length === 0 ? <EmptyState icon={FiCreditCard} title="No expenses yet" description="Add your first expense to track spending." />
        : <DataTable columns={columns} rows={rows} />
      )}

      <Modal open={modalOpen} onClose={() => setModalOpen(false)} title={editing ? 'Edit Expense' : 'Add Expense'} footer={
        <>
          <Button variant="outline" onClick={() => setModalOpen(false)}>Cancel</Button>
          <Button onClick={handleSubmit(onSubmit)} disabled={saving}>{saving ? 'Saving…' : 'Save'}</Button>
        </>
      }>
        <form className="space-y-4">
          <Input label="Amount" type="number" step="0.01" placeholder="0.00" {...register('amount', { required: 'Required' })} error={errors.amount?.message} />
          <Select label="Category" {...register('category', { required: 'Required' })} error={errors.category?.message}>
            {EXPENSE_CATEGORIES.map((c) => <option key={c} value={c}>{c}</option>)}
          </Select>
          <Input label="Date" type="datetime-local" {...register('date', { required: 'Required' })} error={errors.date?.message} />
          <Input label="Payment Method (optional)" placeholder="UPI / Card / Cash" {...register('payment_method')} />
          <Input label="Description (optional)" placeholder="e.g. Groceries" {...register('description')} />
        </form>
      </Modal>

      <ConfirmDialog open={!!deleting} message="This expense will be permanently deleted." onConfirm={confirmDelete} onCancel={() => setDeleting(null)} confirmLabel="Delete" />
    </div>
  )
}
