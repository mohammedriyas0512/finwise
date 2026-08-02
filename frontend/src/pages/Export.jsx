import { useState } from 'react'
import { FiDownload, FiFileText, FiTable, FiFile } from 'react-icons/fi'
import api from '../services/api.js'
import { useToast } from '../context/ToastContext.jsx'
import PageHeader from '../components/PageHeader.jsx'
import { Select, Button } from '../components/Form.jsx'

const REPORTS = [
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

function Exporter({ type, label, icon: Icon }) {
  const toast = useToast()
  const [format, setFormat] = useState('pdf')
  const [busy, setBusy] = useState(false)
  const download = async () => {
    setBusy(true)
    try {
      const res = await api.post('/reports/generate', { report_type: type, format }, { responseType: 'blob' })
      const url = window.URL.createObjectURL(new Blob([res.data]))
      const a = document.createElement('a')
      a.href = url; a.download = `${type}_report.${format}`; a.click()
      window.URL.revokeObjectURL(url)
      toast.success(`${label} exported (${format.toUpperCase()})`)
    } catch (e) { toast.error(e.message) }
    finally { setBusy(false) }
  }
  return (
    <div className="flex items-center justify-between rounded-xl border border-slate-200 bg-white p-4 dark:border-slate-700 dark:bg-slate-800">
      <div className="flex items-center gap-3">
        <div className="grid h-10 w-10 place-items-center rounded-xl bg-primary/10 text-primary"><Icon size={20} /></div>
        <span className="font-medium text-slate-700 dark:text-slate-200">{label}</span>
      </div>
      <div className="flex items-center gap-2">
        <Select value={format} onChange={(e) => setFormat(e.target.value)} className="w-24">
          <option value="pdf">PDF</option>
          <option value="excel">Excel</option>
          <option value="csv">CSV</option>
        </Select>
        <Button onClick={download} disabled={busy}><FiDownload /> {busy ? '…' : 'Export'}</Button>
      </div>
    </div>
  )
}

export default function ExportCenter() {
  return (
    <div className="space-y-6">
      <PageHeader title="Export Center" subtitle="Download your financial data as PDF, Excel or CSV" />
      <div className="grid grid-cols-1 gap-3 md:grid-cols-2">
        <Exporter type="monthly" label="Monthly Report" icon={FiFileText} />
        <Exporter type="yearly" label="Yearly Report" icon={FiFileText} />
        <Exporter type="income" label="Income Report" icon={FiTable} />
        <Exporter type="expense" label="Expense Report" icon={FiTable} />
        <Exporter type="savings" label="Savings Report" icon={FiFile} />
        <Exporter type="debt" label="Debt Report" icon={FiFile} />
        <Exporter type="budget" label="Budget Report" icon={FiFile} />
        <Exporter type="daily" label="Daily Report" icon={FiFileText} />
        <Exporter type="weekly" label="Weekly Report" icon={FiFileText} />
      </div>
    </div>
  )
}
