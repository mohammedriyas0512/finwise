import { useState, useEffect, useCallback } from 'react'
import { useForm } from 'react-hook-form'
import { FiPlus, FiEdit2, FiTrash2, FiTarget } from 'react-icons/fi'
import api from '../services/api.js'
import { useToast } from '../context/ToastContext.jsx'
import { useAuth } from '../context/AuthContext.jsx'
import PageHeader from '../components/PageHeader.jsx'
import { Input, Button } from '../components/Form.jsx'
import Modal from '../components/Modal.jsx'
import ConfirmDialog from '../components/ConfirmDialog.jsx'
import { ProgressBar } from '../components/ProgressBar.jsx'
import { FullSpinner, EmptyState } from '../components/Feedback.jsx'
import { formatCurrency, formatDate } from '../utils/format.js'

export default function SavingsGoals() {
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
    try { const res = await api.get('/goals'); setRows(res.data) }
    catch (e) { toast.error(e.message) } finally { setLoading(false) }
  }, [toast])
  const [tick, setTick] = useState(0)
  useEffect(() => { load() }, [tick, load])
  const refresh = useCallback(() => setTick((t) => t + 1), [])

  const openCreate = () => { setEditing(null); reset({ current_amount: 0 }); setModalOpen(true) }
  const openEdit = (r) => { setEditing(r); reset({ ...r, deadline: r.deadline ? new Date(r.deadline).toISOString().slice(0, 10) : '' }); setModalOpen(true) }

  const onSubmit = async (data) => {
    setSaving(true)
    const payload = { ...data, target_amount: parseFloat(data.target_amount), current_amount: parseFloat(data.current_amount || 0), deadline: data.deadline ? new Date(data.deadline).toISOString() : null }
    try {
      if (editing) await api.patch(`/goals/${editing.id}`, payload)
      else await api.post('/goals', payload)
      toast.success(editing ? 'Goal updated' : 'Goal added'); setModalOpen(false); refresh()
    } catch (e) { toast.error(e.message) }
    finally { setSaving(false) }
  }

  const confirmDelete = async () => {
    try { await api.delete(`/goals/${deleting.id}`); toast.success('Goal deleted'); setDeleting(null); refresh() }
    catch (e) { toast.error(e.message) }
  }

  return (
    <div className="space-y-6">
      <PageHeader title="Savings Goals" subtitle="Set targets and track your progress"
        actions={<Button onClick={openCreate}><FiPlus /> New Goal</Button>} />
      {loading ? <FullSpinner /> : rows.length === 0 ? <EmptyState icon={FiTarget} title="No savings goals yet" />
        : (
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {rows.map((g) => (
              <div key={g.id} className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm dark:border-slate-700 dark:bg-slate-800">
                <div className="flex items-center justify-between">
                  <h4 className="font-bold text-slate-700 dark:text-slate-200">{g.name}</h4>
                  <div className="flex gap-1">
                    <Button size="sm" variant="ghost" onClick={() => openEdit(g)}><FiEdit2 /></Button>
                    <Button size="sm" variant="ghost" className="text-red-600" onClick={() => setDeleting(g)}><FiTrash2 /></Button>
                  </div>
                </div>
                <div className="mt-3 flex items-end justify-between">
                  <span className="text-2xl font-extrabold text-primary">{formatCurrency(g.current_amount, currency)}</span>
                  <span className="text-sm text-slate-400">/ {formatCurrency(g.target_amount, currency)}</span>
                </div>
                <ProgressBar value={g.progress_percent} className="mt-3" color={g.progress_percent >= 100 ? 'bg-green-500' : 'bg-primary'} />
                <div className="mt-2 flex justify-between text-xs text-slate-400">
                  <span>{g.progress_percent.toFixed(1)}% complete</span>
                  <span>{g.deadline ? `By ${formatDate(g.deadline)}` : 'No deadline'}</span>
                </div>
              </div>
            ))}
          </div>
        )}

      <Modal open={modalOpen} onClose={() => setModalOpen(false)} title={editing ? 'Edit Goal' : 'New Savings Goal'} footer={
        <>
          <Button variant="outline" onClick={() => setModalOpen(false)}>Cancel</Button>
          <Button onClick={handleSubmit(onSubmit)} disabled={saving}>{saving ? 'Saving…' : 'Save'}</Button>
        </>
      }>
        <form className="space-y-4">
          <Input label="Goal Name" placeholder="e.g. Buy a Laptop" {...register('name', { required: 'Required' })} error={errors.name?.message} />
          <Input label="Target Amount" type="number" step="0.01" {...register('target_amount', { required: true, min: 1 })} error={errors.target_amount?.message} />
          <Input label="Current Saved Amount" type="number" step="0.01" {...register('current_amount')} />
          <Input label="Deadline (optional)" type="date" {...register('deadline')} />
        </form>
      </Modal>
      <ConfirmDialog open={!!deleting} message="Delete this savings goal?" onConfirm={confirmDelete} onCancel={() => setDeleting(null)} confirmLabel="Delete" />
    </div>
  )
}
