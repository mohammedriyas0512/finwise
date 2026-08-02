import { useState, useEffect, useCallback } from 'react'
import { useForm } from 'react-hook-form'
import { FiPlus, FiEdit2, FiTrash2, FiRepeat, FiBell } from 'react-icons/fi'
import api from '../services/api.js'
import { useToast } from '../context/ToastContext.jsx'
import { useAuth } from '../context/AuthContext.jsx'
import PageHeader from '../components/PageHeader.jsx'
import { Input, Button } from '../components/Form.jsx'
import Modal from '../components/Modal.jsx'
import ConfirmDialog from '../components/ConfirmDialog.jsx'
import DataTable from '../components/DataTable.jsx'
import { FullSpinner, EmptyState } from '../components/Feedback.jsx'
import { formatCurrency } from '../utils/format.js'

export default function RecurringExpenses() {
  const toast = useToast()
  const { user } = useAuth()
  const currency = user?.currency || 'INR'
  const [rows, setRows] = useState([])
  const [loading, setLoading] = useState(true)
  const [modalOpen, setModalOpen] = useState(false)
  const [editing, setEditing] = useState(null)
  const [deleting, setDeleting] = useState(null)
  const [saving, setSaving] = useState(false)
  const { register, handleSubmit, reset, formState: { errors } } = useForm()

  const load = useCallback(async () => {
    setLoading(true)
    try { const res = await api.get('/bills'); setRows(res.data) }
    catch (e) { toast.error(e.message) } finally { setLoading(false) }
  }, [toast])
  const [tick, setTick] = useState(0)
  useEffect(() => { load() }, [tick, load])
  const refresh = useCallback(() => setTick((t) => t + 1), [])

  const openCreate = () => { setEditing(null); reset({ due_day: 1, is_recurring: true, is_active: true }); setModalOpen(true) }
  const openEdit = (r) => { setEditing(r); reset({ ...r }); setModalOpen(true) }

  const onSubmit = async (data) => {
    setSaving(true)
    const payload = { ...data, amount: parseFloat(data.amount), due_day: parseInt(data.due_day), is_recurring: !!data.is_recurring, is_active: !!data.is_active }
    try {
      if (editing) await api.patch(`/bills/${editing.id}`, payload)
      else await api.post('/bills', payload)
      toast.success(editing ? 'Bill updated' : 'Bill added'); setModalOpen(false); refresh()
    } catch (e) { toast.error(e.message) }
    finally { setSaving(false) }
  }

  const confirmDelete = async () => {
    try { await api.delete(`/bills/${deleting.id}`); toast.success('Bill removed'); setDeleting(null); refresh() }
    catch (e) { toast.error(e.message) }
  }

  const columns = [
    { key: 'name', label: 'Name' },
    { key: 'category', label: 'Category' },
    { key: 'amount', label: 'Amount', render: (r) => <span className="font-semibold text-red-600">{formatCurrency(r.amount, currency)}</span> },
    { key: 'due_day', label: 'Due Day', render: (r) => `Day ${r.due_day}` },
    { key: 'is_recurring', label: 'Recurring', render: (r) => r.is_recurring ? 'Yes' : 'No' },
    { key: 'is_active', label: 'Active', render: (r) => r.is_active ? <span className="text-green-600">●</span> : <span className="text-slate-300">●</span> },
    { key: 'actions', label: '', render: (r) => (
      <div className="flex justify-end gap-1">
        <Button size="sm" variant="ghost" onClick={() => openEdit(r)}><FiEdit2 /></Button>
        <Button size="sm" variant="ghost" className="text-red-600" onClick={() => setDeleting(r)}><FiTrash2 /></Button>
      </div>
    ) },
  ]

  return (
    <div className="space-y-6">
      <PageHeader title="Recurring Expenses" subtitle="Track subscriptions & bills that repeat every month"
        actions={<Button onClick={openCreate}><FiPlus /> Add Bill</Button>} />
      {loading ? <FullSpinner /> : rows.length === 0 ? <EmptyState icon={FiRepeat} title="No recurring expenses" />
        : <DataTable columns={columns} rows={rows} />}

      <Modal open={modalOpen} onClose={() => setModalOpen(false)} title={editing ? 'Edit Bill' : 'Add Recurring Bill'} footer={
        <>
          <Button variant="outline" onClick={() => setModalOpen(false)}>Cancel</Button>
          <Button onClick={handleSubmit(onSubmit)} disabled={saving}>{saving ? 'Saving…' : 'Save'}</Button>
        </>
      }>
        <form className="space-y-4">
          <Input label="Name" placeholder="e.g. Netflix" {...register('name', { required: 'Required' })} error={errors.name?.message} />
          <Input label="Category" placeholder="e.g. Entertainment" {...register('category', { required: 'Required' })} error={errors.category?.message} />
          <Input label="Amount" type="number" step="0.01" {...register('amount', { required: true, min: 0.01 })} error={errors.amount?.message} />
          <Input label="Due Day of Month" type="number" min="1" max="31" {...register('due_day', { required: true })} error={errors.due_day?.message} />
          <label className="flex items-center gap-2 text-sm text-slate-600 dark:text-slate-300">
            <input type="checkbox" {...register('is_recurring')} /> Recurring every month
          </label>
          <label className="flex items-center gap-2 text-sm text-slate-600 dark:text-slate-300">
            <input type="checkbox" {...register('is_active')} /> Active
          </label>
        </form>
      </Modal>
      <ConfirmDialog open={!!deleting} message="Remove this recurring bill?" onConfirm={confirmDelete} onCancel={() => setDeleting(null)} confirmLabel="Remove" />
    </div>
  )
}
