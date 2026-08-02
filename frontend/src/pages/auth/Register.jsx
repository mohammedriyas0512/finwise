import { useState } from 'react'
import { Link } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import { FiUser, FiMail, FiPhone, FiLock } from 'react-icons/fi'
import { useAuth } from '../../context/AuthContext.jsx'
import { useToast } from '../../context/ToastContext.jsx'
import { AuthShell } from './Login.jsx'
import { Input, Button } from '../../components/Form.jsx'

export default function Register() {
  const { register: registerUser } = useAuth()
  const toast = useToast()
  const { register, handleSubmit, watch, formState: { errors, isSubmitting } } = useForm()
  const password = watch('password')

  const onSubmit = async (data) => {
    try {
      await registerUser({
        full_name: data.full_name,
        email: data.email,
        phone: data.phone,
        password: data.password,
      })
      toast.success('Account created! Please sign in.')
      window.location.href = '/login'
    } catch (err) {
      toast.error(err.message)
    }
  }

  return (
    <AuthShell title="Create your account" subtitle="Start managing your finances in minutes.">
      <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
        <Input label="Full Name" placeholder="Jane Doe" {...register('full_name', { required: 'Name is required' })} error={errors.full_name?.message} />
        <Input label="Email" type="email" placeholder="you@example.com" {...register('email', { required: 'Email is required' })} error={errors.email?.message} />
        <Input label="Phone (optional)" placeholder="+91 98765 43210" {...register('phone')} />
        <Input label="Password" type="password" placeholder="Min 8 characters"
          {...register('password', { required: 'Password is required', minLength: { value: 8, message: 'At least 8 characters' } })}
          error={errors.password?.message} />
        <Input label="Confirm Password" type="password" placeholder="Re-enter password"
          {...register('confirm', { validate: (v) => v === password || 'Passwords do not match' })}
          error={errors.confirm?.message} />
        <Button type="submit" disabled={isSubmitting} className="w-full">
          {isSubmitting ? 'Creating…' : 'Create Account'}
        </Button>
      </form>
      <p className="mt-6 text-center text-sm text-slate-500">
        Already have an account?{' '}
        <Link to="/login" className="font-semibold text-primary hover:underline">Sign in</Link>
      </p>
    </AuthShell>
  )
}
