import { useState } from 'react'
import { Link } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import { FiMail, FiCheckCircle } from 'react-icons/fi'
import api from '../../services/api.js'
import { useToast } from '../../context/ToastContext.jsx'
import { AuthShell } from './Login.jsx'
import { Input, Button } from '../../components/Form.jsx'

export default function ForgotPassword() {
  const toast = useToast()
  const { register, handleSubmit, formState: { errors, isSubmitting } } = useForm()
  const [done, setDone] = useState(false)

  const onSubmit = async (data) => {
    try {
      await api.post('/auth/forgot-password', { email: data.email })
      setDone(true)
      toast.success('If the account exists, a reset link has been sent.')
    } catch (err) {
      toast.error(err.message)
    }
  }

  return (
    <AuthShell title="Reset password" subtitle="Enter your email and we'll send reset instructions.">
      {done ? (
        <div className="flex flex-col items-center py-6 text-center">
          <FiCheckCircle size={48} className="text-green-500" />
          <p className="mt-3 text-slate-600 dark:text-slate-300">Check your inbox for the next steps.</p>
          <Link to="/login" className="mt-4 font-semibold text-primary hover:underline">Back to login</Link>
        </div>
      ) : (
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          <Input label="Email" type="email" placeholder="you@example.com"
            {...register('email', { required: 'Email is required' })} error={errors.email?.message} />
          <Button type="submit" disabled={isSubmitting} className="w-full">
            {isSubmitting ? 'Sending…' : 'Send reset link'}
          </Button>
        </form>
      )}
      <p className="mt-6 text-center text-sm text-slate-500">
        Remembered it?{' '}
        <Link to="/login" className="font-semibold text-primary hover:underline">Sign in</Link>
      </p>
    </AuthShell>
  )
}
