import { FiAlertCircle, FiCheckCircle, FiInfo, FiLoader } from 'react-icons/fi'

export default function Spinner({ size = 20, className = '' }) {
  return <FiLoader className={`animate-spin ${className}`} size={size} />
}

export function FullSpinner({ label = 'Loading…' }) {
  return (
    <div className="flex flex-col items-center justify-center py-20 text-slate-500 dark:text-slate-400">
      <Spinner size={32} className="text-primary" />
      <p className="mt-3 text-sm">{label}</p>
    </div>
  )
}

// Skeleton block used while data loads.
export function Skeleton({ className = '' }) {
  return <div className={`skeleton rounded-lg ${className}`} />
}

export function EmptyState({ icon: Icon, title, description }) {
  return (
    <div className="flex flex-col items-center justify-center py-16 text-center text-slate-500 dark:text-slate-400">
      {Icon && <Icon size={42} className="mb-3 text-slate-400" />}
      <h3 className="text-lg font-semibold text-slate-700 dark:text-slate-200">{title}</h3>
      {description && <p className="mt-1 max-w-sm text-sm">{description}</p>}
    </div>
  )
}

export function ErrorBox({ message }) {
  return (
    <div className="flex items-center gap-2 rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700 dark:border-red-700 dark:bg-red-900/30 dark:text-red-300">
      <FiAlertCircle /> <span>{message}</span>
    </div>
  )
}

export function SuccessBox({ message }) {
  return (
    <div className="flex items-center gap-2 rounded-xl border border-green-200 bg-green-50 px-4 py-3 text-sm text-green-700 dark:border-green-700 dark:bg-green-900/30 dark:text-green-300">
      <FiCheckCircle /> <span>{message}</span>
    </div>
  )
}

export function InfoBox({ message }) {
  return (
    <div className="flex items-center gap-2 rounded-xl border border-blue-200 bg-blue-50 px-4 py-3 text-sm text-blue-700 dark:border-blue-700 dark:bg-blue-900/30 dark:text-blue-300">
      <FiInfo /> <span>{message}</span>
    </div>
  )
}
