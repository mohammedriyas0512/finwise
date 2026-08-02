import { useState } from 'react'
import Modal from './Modal.jsx'
import { FiAlertTriangle } from 'react-icons/fi'

// Confirmation dialog used before destructive actions.
export default function ConfirmDialog({ open, title = 'Are you sure?', message, onConfirm, onCancel, confirmLabel = 'Delete', loading = false }) {
  return (
    <Modal open={open} onClose={onCancel} title={title} size="sm"
      footer={
        <>
          <button onClick={onCancel} className="rounded-lg px-4 py-2 text-sm font-medium text-slate-600 hover:bg-slate-100 dark:text-slate-300 dark:hover:bg-slate-700">
            Cancel
          </button>
          <button onClick={onConfirm} disabled={loading}
            className="rounded-lg bg-red-600 px-4 py-2 text-sm font-semibold text-white hover:bg-red-700 disabled:opacity-60">
            {loading ? 'Please wait…' : confirmLabel}
          </button>
        </>
      }>
      <div className="flex items-start gap-3">
        <div className="grid h-10 w-10 shrink-0 place-items-center rounded-full bg-red-100 text-red-600 dark:bg-red-900/40">
          <FiAlertTriangle size={20} />
        </div>
        <p className="text-sm text-slate-600 dark:text-slate-300">{message}</p>
      </div>
    </Modal>
  )
}
