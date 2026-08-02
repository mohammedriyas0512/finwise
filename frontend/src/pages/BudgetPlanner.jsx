import { useState, useEffect, useCallback } from 'react'
import { useForm } from 'react-hook-form'
import { FiPlus, FiEdit2, FiTrash2, FiDollarSign, FiAlertTriangle } from 'react-icons/fi'
import api from '../services/api.js'
import { useToast } from '../context/ToastContext.jsx'
import { useAuth } from '../context/AuthContext.jsx'
import PageHeader from '../components/PageHeader.jsx'
import { Input, Button } from '../components/Form.jsx'
import Modal from '../components/Modal.jsx'
import ConfirmDialog from '../components/ConfirmDialog.jsx'
import { ProgressBar } from '../components/ProgressBar.jsx'
import { FullSpinner, EmptyState } from '../components/Feedback.jsx'
import { formatCurrency, formatPercent, EXPENSE_CATEGORIES } from '../utils/format.js'

function currentMonth() { return new Date().toISOString().slice(0, 7) }

export default function BudgetPlanner() {
  const toast = useToast()
  const { user } = useAuth()
  const currency = user?.currency || 'INR'
  const [rows, setRows] = useState([])
  const [loading, setLoading] = useState(true)
  const [month, setMonth] = useState(currentMonth())
  const [modalOpen, setModalOpen] = useState(false)
  const [editing, setEditing] = useState(null)
  const [deleting, setDeleting] = useState(null)
  const [saving, setSaving] = useState(false)
  const { register, handleSubmit, reset, formState: { errors } } = useForm()

  const load = useCallback(async () => {
    setLoading(true)
    try { const res = await api.get(`/budgets?month=${month}`); setRows(res.data) }
    catch (e) { toast.error(e.message) } finally { setLoading(false) }
  }, [month, toast])
  const [tick, setTick] = useState(0)
  useEffect(() => { load() }, [tick, load])
  const refresh = useCallback(() => setTick((t) => t + 1), [])

  const openCreate = () => { setEditing(null); reset({ month, limit_amount: '' }); setModalOpen(true) }
  const openEdit = (r) => { setEditing(r); reset({ ...r }); setModalOpen(true) }

  const onSubmit = async (data) => {
    setSaving(true)
    const payload = { month: data.month, category: data.category, limit_amount: parseFloat(data.limit_amount) }
    try {
      if (editing) await api.patch(`/budgets/${editing.id}`, { limit_amount: payload.limit_amount })
      else await api.post('/budgets', payload)
      toast.success(editing ? 'Budget updated' : 'Budget added'); setModalOpen(false); refresh()
    } catch (e) { toast.error(e.message) }
    finally { setSaving(false) }
  }

  const confirmDelete = async () => {
    try { await api.delete(`/budgets/${deleting.id}`); toast.success('Budget removed'); setDeleting(null); refresh() }
    catch (e) { toast.error(e.message) }
  }

  return (
    <div className="space-y-6">
      <PageHeader title="Budget Planner" subtitle="Set category budgets and get alerted when you overspend"
        actions={<Button onClick={openCreate}><FiPlus /> Add Budget</Button>} />
      <Input type="month" value={month} onChange={(e) => setMonth(e.target.value)} className="sm:w-48" label="Month" />

      {loading ? <FullSpinner /> : rows.length === 0 ? <EmptyState icon={FiDollarSign} title="No budgets for this month" />
        : (
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {rows.map((b) => {
              const over = b.usage_percent > 100
              return (
                <div key={b.id} className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm dark:border-slate-700 dark:bg-slate-800">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <h4 className="font-bold text-slate-700 dark:text-slate-200">{b.category}</h4>
                      {over && <FiAlertTriangle className="text-red-500" />}
                    </div>
                    <div className="flex gap-1">
                      <Button size="sm" variant="ghost" onClick={() => openEdit(b)}><FiEdit2 /></Button>
                      <Button size="sm" variant="ghost" className="text-red-600" onClick={() => setDeleting(b)}><FiTrash2 /></Button>
                    </div>
                  </div>
                  <div className="mt-3 flex items-end justify-between">
                    <span className="font-extrabold text-slate-800 dark:text-white">{formatCurrency(b.spent_amount, currency)}</span>
                    <span className="text-sm text-slate-400">/ {formatCurrency(b.limit_amount, currency)}</span>
                  </div>
                  <ProgressBar value={b.usage_percent} color={over ? 'bg-red-500' : b.usage_percent > 80 ? 'bg-amber-500' : 'bg-green-500'} className="mt-2" />
                  <p className={`mt-2 text-xs ${over ? 'font-semibold text-red-500' : 'text-slate-400'}`}>
                    {over ? `Over budget by ${formatCurrency(b.spent_amount - b.limit_amount, currency)}` : `${formatPercent(b.usage_percent)} used · ${formatCurrency(b.remaining, currency)} left`}
                  </p>
                </div>
              )
            })}
          </div>
        )}

      <Modal open={modalOpen} onClose={() => setModalOpen(false)} title={editing ? 'Edit Budget' : 'Add Budget'} footer={
        <>
          <Button variant="outline" onClick={() => setModalOpen(false)}>Cancel</Button>
          <Button onClick={handleSubmit(onSubmit)} disabled={saving}>{saving ? 'Saving…' : 'Save'}</Button>
        </>
      }>
        <form className="space-y-4">
          <Input label="Month" type="month" {...register('month', { required: true })} error={errors.month?.message} />
          <select {...register('category', { required: true })} className="w-full rounded-xl border border-slate-300 bg-white px-3.5 py-2.5 text-sm dark:border-slate-600 dark:bg-slate-700 dark:text-white">
            {EXPENSE_CATEGORIES.map((c) => <option key={c} value={c}>{c}</option>)}
          </select>
          <Input label="Limit Amount" type="number" step="0.01" {...register('limit_amount', { required: true, min: 1 })} error={errors.limit_amount?.message} />
        </form>
      </Modal>
      <ConfirmDialog open={!!deleting} message="Remove this budget?" onConfirm={confirmDelete} onCancel={() => setDeleting(null)} confirmLabel="Remove" />
    </div>
  )
}
