import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import { FiMail, FiLock, FiLogIn } from 'react-icons/fi'
import { useAuth } from '../../context/AuthContext.jsx'
import { useToast } from '../../context/ToastContext.jsx'
import { Input, Button } from '../../components/Form.jsx'

export default function Login() {
  const { login } = useAuth()
  const toast = useToast()
  const navigate = useNavigate()
  const { register, handleSubmit, formState: { errors, isSubmitting } } = useForm()
  const [showPassword, setShowPassword] = useState(false)

  const onSubmit = async (data) => {
    try {
      const user = await login(data.email, data.password)
      toast.success('Welcome back!')
      navigate(user.role === 'admin' ? '/admin' : '/dashboard')
    } catch (err) {
      toast.error(err.message)
    }
  }

  return (
    <AuthShell title="Sign in to FinWise" subtitle="Plan Smart. Spend Wisely. Achieve Financial Freedom.">
      <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
        <Input label="Email" type="email" placeholder="you@example.com"
          icon={<FiMail />}
          {...register('email', { required: 'Email is required' })} error={errors.email?.message} />
        <div className="relative">
          <Input label="Password" type={showPassword ? 'text' : 'password'} placeholder="••••••••"
            {...register('password', { required: 'Password is required' })} error={errors.password?.message} />
          <button type="button" onClick={() => setShowPassword((s) => !s)}
            className="absolute right-3 top-9 text-xs text-primary font-medium">{showPassword ? 'Hide' : 'Show'}</button>
        </div>
        <div className="flex justify-end">
          <Link to="/forgot-password" className="text-sm font-medium text-primary hover:underline">Forgot password?</Link>
        </div>
        <Button type="submit" disabled={isSubmitting} className="w-full">
          <FiLogIn /> {isSubmitting ? 'Signing in…' : 'Sign In'}
        </Button>
      </form>
      <p className="mt-6 text-center text-sm text-slate-500">
        Don't have an account?{' '}
        <Link to="/register" className="font-semibold text-primary hover:underline">Create one</Link>
      </p>
    </AuthShell>
  )
}

export function AuthShell({ title, subtitle, children }) {
  return (
    <div className="flex min-h-screen items-center justify-center bg-gradient-to-br from-blue-50 via-slate-50 to-violet-50 p-4 dark:from-slate-900 dark:via-slate-900 dark:to-slate-800">
      <div className="w-full max-w-md animate-fade-in">
        <div className="mb-6 text-center">
          <div className="mx-auto mb-3 grid h-14 w-14 place-items-center rounded-2xl bg-primary text-2xl font-extrabold text-white shadow-lg">₹</div>
          <h1 className="text-2xl font-extrabold text-slate-800 dark:text-white">{title}</h1>
          {subtitle && <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">{subtitle}</p>}
        </div>
        <div className="glass rounded-3xl p-7 shadow-xl">{children}</div>
      </div>
    </div>
  )
}
