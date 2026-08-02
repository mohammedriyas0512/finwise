import { useState } from 'react'
import { FiPlus, FiTrash2, FiPieChart } from 'react-icons/fi'
import api from '../services/api.js'
import { useToast } from '../context/ToastContext.jsx'
import { useAuth } from '../context/AuthContext.jsx'
import PageHeader from '../components/PageHeader.jsx'
import { Input, Select, Button } from '../components/Form.jsx'
import { BarChart } from '../components/Charts.jsx'
import { formatCurrency } from '../utils/format.js'

const LOAN_TYPES = [
  { value: 'home', label: 'Home Loan' },
  { value: 'car', label: 'Car Loan' },
  { value: 'education', label: 'Education Loan' },
  { value: 'personal', label: 'Personal Loan' },
  { value: 'business', label: 'Business Loan' },
]

function LoanForm({ loan, index, onChange, onRemove }) {
  return (
    <div className="rounded-xl border border-slate-200 p-4 dark:border-slate-700">
      <div className="mb-2 flex items-center justify-between">
        <span className="text-sm font-semibold text-slate-600 dark:text-slate-300">Loan {index + 1}</span>
        <button onClick={onRemove} className="text-red-500 hover:text-red-700"><FiTrash2 size={16} /></button>
      </div>
      <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
        <Select value={loan.type} onChange={(e) => onChange({ ...loan, type: e.target.value })}>
          {LOAN_TYPES.map((t) => <option key={t.value} value={t.value}>{t.label}</option>)}
        </Select>
        <Input type="number" placeholder="Principal" value={loan.principal} onChange={(e) => onChange({ ...loan, principal: e.target.value })} />
        <Input type="number" step="0.01" placeholder="Rate %" value={loan.interest_rate} onChange={(e) => onChange({ ...loan, interest_rate: e.target.value })} />
        <Input type="number" placeholder="Months" value={loan.tenure_months} onChange={(e) => onChange({ ...loan, tenure_months: e.target.value })} />
      </div>
    </div>
  )
}

export default function LoanCalculator() {
  const toast = useToast()
  const { user } = useAuth()
  const currency = user?.currency || 'INR'
  const [loans, setLoans] = useState([{ type: 'home', principal: 5000000, interest_rate: 8.5, tenure_months: 240 }])
  const [comparison, setComparison] = useState(null)
  const [loading, setLoading] = useState(false)

  const updateLoan = (idx, next) => setLoans((ls) => ls.map((l, i) => (i === idx ? next : l)))
  const addLoan = () => setLoans((ls) => [...ls, { type: 'car', principal: 1000000, interest_rate: 9.5, tenure_months: 84 }])
  const removeLoan = (idx) => setLoans((ls) => ls.filter((_, i) => i !== idx))

  const compare = async () => {
    setLoading(true)
    try {
      const payload = loans.map((l, i) => ({
        label: LOAN_TYPES.find((t) => t.value === l.type)?.label || `Loan ${i + 1}`,
        principal: parseFloat(l.principal),
        interest_rate: parseFloat(l.interest_rate),
        tenure_months: parseInt(l.tenure_months),
      }))
      const res = await api.post('/loans/compare', payload)
      setComparison(res.data)
    } catch (e) { toast.error(e.message) }
    finally { setLoading(false) }
  }

  return (
    <div className="space-y-6">
      <PageHeader title="Loan Calculator" subtitle="Compare different loan scenarios side by side" />
      <div className="space-y-3">
        {loans.map((l, i) => (
          <LoanForm key={i} index={i} loan={l} onChange={(n) => updateLoan(i, n)} onRemove={() => removeLoan(i)} />
        ))}
        {loans.length < 4 && (
          <Button variant="outline" onClick={addLoan}><FiPlus /> Add Loan</Button>
        )}
        <Button onClick={compare} disabled={loading || loans.length < 2}><FiPieChart /> Compare Loans</Button>
      </div>

      {comparison && (
        <div className="space-y-4">
          <div className="overflow-x-auto rounded-2xl border border-slate-200 bg-white shadow-sm dark:border-slate-700 dark:bg-slate-800">
            <table className="w-full text-sm">
              <thead className="bg-slate-50 text-xs uppercase text-slate-500 dark:bg-slate-900/40">
                <tr>
                  <th className="px-4 py-3 text-left">Loan</th>
                  <th className="px-4 py-3">Principal</th>
                  <th className="px-4 py-3">Rate</th>
                  <th className="px-4 py-3">Tenure</th>
                  <th className="px-4 py-3">Monthly EMI</th>
                  <th className="px-4 py-3">Total Interest</th>
                  <th className="px-4 py-3">Total Payment</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 dark:divide-slate-700">
                {comparison.map((c, i) => (
                  <tr key={i} className="text-center">
                    <td className="px-4 py-3 text-left font-medium text-slate-700 dark:text-slate-200">{c.label}</td>
                    <td className="px-4 py-3">{formatCurrency(c.principal, currency)}</td>
                    <td className="px-4 py-3">{c.interest_rate}%</td>
                    <td className="px-4 py-3">{c.tenure_months}m</td>
                    <td className="px-4 py-3 font-bold text-primary">{formatCurrency(c.monthly_emi, currency)}</td>
                    <td className="px-4 py-3 text-amber-600">{formatCurrency(c.total_interest, currency)}</td>
                    <td className="px-4 py-3">{formatCurrency(c.total_payment, currency)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <BarChart title="Monthly EMI Comparison" labels={comparison.map((c) => c.label)} data={comparison.map((c) => c.monthly_emi)} />
        </div>
      )}
    </div>
  )
}
