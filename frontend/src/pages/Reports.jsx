import { useState } from 'react'
import { FiFileText, FiDownload } from 'react-icons/fi'
import api from '../services/api.js'
import { useToast } from '../context/ToastContext.jsx'
import { useAuth } from '../context/AuthContext.jsx'
import PageHeader from '../components/PageHeader.jsx'
import { Select, Button } from '../components/Form.jsx'
import { FullSpinner } from '../components/Feedback.jsx'

const TYPES = [
  { value: 'daily', label: 'Daily Report' },
  { value: 'weekly', label: 'Weekly Report' },
  { value: 'monthly', label: 'Monthly Report' },
  { value: 'yearly', label: 'Yearly Report' },
  { value: 'income', label: 'Income Report' },
  { value: 'expense', label: 'Expense Report' },
  { value: 'savings', label: 'Savings Report' },
  { value: 'debt', label: 'Debt Report' },
  { value: 'budget', label: 'Budget Report' },
]

export default function Reports() {
  const toast = useToast()
  const { user } = useAuth()
  const [type, setType] = useState('monthly')
  const [format, setFormat] = useState('pdf')
  const [preview, setPreview] = useState(null)
  const [loading, setLoading] = useState(false)

  const loadPreview = async () => {
    setLoading(true)
    try {
      const res = await api.get(`/reports/preview?report_type=${type}`)
      setPreview(res.data)
    } catch (e) { toast.error(e.message) }
    finally { setLoading(false) }
  }

  const generate = async () => {
    try {
      const res = await api.post('/reports/generate', { report_type: type, format }, { responseType: 'blob' })
      const url = window.URL.createObjectURL(new Blob([res.data]))
      const a = document.createElement('a')
      a.href = url
      a.download = `${type}_report.${format}`
      a.click()
      window.URL.revokeObjectURL(url)
      toast.success(`Report downloaded (${format.toUpperCase()})`)
    } catch (e) { toast.error(e.message) }
  }

  return (
    <div className="space-y-6">
      <PageHeader title="Reports" subtitle="Generate daily, weekly, monthly & category reports" />

      <div className="flex flex-wrap items-end gap-3 rounded-2xl border border-slate-200 bg-white p-5 shadow-sm dark:border-slate-700 dark:bg-slate-800">
        <Select label="Report Type" value={type} onChange={(e) => setType(e.target.value)} className="sm:w-52">
          {TYPES.map((t) => <option key={t.value} value={t.value}>{t.label}</option>)}
        </Select>
        <Select label="Format" value={format} onChange={(e) => setFormat(e.target.value)} className="sm:w-40">
          <option value="pdf">PDF</option>
          <option value="excel">Excel</option>
          <option value="csv">CSV</option>
        </Select>
        <Button variant="outline" onClick={loadPreview}><FiFileText /> Preview</Button>
        <Button onClick={generate}><FiDownload /> Generate & Download</Button>
      </div>

      {loading && <FullSpinner label="Generating preview…" />}
      {preview && !loading && (
        <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm dark:border-slate-700 dark:bg-slate-800">
          <div className="mb-4 flex flex-wrap gap-4">
            {preview.summary.map((s) => (
              <div key={s[0]} className="rounded-xl bg-slate-50 px-4 py-2 dark:bg-slate-700/40">
                <p className="text-xs text-slate-400">{s[0]}</p>
                <p className="font-bold text-slate-700 dark:text-slate-200">{s[1]}</p>
              </div>
            ))}
          </div>
          <p className="mb-2 text-sm text-slate-500">{preview.count} transactions in this report</p>
          <div className="max-h-80 overflow-auto rounded-xl">
            <table className="w-full text-left text-sm">
              <thead className="sticky top-0 bg-slate-50 text-xs uppercase text-slate-500 dark:bg-slate-900/60">
                <tr><th className="px-3 py-2">Date</th><th className="px-3 py-2">Type</th><th className="px-3 py-2">Category</th><th className="px-3 py-2">Amount</th></tr>
              </thead>
              <tbody className="divide-y divide-slate-100 dark:divide-slate-700">
                {preview.rows.slice(0, 50).map((r, i) => (
                  <tr key={i}>
                    <td className="px-3 py-1.5">{r.date}</td>
                    <td className="px-3 py-1.5">{r.type}</td>
                    <td className="px-3 py-1.5">{r.category}</td>
                    <td className="px-3 py-1.5">{r.amount}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  )
}
