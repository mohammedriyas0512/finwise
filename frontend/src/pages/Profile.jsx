import { useState, useEffect } from 'react'
import { useForm } from 'react-hook-form'
import { FiUser, FiLock, FiTrash2 } from 'react-icons/fi'
import api from '../services/api.js'
import { useToast } from '../context/ToastContext.jsx'
import { useAuth } from '../context/AuthContext.jsx'
import { useTheme } from '../context/ThemeContext.jsx'
import PageHeader from '../components/PageHeader.jsx'
import { Input, Select, Button } from '../components/Form.jsx'
import Modal from '../components/Modal.jsx'
import { InfoBox } from '../components/Feedback.jsx'

export default function Profile() {
  const toast = useToast()
  const { user, updateUser, logout } = useAuth()
  const { setTheme } = useTheme()
  const [tab, setTab] = useState('profile')
  const [saving, setSaving] = useState(false)
  const [pwSaving, setPwSaving] = useState(false)
  const [confirmDel, setConfirmDel] = useState(false)
  const [delPw, setDelPw] = useState('')

  const { register: regP, handleSubmit: subP, reset: resetP } = useForm({ values: { full_name: user?.full_name, phone: user?.phone, currency: user?.currency, language: user?.language, theme: user?.theme } })
  const { register: regW, handleSubmit: subW } = useForm()

  const onProfile = async (data) => {
    setSaving(true)
    try {
      const res = await api.patch('/auth/profile', { full_name: data.full_name, phone: data.phone, currency: data.currency, language: data.language, theme: data.theme })
      updateUser(res.data)
      setTheme(data.theme)
      toast.success('Profile updated')
    } catch (e) { toast.error(e.message) }
    finally { setSaving(false) }
  }

  const onPassword = async (data) => {
    setPwSaving(true)
    try {
      await api.patch('/auth/change-password', { current_password: data.current_password, new_password: data.new_password })
      toast.success('Password changed')
    } catch (e) { toast.error(e.message) }
    finally { setPwSaving(false) }
  }

  const onDelete = async () => {
    try {
      await api.delete('/auth/account', { data: { password: delPw } })
      toast.success('Account deleted')
      logout()
    } catch (e) { toast.error(e.message) }
  }

  return (
    <div className="space-y-6">
      <PageHeader title="Profile & Settings" subtitle="Manage your account, security and preferences" />
      <div className="flex gap-2 border-b border-slate-200 dark:border-slate-700">
        {[{ id: 'profile', label: 'Profile', icon: FiUser }, { id: 'password', label: 'Security', icon: FiLock }].map((t) => (
          <button key={t.id} onClick={() => setTab(t.id)}
            className={`flex items-center gap-2 border-b-2 px-4 py-2 text-sm font-medium ${tab === t.id ? 'border-primary text-primary' : 'border-transparent text-slate-500'}`}>
            <t.icon /> {t.label}
          </button>
        ))}
      </div>

      {tab === 'profile' && (
        <form onSubmit={subP(onProfile)} className="max-w-lg space-y-4 rounded-2xl border border-slate-200 bg-white p-6 shadow-sm dark:border-slate-700 dark:bg-slate-800">
          <div className="flex items-center gap-4">
            <div className="grid h-16 w-16 place-items-center rounded-full bg-gradient-to-br from-primary to-violet-500 text-2xl font-bold text-white">
              {user?.full_name?.charAt(0).toUpperCase()}
            </div>
            <div>
              <p className="text-lg font-bold text-slate-700 dark:text-slate-200">{user?.full_name}</p>
              <p className="text-sm text-slate-400">{user?.email}</p>
            </div>
          </div>
          <Input label="Full Name" {...regP('full_name', { required: true })} />
          <Input label="Phone" {...regP('phone')} />
          <Select label="Currency" {...regP('currency')}>
            <option value="INR">INR (₹)</option>
            <option value="USD">USD ($)</option>
            <option value="EUR">EUR (€)</option>
            <option value="GBP">GBP (£)</option>
          </Select>
          <Select label="Language" {...regP('language')}>
            <option value="en">English</option>
            <option value="hi">Hindi</option>
          </Select>
          <Select label="Theme" {...regP('theme')}>
            <option value="light">Light</option>
            <option value="dark">Dark</option>
          </Select>
          <Button type="submit" disabled={saving}>{saving ? 'Saving…' : 'Save Changes'}</Button>
        </form>
      )}

      {tab === 'password' && (
        <div className="max-w-lg space-y-4">
          <form onSubmit={subW(onPassword)} className="space-y-4 rounded-2xl border border-slate-200 bg-white p-6 shadow-sm dark:border-slate-700 dark:bg-slate-800">
            <h3 className="font-bold text-slate-700 dark:text-slate-200">Change Password</h3>
            <Input label="Current Password" type="password" {...regW('current_password', { required: true })} />
            <Input label="New Password" type="password" {...regW('new_password', { required: true, minLength: 8 })} />
            <Button type="submit" disabled={pwSaving}>{pwSaving ? 'Updating…' : 'Change Password'}</Button>
          </form>

          <div className="rounded-2xl border border-red-200 bg-red-50 p-6 dark:border-red-700 dark:bg-red-900/20">
            <h3 className="flex items-center gap-2 font-bold text-red-700 dark:text-red-300"><FiTrash2 /> Danger Zone</h3>
            <p className="mt-2 text-sm text-red-600 dark:text-red-300">Permanently delete your account and all associated data. This cannot be undone.</p>
            <Button variant="danger" className="mt-3" onClick={() => setConfirmDel(true)}><FiTrash2 /> Delete Account</Button>
          </div>
        </div>
      )}

      <Modal open={confirmDel} onClose={() => setConfirmDel(false)} title="Delete account?" footer={
        <>
          <Button variant="outline" onClick={() => setConfirmDel(false)}>Cancel</Button>
          <Button variant="danger" onClick={onDelete} disabled={!delPw}>Delete Account</Button>
        </>
      }>
        <p className="text-sm text-slate-600 dark:text-slate-300">All your data will be permanently removed. This cannot be undone.</p>
        <Input type="password" placeholder="Type your password to confirm" value={delPw} onChange={(e) => setDelPw(e.target.value)} className="mt-3" />
      </Modal>
    </div>
  )
}