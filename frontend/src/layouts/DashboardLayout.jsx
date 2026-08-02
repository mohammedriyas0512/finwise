import { NavLink, useNavigate } from 'react-router-dom'
import { FiGrid, FiTrendingUp, FiCreditCard, FiPieChart, FiTarget, FiDollarSign, FiRepeat, FiFileText, FiHeart, FiBell, FiUser, FiDownload, FiSearch, FiShield, FiLogOut, FiSun, FiMoon, FiMenu, FiX } from 'react-icons/fi'
import { useAuth } from '../context/AuthContext.jsx'
import { useTheme } from '../context/ThemeContext.jsx'
import { useEffect, useState } from 'react'
import api from '../services/api.js'
import { useToast } from '../context/ToastContext.jsx'

const NAV = [
  { to: '/dashboard', label: 'Dashboard', icon: FiGrid },
  { to: '/income', label: 'Income', icon: FiTrendingUp },
  { to: '/expenses', label: 'Expenses', icon: FiCreditCard },
  { to: '/emi', label: 'EMI Calculator', icon: FiPieChart },
  { to: '/loans', label: 'Loan Calculator', icon: FiPieChart },
  { to: '/debts', label: 'Debt Tracker', icon: FiCreditCard },
  { to: '/goals', label: 'Savings Goals', icon: FiTarget },
  { to: '/budgets', label: 'Budget Planner', icon: FiDollarSign },
  { to: '/bills', label: 'Recurring', icon: FiRepeat },
  { to: '/reports', label: 'Reports', icon: FiFileText },
  { to: '/charts', label: 'Charts', icon: FiPieChart },
  { to: '/health', label: 'Financial Health', icon: FiHeart },
  { to: '/search', label: 'Search', icon: FiSearch },
  { to: '/notifications', label: 'Notifications', icon: FiBell },
  { to: '/profile', label: 'Profile', icon: FiUser },
  { to: '/export', label: 'Export', icon: FiDownload },
]

const ADMIN_NAV = { to: '/admin', label: 'Admin Panel', icon: FiShield }

export default function DashboardLayout({ children }) {
  const { user, logout, isAdmin } = useAuth()
  const { theme, toggleTheme } = useTheme()
  const navigate = useNavigate()
  const toast = useToast()
  const [mobileOpen, setMobileOpen] = useState(false)
  const [unread, setUnread] = useState(0)

  useEffect(() => {
    api.get('/notifications?unread_only=true').then((r) => setUnread(r.data.length)).catch(() => {})
  }, [])

  const handleLogout = () => {
    logout()
    toast.success('Logged out')
    navigate('/login')
  }

  const navItems = isAdmin ? [...NAV, ADMIN_NAV] : NAV

  const SidebarContent = (
    <div className="flex h-full flex-col">
      <div className="flex items-center gap-3 px-5 py-5">
        <div className="grid h-10 w-10 place-items-center rounded-xl bg-primary text-white text-xl font-bold">₹</div>
        <div>
          <p className="text-lg font-extrabold text-slate-800 dark:text-white">FinWise</p>
          <p className="text-[11px] text-slate-400">Plan Smart. Spend Wisely.</p>
        </div>
      </div>
      <nav className="flex-1 space-y-1 overflow-y-auto px-3 pb-4">
        {navItems.map((item) => (
          <NavLink key={item.to} to={item.to}
            onClick={() => setMobileOpen(false)}
            className={({ isActive }) =>
              `flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium transition ${
                isActive
                  ? 'bg-primary text-white shadow-sm'
                  : 'text-slate-600 hover:bg-slate-100 dark:text-slate-300 dark:hover:bg-slate-700/60'
              }`}>
            <item.icon size={18} />
            <span>{item.label}</span>
            {item.to === '/notifications' && unread > 0 && (
              <span className="ml-auto rounded-full bg-red-500 px-2 py-0.5 text-xs text-white">{unread}</span>
            )}
          </NavLink>
        ))}
      </nav>
      <div className="border-t border-slate-200 px-4 py-4 dark:border-slate-700">
        <div className="flex items-center gap-3">
          <div className="grid h-9 w-9 place-items-center rounded-full bg-gradient-to-br from-primary to-violet-500 text-sm font-bold text-white">
            {user?.full_name?.charAt(0).toUpperCase() || 'U'}
          </div>
          <div className="min-w-0 flex-1">
            <p className="truncate text-sm font-semibold text-slate-700 dark:text-slate-200">{user?.full_name}</p>
            <p className="truncate text-xs text-slate-400">{user?.role === 'admin' ? 'Administrator' : 'User'}</p>
          </div>
        </div>
      </div>
    </div>
  )

  return (
    <div className="flex h-screen overflow-hidden bg-surface dark:bg-slate-900">
      {/* Desktop sidebar */}
      <aside className="hidden w-64 shrink-0 border-r border-slate-200 bg-white dark:border-slate-700 dark:bg-slate-800 lg:block">
        {SidebarContent}
      </aside>

      {/* Mobile drawer */}
      {mobileOpen && (
        <div className="fixed inset-0 z-50 lg:hidden">
          <div className="absolute inset-0 bg-slate-900/50" onClick={() => setMobileOpen(false)} />
          <aside className="absolute left-0 top-0 h-full w-64 bg-white dark:bg-slate-800">{SidebarContent}</aside>
        </div>
      )}

      {/* Main */}
      <div className="flex flex-1 flex-col overflow-hidden">
        <header className="flex items-center justify-between border-b border-slate-200 bg-white px-4 py-3 dark:border-slate-700 dark:bg-slate-800">
          <button onClick={() => setMobileOpen(true)} className="rounded-lg p-2 text-slate-600 dark:text-slate-300 lg:hidden">
            <FiMenu size={22} />
          </button>
          <div className="hidden flex-1 px-4 sm:block">
            <span className="text-sm text-slate-400">Welcome back, </span>
            <span className="text-sm font-semibold text-slate-700 dark:text-slate-200">{user?.full_name?.split(' ')[0]}</span>
          </div>
          <div className="flex items-center gap-1">
            <button onClick={toggleTheme} className="rounded-lg p-2 text-slate-600 hover:bg-slate-100 dark:text-slate-300 dark:hover:bg-slate-700" title="Toggle theme">
              {theme === 'dark' ? <FiSun size={20} /> : <FiMoon size={20} />}
            </button>
            <button onClick={handleLogout} className="rounded-lg p-2 text-slate-600 hover:bg-slate-100 dark:text-slate-300 dark:hover:bg-slate-700" title="Logout">
              <FiLogOut size={20} />
            </button>
          </div>
        </header>
        <main className="flex-1 overflow-y-auto p-4 sm:p-6">{children}</main>
      </div>
    </div>
  )
}
