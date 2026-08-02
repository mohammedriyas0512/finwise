import { FiHeart, FiShield, FiTrendingUp, FiCreditCard, FiPieChart } from 'react-icons/fi'
import { useFetch } from '../hooks/useFetch.js'
import PageHeader from '../components/PageHeader.jsx'
import { useTheme } from '../context/ThemeContext.jsx'
import { healthColor, ratingColor } from '../utils/format.js'
import { FullSpinner } from '../components/Feedback.jsx'

const ICONS = { 'Savings Rate': FiTrendingUp, 'Expense Control': FiPieChart, 'Debt Load': FiCreditCard, 'EMI Burden': FiCreditCard, 'Budget Discipline': FiShield }

export default function FinancialHealth() {
  const { data, loading } = useFetch('/health')
  const { theme } = useTheme()
  if (loading || !data) return <FullSpinner label="Calculating your score…" />

  return (
    <div className="space-y-6">
      <PageHeader title="Financial Health" subtitle="A 0–100 score based on your savings, debt, expenses & budget discipline" />

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        <div className="flex flex-col items-center justify-center rounded-2xl border border-slate-200 bg-white p-8 text-center shadow-sm dark:border-slate-700 dark:bg-slate-800">
          <div className="relative grid h-40 w-40 place-items-center rounded-full" style={{ background: `conic-gradient(${data.rating === 'Excellent' ? '#16A34A' : data.rating === 'Good' ? '#2563EB' : data.rating === 'Average' ? '#F59E0B' : '#DC2626'} ${data.score * 3.6}deg, #e2e8f0 0deg)` }}>
            <div className="grid h-32 w-32 place-items-center rounded-full bg-white dark:bg-slate-800">
              <div>
                <p className="text-4xl font-extrabold text-slate-800 dark:text-white">{data.score}</p>
                <p className="text-xs text-slate-400">/ 100</p>
              </div>
            </div>
          </div>
          <span className={`mt-4 rounded-full px-4 py-1 text-sm font-bold ${healthColor(data.rating)}`}>{data.rating}</span>
          <p className="mt-2 text-sm text-slate-500">Financial Health Score</p>
        </div>

        <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm dark:border-slate-700 dark:bg-slate-800 lg:col-span-2">
          <h3 className="mb-4 text-base font-bold text-slate-700 dark:text-slate-200">Score Breakdown</h3>
          <div className="space-y-4">
            {data.factors.map((f) => {
              const Icon = ICONS[f.label] || FiHeart
              return (
                <div key={f.label}>
                  <div className="mb-1 flex items-center justify-between text-sm">
                    <span className="flex items-center gap-2 font-medium text-slate-600 dark:text-slate-300"><Icon /> {f.label}</span>
                    <span className="text-slate-400">{f.detail}</span>
                  </div>
                  <div className="h-2.5 w-full overflow-hidden rounded-full bg-slate-200 dark:bg-slate-700">
                    <div className={`h-2.5 rounded-full ${ratingColor(f.score)}`} style={{ width: `${Math.min(100, f.score)}%` }} />
                  </div>
                </div>
              )
            })}
          </div>
          <div className="mt-6 rounded-xl bg-slate-50 p-4 text-sm text-slate-600 dark:bg-slate-700/40 dark:text-slate-300">
            <p className="font-semibold">How to improve:</p>
            <ul className="mt-1 list-inside list-disc space-y-1">
              <li>Increase your savings rate (aim for 20%+ of income).</li>
              <li>Keep expenses below your income.</li>
              <li>Reduce high-interest debt and EMI burden.</li>
              <li>Stay within your monthly budgets.</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  )
}
