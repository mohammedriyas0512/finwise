export function ProgressBar({ value, color = 'bg-primary', height = 'h-2.5' }) {
  const pct = Math.min(100, Math.max(0, Number(value) || 0))
  return (
    <div className={`w-full ${height} rounded-full bg-slate-200 dark:bg-slate-700`}>
      <div className={`${height} rounded-full ${color} transition-all duration-500`} style={{ width: `${pct}%` }} />
    </div>
  )
}

export default ProgressBar
