import { useState, useEffect, useCallback } from 'react'
import { useForm } from 'react-hook-form'
import { FiPlus, FiEdit2, FiTrash2, FiDollarSign, FiList } from 'react-icons/fi'
import api from '../services/api.js'
import { useToast } from '../context/ToastContext.jsx'
import { useAuth } from '../context/AuthContext.jsx'
import PageHeader from '../components/PageHeader.jsx'
import { Input, Select, Button } from '../components/Form.jsx'
import Modal from '../components/Modal.jsx'
import ConfirmDialog from '../components/ConfirmDialog.jsx'
import DataTable from '../components/DataTable.jsx'
import { ProgressBar } from '../components/ProgressBar.jsx'
import { FullSpinner, EmptyState } from '../components/Feedback.jsx'
import { formatCurrency, formatDate } from '../utils/format.js'

const TYPES = [
  { value: 'credit_card', label: 'Credit Card' },
  { value: 'personal_loan', label: 'Personal Loan' },
  { value: 'borrowed', label: 'Borrowed Money' },
  { value: 'bank_loan', label: 'Bank Loan' },
  { value: 'friend_loan', label: 'Friend Loan' },
]

export default function DebtTracker() {
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
    try { const res = await api.get('/debts'); setRows(res.data) }
    catch (e) { toast.error(e.message) } finally { setLoading(false) }
  }, [toast])
  const [tick, setTick] = useState(0)
  useEffect(() => { load() }, [tick, load])
  const refresh = useCallback(() => setTick((t) => t + 1), [])

  const openCreate = () => { setEditing(null); reset({ status: 'active', debt_type: 'credit_card' }); setModalOpen(true) }
  const openEdit = (r) => { setEditing(r); reset({ ...r, due_date: r.due_date ? new Date(r.due_date).toISOString().slice(0, 10) : '' }); setModalOpen(true) }

  const onSubmit = async (data) => {
    setSaving(true)
    const payload = { ...data, total_amount: parseFloat(data.total_amount), remaining_balance: parseFloat(data.remaining_balance), monthly_payment: data.monthly_payment ? parseFloat(data.monthly_payment) : null, due_date: data.due_date ? new Date(data.due_date).toISOString() : null }
    try {
      if (editing) await api.patch(`/debts/${editing.id}`, payload)
      else await api.post('/debts', payload)
      toast.success(editing ? 'Debt updated' : 'Debt added'); setModalOpen(false); refresh()
    } catch (e) { toast.error(e.message) }
    finally { setSaving(false) }
  }

  const confirmDelete = async () => {
    try { await api.delete(`/debts/${deleting.id}`); toast.success('Debt deleted'); setDeleting(null); refresh() }
    catch (e) { toast.error(e.message) }
  }

  // --- Repayments -----------------------------------------------------------
  const [detail, setDetail] = useState(null)      // { ...debt, payments, total_paid }
  const [detailLoading, setDetailLoading] = useState(false)
  const [payAmt, setPayAmt] = useState('')
  const [payNote, setPayNote] = useState('')
  const [paying, setPaying] = useState(false)

  const openDetail = async (d) => {
    setDetail({ ...d, payments: [], total_paid: 0 })
    setPayAmt(''); setPayNote('')
    setDetailLoading(true)
    try { const res = await api.get(`/debts/${d.id}/payments`); setDetail(res.data) }
    catch (e) { toast.error(e.message) } finally { setDetailLoading(false) }
  }

  const onPay = async (e) => {
    e?.preventDefault()
    const amount = parseFloat(payAmt)
    if (!amount || amount <= 0) return toast.error('Enter a valid amount')
    setPaying(true)
    try {
      const res = await api.post(`/debts/${detail.id}/payments`, { amount, note: payNote || null })
      setDetail(res.data)
      setPayAmt(''); setPayNote('')
      toast.success('Payment recorded')
      refresh()
    } catch (e) { toast.error(e.response?.data?.detail || e.message) }
    finally { setPaying(false) }
  }

  const columns = [
    { key: 'name', label: 'Name' },
    { key: 'debt_type', label: 'Type', render: (r) => TYPES.find((t) => t.value === r.debt_type)?.label || r.debt_type },
    { key: 'remaining_balance', label: 'Remaining', render: (r) => <span className="font-semibold text-amber-600">{formatCurrency(r.remaining_balance, currency)}</span> },
    { key: 'monthly_payment', label: 'Monthly', render: (r) => r.monthly_payment ? formatCurrency(r.monthly_payment, currency) : '—' },
    { key: 'due_date', label: 'Due', render: (r) => r.due_date ? formatDate(r.due_date) : '—' },
    { key: 'status', label: 'Status', render: (r) => <span className={`rounded-full px-2 py-0.5 text-xs font-semibold ${r.status === 'paid' ? 'bg-green-100 text-green-700' : r.status === 'overdue' ? 'bg-red-100 text-red-700' : 'bg-blue-100 text-blue-700'}`}>{r.status}</span> },
    { key: 'actions', label: '', render: (r) => (
      <div className="flex justify-end gap-1">
        <Button size="sm" variant="ghost" title="Repayments" onClick={() => openDetail(r)}><FiList /></Button>
        <Button size="sm" variant="ghost" onClick={() => openEdit(r)}><FiEdit2 /></Button>
        <Button size="sm" variant="ghost" className="text-red-600" onClick={() => setDeleting(r)}><FiTrash2 /></Button>
      </div>
    ) },
  ]

  return (
    <div className="space-y-6">
      <PageHeader title="Debt Tracker" subtitle="Monitor credit cards, loans and borrowed money"
        actions={<Button onClick={openCreate}><FiPlus /> Add Debt</Button>} />
      {loading ? <FullSpinner /> : rows.length === 0 ? <EmptyState icon={FiDollarSign} title="No debts tracked" />
        : (
          <>
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
              {rows.map((d) => {
                const pct = d.total_amount ? (1 - d.remaining_balance / d.total_amount) * 100 : 0
                return (
                  <div key={d.id} onClick={() => openDetail(d)} role="button" tabIndex={0}
                    onKeyDown={(e) => { if (e.key === 'Enter') openDetail(d) }}
                    className="cursor-pointer rounded-2xl border border-slate-200 bg-white p-5 shadow-sm transition hover:border-primary hover:shadow-md dark:border-slate-700 dark:bg-slate-800">
                    <div className="flex items-center justify-between">
                      <h4 className="font-bold text-slate-700 dark:text-slate-200">{d.name}</h4>
                      <span className={`rounded-full px-2 py-0.5 text-xs font-semibold ${d.status === 'paid' ? 'bg-green-100 text-green-700' : 'bg-amber-100 text-amber-700'}`}>{d.status}</span>
                    </div>
                    <p className="mt-1 text-sm text-slate-400">{TYPES.find((t) => t.value === d.debt_type)?.label}</p>
                    <div className="mt-3"><ProgressBar value={pct} color={pct > 75 ? 'bg-green-500' : 'bg-amber-500'} /></div>
                    <div className="mt-2 flex justify-between text-sm">
                      <span className="text-slate-500">Paid {pct.toFixed(0)}%</span>
                      <span className="font-semibold">{formatCurrency(d.remaining_balance, currency)} left</span>
                    </div>
                    <p className="mt-2 flex items-center gap-1 text-xs text-primary"><FiList size={12} /> View repayments</p>
                  </div>
                )
              })}
            </div>
            <DataTable columns={columns} rows={rows} />
          </>
        )}

      <Modal open={modalOpen} onClose={() => setModalOpen(false)} title={editing ? 'Edit Debt' : 'Add Debt'} footer={
        <>
          <Button variant="outline" onClick={() => setModalOpen(false)}>Cancel</Button>
          <Button onClick={handleSubmit(onSubmit)} disabled={saving}>{saving ? 'Saving…' : 'Save'}</Button>
        </>
      }>
        <form className="space-y-4">
          <Input label="Name" placeholder="e.g. HDFC Credit Card" {...register('name', { required: 'Required' })} error={errors.name?.message} />
          <Select label="Type" {...register('debt_type', { required: true })} error={errors.debt_type?.message}>
            {TYPES.map((t) => <option key={t.value} value={t.value}>{t.label}</option>)}
          </Select>
          <div className="grid grid-cols-2 gap-3">
            <Input label="Total Amount" type="number" step="0.01" {...register('total_amount', { required: true, min: 0 })} error={errors.total_amount?.message} />
            <Input label="Remaining Balance" type="number" step="0.01" {...register('remaining_balance', { required: true, min: 0 })} error={errors.remaining_balance?.message} />
          </div>
          <div className="grid grid-cols-2 gap-3">
            <Input label="Monthly Payment" type="number" step="0.01" {...register('monthly_payment')} />
            <Input label="Due Date" type="date" {...register('due_date')} />
          </div>
          <Select label="Status" {...register('status')}>
            <option value="active">Active</option>
            <option value="paid">Paid</option>
            <option value="overdue">Overdue</option>
          </Select>
        </form>
      </Modal>
      <Modal open={!!detail} onClose={() => setDetail(null)} title={detail ? `${detail.name} — Repayments` : ''} size="lg">
        {detail && (() => {
          const due = Number(detail.remaining_balance) || 0
          const paid = Number(detail.total_paid) || 0
          const total = Number(detail.total_amount) || 0
          return (
            <div className="space-y-5">
              <div className="grid grid-cols-3 gap-3">
                <div className="rounded-xl bg-slate-100 p-3 text-center dark:bg-slate-700/50">
                  <p className="text-xs text-slate-500 dark:text-slate-400">Total Borrowed</p>
                  <p className="mt-1 font-bold text-slate-700 dark:text-slate-200">{formatCurrency(total, currency)}</p>
                </div>
                <div className="rounded-xl bg-green-100 p-3 text-center dark:bg-green-900/30">
                  <p className="text-xs text-green-700 dark:text-green-300">Total Paid</p>
                  <p className="mt-1 font-bold text-green-700 dark:text-green-300">{formatCurrency(paid, currency)}</p>
                </div>
                <div className="rounded-xl bg-amber-100 p-3 text-center dark:bg-amber-900/30">
                  <p className="text-xs text-amber-700 dark:text-amber-300">Total Due</p>
                  <p className="mt-1 font-bold text-amber-700 dark:text-amber-300">{formatCurrency(due, currency)}</p>
                </div>
              </div>

              {due > 0 ? (
                <form onSubmit={onPay} className="flex flex-wrap items-end gap-3 rounded-xl border border-slate-200 p-3 dark:border-slate-700">
                  <Input label="Repay amount" type="number" step="0.01" min="0" value={payAmt}
                    onChange={(e) => setPayAmt(e.target.value)} className="w-36" />
                  <Input label="Note (optional)" value={payNote} onChange={(e) => setPayNote(e.target.value)} className="flex-1 min-w-[8rem]" />
                  <Button type="submit" disabled={paying}>{paying ? 'Saving…' : 'Add Payment'}</Button>
                </form>
              ) : (
                <div className="rounded-xl bg-green-50 p-3 text-center text-sm font-semibold text-green-700 dark:bg-green-900/20 dark:text-green-300">🎉 Fully paid off</div>
              )}

              <div>
                <h4 className="mb-2 text-sm font-semibold text-slate-600 dark:text-slate-300">Payment History</h4>
                {detailLoading ? <p className="py-4 text-center text-sm text-slate-400">Loading…</p>
                  : detail.payments.length === 0 ? <p className="py-4 text-center text-sm text-slate-400">No payments recorded yet.</p>
                  : (
                    <ul className="divide-y divide-slate-200 dark:divide-slate-700">
                      {detail.payments.map((p) => (
                        <li key={p.id} className="flex items-center justify-between py-2 text-sm">
                          <div>
                            <span className="font-semibold text-green-600">{formatCurrency(p.amount, currency)}</span>
                            {p.note && <span className="ml-2 text-slate-500">— {p.note}</span>}
                          </div>
                          <span className="text-slate-400">{formatDate(p.paid_at)}</span>
                        </li>
                      ))}
                    </ul>
                  )}
              </div>
            </div>
          )
        })()}
      </Modal>

      <ConfirmDialog open={!!deleting} message="Delete this debt record?" onConfirm={confirmDelete} onCancel={() => setDeleting(null)} confirmLabel="Delete" />
    </div>
  )
}
