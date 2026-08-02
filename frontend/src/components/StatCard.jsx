import { FiTrendingUp, FiTrendingDown } from 'react-icons/fi'

// A glassmorphism KPI card with optional icon, trend and currency formatting.
export default function StatCard({ title, value, icon: Icon, accent = 'primary', sub, trend }) {
  const accents = {
    primary: 'from-blue-500 to-blue-600 text-white',
    success: 'from-green-500 to-green-600 text-white',
    danger: 'from-red-500 to-red-600 text-white',
    warning: 'from-amber-500 to-amber-600 text-white',
    purple: 'from-violet-500 to-violet-600 text-white',
  }
  return (
    <div className="glass rounded-2xl p-5 shadow-sm animate-fade-in hover:shadow-md transition">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-sm font-medium text-slate-500 dark:text-slate-400">{title}</p>
          <p className="mt-2 text-2xl font-extrabold text-slate-800 dark:text-white">{value}</p>
          {sub && <p className="mt-1 text-xs text-slate-400">{sub}</p>}
        </div>
        {Icon && (
          <div className={`grid h-11 w-11 place-items-center rounded-xl bg-gradient-to-br ${accents[accent]}`}>
            <Icon size={22} />
          </div>
        )}
      </div>
      {trend !== undefined && (
        <div className={`mt-3 flex items-center gap-1 text-xs font-medium ${trend >= 0 ? 'text-green-600' : 'text-red-600'}`}>
          {trend >= 0 ? <FiTrendingUp /> : <FiTrendingDown />}
          <span>{trend >= 0 ? '+' : ''}{trend}% vs last month</span>
        </div>
      )}
    </div>
  )
}
