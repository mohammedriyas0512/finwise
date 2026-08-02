// Currency + number formatting helpers shared across the app.

export function formatCurrency(value, currency = 'INR') {
  const n = Number(value || 0)
  try {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency,
      maximumFractionDigits: 2,
    }).format(n)
  } catch {
    return `₹${n.toLocaleString('en-IN', { maximumFractionDigits: 2 })}`
  }
}

export function formatNumber(value) {
  return Number(value || 0).toLocaleString('en-IN', { maximumFractionDigits: 2 })
}

export function formatDate(value, withTime = false) {
  if (!value) return '—'
  const d = new Date(value)
  if (isNaN(d)) return '—'
  return d.toLocaleDateString('en-IN', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    ...(withTime ? { hour: '2-digit', minute: '2-digit' } : {}),
  })
}

export function formatPercent(value) {
  return `${Number(value || 0).toFixed(1)}%`
}

// Health rating color mapping (used by score badges + progress bars).
export function healthColor(rating) {
  switch (rating) {
    case 'Excellent':
      return 'text-green-600 bg-green-100 dark:bg-green-900/40 dark:text-green-300'
    case 'Good':
      return 'text-blue-600 bg-blue-100 dark:bg-blue-900/40 dark:text-blue-300'
    case 'Average':
      return 'text-amber-600 bg-amber-100 dark:bg-amber-900/40 dark:text-amber-300'
    default:
      return 'text-red-600 bg-red-100 dark:bg-red-900/40 dark:text-red-300'
  }
}

export function ratingColor(score) {
  if (score >= 80) return 'bg-green-500'
  if (score >= 60) return 'bg-blue-500'
  if (score >= 40) return 'bg-amber-500'
  return 'bg-red-500'
}

export const INCOME_CATEGORIES = [
  'Salary', 'Business', 'Freelancing', 'Investment', 'Rental', 'Gift', 'Other',
]

export const EXPENSE_CATEGORIES = [
  'Food', 'Fuel', 'Rent', 'Electricity', 'Water', 'Internet', 'Education',
  'Medical', 'Travel', 'Entertainment', 'Shopping', 'Insurance', 'Others',
]
