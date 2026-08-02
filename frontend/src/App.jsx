import { Routes, Route, Navigate } from 'react-router-dom'
import ProtectedRoute from './components/ProtectedRoute.jsx'
import DashboardLayout from './layouts/DashboardLayout.jsx'

import Login from './pages/auth/Login.jsx'
import Register from './pages/auth/Register.jsx'
import ForgotPassword from './pages/auth/ForgotPassword.jsx'

import Dashboard from './pages/Dashboard.jsx'
import IncomePage from './pages/Income.jsx'
import ExpensesPage from './pages/Expenses.jsx'
import EmiCalculator from './pages/EmiCalculator.jsx'
import LoanCalculator from './pages/LoanCalculator.jsx'
import DebtTracker from './pages/DebtTracker.jsx'
import SavingsGoals from './pages/SavingsGoals.jsx'
import BudgetPlanner from './pages/BudgetPlanner.jsx'
import RecurringExpenses from './pages/RecurringExpenses.jsx'
import Reports from './pages/Reports.jsx'
import Charts from './pages/Charts.jsx'
import FinancialHealth from './pages/FinancialHealth.jsx'
import GlobalSearch from './pages/GlobalSearch.jsx'
import Notifications from './pages/Notifications.jsx'
import Profile from './pages/Profile.jsx'
import ExportCenter from './pages/Export.jsx'
import AdminPanel from './pages/AdminPanel.jsx'

export default function App() {
  return (
    <Routes>
      {/* Public auth routes */}
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />
      <Route path="/forgot-password" element={<ForgotPassword />} />

      {/* Protected app routes */}
      <Route path="/" element={<ProtectedRoute><DashboardLayout><Dashboard /></DashboardLayout></ProtectedRoute>} />
      <Route path="/dashboard" element={<ProtectedRoute><DashboardLayout><Dashboard /></DashboardLayout></ProtectedRoute>} />
      <Route path="/income" element={<ProtectedRoute><DashboardLayout><IncomePage /></DashboardLayout></ProtectedRoute>} />
      <Route path="/expenses" element={<ProtectedRoute><DashboardLayout><ExpensesPage /></DashboardLayout></ProtectedRoute>} />
      <Route path="/emi" element={<ProtectedRoute><DashboardLayout><EmiCalculator /></DashboardLayout></ProtectedRoute>} />
      <Route path="/loans" element={<ProtectedRoute><DashboardLayout><LoanCalculator /></DashboardLayout></ProtectedRoute>} />
      <Route path="/debts" element={<ProtectedRoute><DashboardLayout><DebtTracker /></DashboardLayout></ProtectedRoute>} />
      <Route path="/goals" element={<ProtectedRoute><DashboardLayout><SavingsGoals /></DashboardLayout></ProtectedRoute>} />
      <Route path="/budgets" element={<ProtectedRoute><DashboardLayout><BudgetPlanner /></DashboardLayout></ProtectedRoute>} />
      <Route path="/bills" element={<ProtectedRoute><DashboardLayout><RecurringExpenses /></DashboardLayout></ProtectedRoute>} />
      <Route path="/reports" element={<ProtectedRoute><DashboardLayout><Reports /></DashboardLayout></ProtectedRoute>} />
      <Route path="/charts" element={<ProtectedRoute><DashboardLayout><Charts /></DashboardLayout></ProtectedRoute>} />
      <Route path="/health" element={<ProtectedRoute><DashboardLayout><FinancialHealth /></DashboardLayout></ProtectedRoute>} />
      <Route path="/search" element={<ProtectedRoute><DashboardLayout><GlobalSearch /></DashboardLayout></ProtectedRoute>} />
      <Route path="/notifications" element={<ProtectedRoute><DashboardLayout><Notifications /></DashboardLayout></ProtectedRoute>} />
      <Route path="/profile" element={<ProtectedRoute><DashboardLayout><Profile /></DashboardLayout></ProtectedRoute>} />
      <Route path="/export" element={<ProtectedRoute><DashboardLayout><ExportCenter /></DashboardLayout></ProtectedRoute>} />
      <Route path="/admin" element={<ProtectedRoute adminOnly><DashboardLayout><AdminPanel /></DashboardLayout></ProtectedRoute>} />

      <Route path="*" element={<Navigate to="/dashboard" replace />} />
    </Routes>
  )
}
