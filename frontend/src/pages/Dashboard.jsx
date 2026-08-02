import { Link } from 'react-router-dom'
import { FiTrendingUp, FiTrendingDown, FiDollarSign, FiPieChart, FiTarget, FiBell, FiCreditCard, FiActivity } from 'react-icons/fi'
import StatCard from '../components/StatCard.jsx'
import PageHeader from '../components/PageHeader.jsx'
import { PieChart, LineChart, PALETTE } from '../components/Charts.jsx'
import { useFetch } from '../hooks/useFetch.js'
import { useTheme } from '../context/ThemeContext.jsx'
import { formatCurrency, formatDate, formatPercent, healthColor, ratingColor } from '../utils/format.js'
import { Skeleton, FullSpinner } from '../components/Feedback.jsx'

export default function Dashboard() {
  const { data: summary, loading } = useFetch('/dashboard/summary')
  const { data: charts } = useFetch('/charts/expense-breakdown')
  const { data: monthly } = useFetch('/charts/monthly-analysis?months=6')
  const { theme } = useTheme()
  const dark = theme === 'dark'
  const currency = 'INR'

  if (loading || !summary) return <FullSpinner label="Loading your dashboard…" />

  const health = summary.financial_health

  return (
    <div className="space-y-6">
      <PageHeader title="Dashboard" subtitle="Your complete financial snapshot at a glance" />

      {/* KPI cards */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
        <StatCard title="Total Income" value={formatCurrency(summary.total_income, currency)} icon={FiTrendingUp} accent="success" />
        <StatCard title="Total Expense" value={formatCurrency(summary.total_expense, currency)} icon={FiTrendingDown} accent="danger" />
        <StatCard title="Total Savings" value={formatCurrency(summary.total_savings, currency)} icon={FiDollarSign} accent="primary" />
        <StatCard title="Total Debt" value={formatCurrency(summary.total_debt, currency)} icon={FiCreditCard} accent="warning" />
        <StatCard title="Monthly EMI" value={formatCurrency(summary.total_emi, currency)} icon={FiPieChart} accent="purple" />
        <StatCard title="Current Balance" value={formatCurrency(summary.current_balance, currency)} icon={FiActivity} accent="primary" />
        <StatCard title="Savings Goals" value={`${formatCurrency(summary.goals_current, currency)} / ${formatCurrency(summary.goals_target, currency)}`} icon={FiTarget} accent="success" />
        <StatCard title="Monthly Income" value={formatCurrency(summary.monthly_income, currency)} icon={FiTrendingUp} accent="success" sub={`Expense ${formatCurrency(summary.monthly_expense, currency)}`} />
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        {/* Financial health */}
        <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm dark:border-slate-700 dark:bg-slate-800">
          <div className="flex items-center justify-between">
            <h3 className="text-base font-bold text-slate-700 dark:text-slate-200">Financial Health</h3>
            <span className={`rounded-full px-3 py-1 text-xs font-bold ${healthColor(health.rating)}`}>{health.rating}</span>
          </div>
          <div className="mt-4 flex items-end gap-2">
            <span className="text-5xl font-extrabold text-slate-800 dark:text-white">{health.score}</span>
            <span className="mb-1 text-slate-400">/100</span>
          </div>
          <div className="mt-3 h-3 w-full overflow-hidden rounded-full bg-slate-200 dark:bg-slate-700">
            <div className={`h-3 rounded-full ${ratingColor(health.score)}`} style={{ width: `${health.score}%` }} />
          </div>
          <Link to="/health" className="mt-4 inline-block text-sm font-medium text-primary hover:underline">View breakdown →</Link>
        </div>

        {/* Expense breakdown pie */}
        <div className="lg:col-span-2">
          {charts && charts.labels.length > 0 ? (
            <PieChart labels={charts.labels} values={charts.values} title="Expense Breakdown" />
          ) : (
            <div className="grid h-full place-items-center rounded-2xl border border-slate-200 bg-white p-5 text-slate-400 shadow-sm dark:border-slate-700 dark:bg-slate-800">
              No expense data yet
            </div>
          )}
        </div>
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        {/* Income vs Expense */}
        {monthly && (
          <LineChart
            title="Income vs Expense (6 months)"
            dark={dark}
            labels={monthly.labels}
            datasets={[
              { label: 'Income', data: monthly.income, borderColor: '#16A34A', backgroundColor: 'rgba(22,163,74,0.1)', fill: true, tension: 0.35 },
              { label: 'Expense', data: monthly.expense, borderColor: '#DC2626', backgroundColor: 'rgba(220,38,38,0.1)', fill: true, tension: 0.35 },
            ]}
          />
        )}
        {/* Savings goals progress */}
        <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm dark:border-slate-700 dark:bg-slate-800">
          <h3 className="mb-3 text-base font-bold text-slate-700 dark:text-slate-200">Savings Goals Progress</h3>
          <div className="space-y-3">
            {summary.savings_goals.length === 0 && <p className="py-6 text-center text-sm text-slate-400">No goals yet</p>}
            {summary.savings_goals.map((g) => (
              <div key={g.id}>
                <div className="mb-1 flex items-center justify-between text-sm">
                  <span className="font-medium text-slate-600 dark:text-slate-300">{g.name}</span>
                  <span className="text-slate-400">{formatPercent(g.progress_percent)}</span>
                </div>
                <div className="h-2.5 w-full overflow-hidden rounded-full bg-slate-200 dark:bg-slate-700">
                  <div className="h-2.5 rounded-full bg-primary" style={{ width: `${g.progress_percent}%` }} />
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Recent transactions + upcoming */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm dark:border-slate-700 dark:bg-slate-800">
          <div className="mb-3 flex items-center justify-between">
            <h3 className="text-base font-bold text-slate-700 dark:text-slate-200">Recent Transactions</h3>
            <Link to="/search" className="text-sm font-medium text-primary hover:underline">View all</Link>
          </div>
          <div className="space-y-2">
            {summary.recent_transactions.length === 0 && <p className="py-6 text-center text-sm text-slate-400">No transactions yet</p>}
            {summary.recent_transactions.map((t) => (
              <div key={t.id} className="flex items-center justify-between rounded-xl px-2 py-2 hover:bg-slate-50 dark:hover:bg-slate-700/40">
                <div className="flex items-center gap-3">
                  <div className={`grid h-9 w-9 place-items-center rounded-full ${t.type === 'income' ? 'bg-green-100 text-green-600' : 'bg-red-100 text-red-600'} dark:bg-slate-700`}>
                    {t.type === 'income' ? <FiTrendingUp size={16} /> : <FiTrendingDown size={16} />}
                  </div>
                  <div>
                    <p className="text-sm font-medium text-slate-700 dark:text-slate-200">{t.category}</p>
                    <p className="text-xs text-slate-400">{formatDate(t.date)}</p>
                  </div>
                </div>
                <span className={`text-sm font-bold ${t.type === 'income' ? 'text-green-600' : 'text-red-600'}`}>
                  {t.type === 'income' ? '+' : '-'}{formatCurrency(t.amount, currency)}
                </span>
              </div>
            ))}
          </div>
        </div>

        <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm dark:border-slate-700 dark:bg-slate-800">
          <div className="mb-3 flex items-center justify-between">
            <h3 className="text-base font-bold text-slate-700 dark:text-slate-200">Upcoming Dues</h3>
            <Link to="/debts" className="text-sm font-medium text-primary hover:underline">Manage</Link>
          </div>
          <div className="space-y-2">
            {summary.upcoming_debts.length === 0 && <p className="py-6 text-center text-sm text-slate-400">No upcoming dues</p>}
            {summary.upcoming_debts.map((d) => (
              <div key={d.id} className="flex items-center justify-between rounded-xl px-2 py-2 hover:bg-slate-50 dark:hover:bg-slate-700/40">
                <div className="flex items-center gap-3">
                  <div className="grid h-9 w-9 place-items-center rounded-full bg-amber-100 text-amber-600 dark:bg-slate-700"><FiBell size={16} /></div>
                  <div>
                    <p className="text-sm font-medium text-slate-700 dark:text-slate-200">{d.name}</p>
                    <p className="text-xs text-slate-400">Due {formatDate(d.due_date)}</p>
                  </div>
                </div>
                <span className="text-sm font-bold text-amber-600">{formatCurrency(d.remaining_balance, currency)}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}
