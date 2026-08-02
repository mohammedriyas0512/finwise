import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { FiSliders, FiDownload, FiSave } from 'react-icons/fi'
import api from '../services/api.js'
import { useToast } from '../context/ToastContext.jsx'
import { useAuth } from '../context/AuthContext.jsx'
import PageHeader from '../components/PageHeader.jsx'
import { Input, Button } from '../components/Form.jsx'
import { formatCurrency, formatNumber } from '../utils/format.js'
import { FullSpinner } from '../components/Feedback.jsx'

export default function EmiCalculator() {
  const toast = useToast()
  const { user } = useAuth()
  const currency = user?.currency || 'INR'
  const { register, handleSubmit, watch } = useForm({ defaultValues: { loan_amount: 1000000, interest_rate: 8.5, tenure_months: 120 } })
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [saving, setSaving] = useState(false)

  const onSubmit = async (data) => {
    setLoading(true)
    try {
      const res = await api.post('/emi/calculate', {
        loan_amount: parseFloat(data.loan_amount),
        interest_rate: parseFloat(data.interest_rate),
        tenure_months: parseInt(data.tenure_months),
      })
      setResult(res.data)
    } catch (e) { toast.error(e.message) }
    finally { setLoading(false) }
  }

  const saveCalc = async () => {
    setSaving(true)
    try {
      const values = watch()
      await api.post('/emi/save', {
        loan_amount: parseFloat(values.loan_amount),
        interest_rate: parseFloat(values.interest_rate),
        tenure_months: parseInt(values.tenure_months),
      })
      toast.success('Calculation saved')
    } catch (e) { toast.error(e.message) }
    finally { setSaving(false) }
  }

  const exportPdf = async () => {
    try {
      const values = watch()
      const res = await api.post('/emi/save', {
        loan_amount: parseFloat(values.loan_amount),
        interest_rate: parseFloat(values.interest_rate),
        tenure_months: parseInt(values.tenure_months),
      })
      const id = res.data.id
      window.open(`/api/emi/export/${id}/pdf`, '_blank')
    } catch (e) { toast.error(e.message) }
  }

  const summary = [
    { label: 'Monthly EMI', value: result ? formatCurrency(result.monthly_emi, currency) : '—', color: 'text-primary' },
    { label: 'Total Interest', value: result ? formatCurrency(result.total_interest, currency) : '—', color: 'text-amber-600' },
    { label: 'Total Payment', value: result ? formatCurrency(result.total_payment, currency) : '—', color: 'text-danger' },
  ]

  return (
    <div className="space-y-6">
      <PageHeader title="EMI Calculator" subtitle="Calculate your equated monthly instalment & amortization schedule"
        actions={<><Button variant="outline" onClick={saveCalc} disabled={saving}><FiSave /> Save</Button>
          <Button onClick={exportPdf} disabled={!result}><FiDownload /> Export PDF</Button></>} />

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm dark:border-slate-700 dark:bg-slate-800">
          <h3 className="mb-4 text-base font-bold text-slate-700 dark:text-slate-200">Loan Details</h3>
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
            <Input label="Loan Amount" type="number" step="0.01" {...register('loan_amount', { required: true, min: 1 })} />
            <Input label="Interest Rate (% p.a.)" type="number" step="0.01" {...register('interest_rate', { required: true, min: 0 })} />
            <Input label="Tenure (months)" type="number" {...register('tenure_months', { required: true, min: 1 })} />
            <Button type="submit" disabled={loading} className="w-full"><FiSliders /> {loading ? 'Calculating…' : 'Calculate EMI'}</Button>
          </form>
        </div>

        <div className="lg:col-span-2 space-y-4">
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
            {summary.map((s) => (
              <div key={s.label} className="rounded-2xl border border-slate-200 bg-white p-5 text-center shadow-sm dark:border-slate-700 dark:bg-slate-800">
                <p className="text-xs text-slate-400">{s.label}</p>
                <p className={`mt-1 text-xl font-extrabold ${s.color}`}>{s.value}</p>
              </div>
            ))}
          </div>

          {result && (
            <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm dark:border-slate-700 dark:bg-slate-800">
              <h3 className="mb-3 text-base font-bold text-slate-700 dark:text-slate-200">Amortization Schedule</h3>
              <div className="max-h-96 overflow-auto rounded-xl">
                <table className="w-full text-left text-sm">
                  <thead className="sticky top-0 bg-slate-50 text-xs uppercase text-slate-500 dark:bg-slate-900/60">
                    <tr>
                      <th className="px-3 py-2">#</th><th className="px-3 py-2">Payment</th>
                      <th className="px-3 py-2">Principal</th><th className="px-3 py-2">Interest</th>
                      <th className="px-3 py-2">Balance</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100 dark:divide-slate-700">
                    {result.amortization.map((r) => (
                      <tr key={r.month}>
                        <td className="px-3 py-1.5">{r.month}</td>
                        <td className="px-3 py-1.5">{formatCurrency(r.payment, currency)}</td>
                        <td className="px-3 py-1.5 text-green-600">{formatCurrency(r.principal, currency)}</td>
                        <td className="px-3 py-1.5 text-red-500">{formatCurrency(r.interest, currency)}</td>
                        <td className="px-3 py-1.5">{formatCurrency(r.balance, currency)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
