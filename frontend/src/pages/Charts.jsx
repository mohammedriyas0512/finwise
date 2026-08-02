import { useState, useEffect } from 'react'
import { PieChart, BarChart, LineChart, AreaChart } from '../components/Charts.jsx'
import { useFetch } from '../hooks/useFetch.js'
import { useTheme } from '../context/ThemeContext.jsx'
import PageHeader from '../components/PageHeader.jsx'
import { Select } from '../components/Form.jsx'
import { FullSpinner, EmptyState } from '../components/Feedback.jsx'
import { FiPieChart } from 'react-icons/fi'

export default function Charts() {
  const { theme } = useTheme()
  const dark = theme === 'dark'
  const { data: expense, loading: l1 } = useFetch('/charts/expense-breakdown')
  const { data: income, loading: l2 } = useFetch('/charts/income-breakdown')
  const { data: monthly } = useFetch('/charts/monthly-analysis?months=12')
  const { data: savings } = useFetch('/charts/savings-trend?months=12')

  if (l1 || l2) return <FullSpinner label="Loading charts…" />

  const hasData = expense?.labels?.length || income?.labels?.length

  return (
    <div className="space-y-6">
      <PageHeader title="Charts & Analytics" subtitle="Visualise your income, expenses and savings" />
      {!hasData ? <EmptyState icon={FiPieChart} title="No data to chart yet" description="Add income and expenses to see insights." />
        : (
          <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
            {expense?.labels?.length > 0 && <PieChart labels={expense.labels} values={expense.values} title="Expense Distribution" />}
            {income?.labels?.length > 0 && <PieChart labels={income.labels} values={income.values} title="Income Sources" />}
            {monthly && <BarChart labels={monthly.labels} data={monthly.expense} label="Expense" title="Monthly Expense Analysis" dark={dark} />}
            {monthly && <BarChart labels={monthly.labels} data={monthly.income} label="Income" title="Monthly Income Analysis" dark={dark} />}
            {monthly && (
              <LineChart title="Income vs Expense" dark={dark} labels={monthly.labels}
                datasets={[
                  { label: 'Income', data: monthly.income, borderColor: '#16A34A', backgroundColor: 'rgba(22,163,74,0.1)', fill: true, tension: 0.35 },
                  { label: 'Expense', data: monthly.expense, borderColor: '#DC2626', backgroundColor: 'rgba(220,38,38,0.1)', fill: true, tension: 0.35 },
                ]} />
            )}
            {savings && <AreaChart labels={savings.labels} data={savings.savings} label="Cumulative Savings" title="Savings Trend" dark={dark} />}
          </div>
        )}
    </div>
  )
}
