import { Chart as ChartJS, ArcElement, Tooltip, Legend, CategoryScale, LinearScale, PointElement, LineElement, BarElement, Filler } from 'chart.js'
import { Pie, Bar, Line } from 'react-chartjs-2'

ChartJS.register(ArcElement, Tooltip, Legend, CategoryScale, LinearScale, PointElement, LineElement, BarElement, Filler)

const PALETTE = ['#2563EB', '#16A34A', '#DC2626', '#F59E0B', '#8B5CF6', '#06B6D4', '#EC4899', '#84CC16', '#F97316', '#6366F1', '#14B8A6', '#EF4444', '#A855F7']

function gridColor(dark) { return dark ? 'rgba(148,163,184,0.15)' : 'rgba(15,23,42,0.06)' }
function tickColor(dark) { return dark ? '#94A3B8' : '#475569' }

export function PieChart({ labels, values, title }) {
  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm dark:border-slate-700 dark:bg-slate-800">
      {title && <h3 className="mb-3 text-base font-bold text-slate-700 dark:text-slate-200">{title}</h3>}
      <div style={{ height: 280 }}>
        <Pie data={{ labels: labels || [], datasets: [{ data: values || [], backgroundColor: PALETTE, borderWidth: 2, borderColor: '#fff' }] }}
          options={{ responsive: true, maintainAspectRatio: false, plugins: { legend: { position: 'right' } } }} />
      </div>
    </div>
  )
}

export function BarChart({ labels, data, label = 'Amount', title, dark = false }) {
  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm dark:border-slate-700 dark:bg-slate-800">
      {title && <h3 className="mb-3 text-base font-bold text-slate-700 dark:text-slate-200">{title}</h3>}
      <div style={{ height: 280 }}>
        <Bar data={{ labels, datasets: [{ label, data, backgroundColor: '#2563EB', borderRadius: 6 }] }}
          options={{ responsive: true, maintainAspectRatio: false,
            scales: { x: { grid: { color: gridColor(dark) }, ticks: { color: tickColor(dark) } },
              y: { grid: { color: gridColor(dark) }, ticks: { color: tickColor(dark) } } } }} />
      </div>
    </div>
  )
}

export function LineChart({ labels, datasets, title, dark = false }) {
  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm dark:border-slate-700 dark:bg-slate-800">
      {title && <h3 className="mb-3 text-base font-bold text-slate-700 dark:text-slate-200">{title}</h3>}
      <div style={{ height: 280 }}>
        <Line data={{ labels, datasets }} options={{ responsive: true, maintainAspectRatio: false,
          plugins: { legend: { labels: { color: tickColor(dark) } } },
          scales: { x: { grid: { color: gridColor(dark) }, ticks: { color: tickColor(dark) } },
            y: { grid: { color: gridColor(dark) }, ticks: { color: tickColor(dark) } } },
          interaction: { mode: 'index', intersect: false } }} />
      </div>
    </div>
  )
}

export function AreaChart({ labels, data, label = 'Amount', title, dark = false }) {
  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm dark:border-slate-700 dark:bg-slate-800">
      {title && <h3 className="mb-3 text-base font-bold text-slate-700 dark:text-slate-200">{title}</h3>}
      <div style={{ height: 280 }}>
        <Line data={{ labels, datasets: [{ label, data, borderColor: '#2563EB', backgroundColor: 'rgba(37,99,235,0.15)', fill: true, tension: 0.35, pointRadius: 3 }] }}
          options={{ responsive: true, maintainAspectRatio: false,
            scales: { x: { grid: { color: gridColor(dark) }, ticks: { color: tickColor(dark) } },
              y: { grid: { color: gridColor(dark) }, ticks: { color: tickColor(dark) } } } }} />
      </div>
    </div>
  )
}

export { PALETTE }
