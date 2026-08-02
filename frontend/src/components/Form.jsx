import { forwardRef } from 'react'

const baseInput =
  'w-full rounded-xl border border-slate-300 bg-white px-3.5 py-2.5 text-sm text-slate-800 outline-none transition focus:border-primary focus:ring-2 focus:ring-primary/20 dark:border-slate-600 dark:bg-slate-700 dark:text-white'

export const Input = forwardRef(function Input({ label, error, className = '', ...props }, ref) {
  return (
    <div className={className}>
      {label && <label className="mb-1 block text-sm font-medium text-slate-600 dark:text-slate-300">{label}</label>}
      <input ref={ref} className={`${baseInput} ${error ? 'border-red-500 focus:ring-red-200' : ''}`} {...props} />
      {error && <p className="mt-1 text-xs text-red-500">{error}</p>}
    </div>
  )
})

export const Select = forwardRef(function Select({ label, error, className = '', children, ...props }, ref) {
  return (
    <div className={className}>
      {label && <label className="mb-1 block text-sm font-medium text-slate-600 dark:text-slate-300">{label}</label>}
      <select ref={ref} className={`${baseInput} ${error ? 'border-red-500' : ''}`} {...props}>
        {children}
      </select>
      {error && <p className="mt-1 text-xs text-red-500">{error}</p>}
    </div>
  )
})

export const Textarea = forwardRef(function Textarea({ label, error, className = '', ...props }, ref) {
  return (
    <div className={className}>
      {label && <label className="mb-1 block text-sm font-medium text-slate-600 dark:text-slate-300">{label}</label>}
      <textarea ref={ref} className={`${baseInput} ${error ? 'border-red-500' : ''}`} rows={3} {...props} />
      {error && <p className="mt-1 text-xs text-red-500">{error}</p>}
    </div>
  )
})

export function Button({ variant = 'primary', size = 'md', className = '', children, ...props }) {
  const variants = {
    primary: 'bg-primary text-white hover:bg-blue-700',
    success: 'bg-success text-white hover:bg-green-700',
    danger: 'bg-danger text-white hover:bg-red-700',
    warning: 'bg-warning text-white hover:bg-amber-600',
    outline: 'border border-slate-300 text-slate-700 hover:bg-slate-100 dark:border-slate-600 dark:text-slate-200 dark:hover:bg-slate-700',
    ghost: 'text-slate-600 hover:bg-slate-100 dark:text-slate-300 dark:hover:bg-slate-700',
  }
  const sizes = { sm: 'px-3 py-1.5 text-xs', md: 'px-4 py-2.5 text-sm', lg: 'px-6 py-3 text-base' }
  return (
    <button className={`inline-flex items-center justify-center gap-2 rounded-xl font-semibold transition disabled:cursor-not-allowed disabled:opacity-60 ${variants[variant]} ${sizes[size]} ${className}`} {...props}>
      {children}
    </button>
  )
}
