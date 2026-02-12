'use client'

import { AlertCircle } from 'lucide-react'
import Button from './Button'

interface ErrorStateProps {
  message: string
  onRetry?: () => void
}

export default function ErrorState({ message, onRetry }: ErrorStateProps) {
  return (
    <div
      className="flex flex-col items-center justify-center rounded-xl border border-red-100 bg-red-50/50 px-6 py-10 text-center"
      role="alert"
    >
      <div className="mb-3 flex h-12 w-12 items-center justify-center rounded-full bg-red-100">
        <AlertCircle className="h-6 w-6 text-red-600" strokeWidth={1.5} />
      </div>
      <p className="mb-4 max-w-sm text-body text-red-800">{message}</p>
      {onRetry && (
        <Button variant="secondary" onClick={onRetry}>
          Retry
        </Button>
      )}
    </div>
  )
}
