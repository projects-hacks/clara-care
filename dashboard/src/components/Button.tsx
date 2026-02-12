'use client'

import { cn } from '@/lib/utils'
import type { ButtonHTMLAttributes, ReactNode } from 'react'

const variants = {
  primary:
    'bg-clara-600 text-white hover:bg-clara-700 active:bg-clara-800 focus:ring-clara-500 disabled:opacity-70',
  secondary:
    'border border-gray-200 bg-white text-gray-700 shadow-card hover:bg-gray-50 focus:ring-gray-400',
  ghost: 'text-gray-700 hover:bg-gray-100 active:bg-gray-200 focus:ring-gray-400',
  destructive: 'bg-red-600 text-white hover:bg-red-700 focus:ring-red-500',
}

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: keyof typeof variants
  leftIcon?: ReactNode
  rightIcon?: ReactNode
  children: ReactNode
  className?: string
}

export default function Button({
  variant = 'primary',
  leftIcon,
  rightIcon,
  children,
  className,
  disabled,
  ...props
}: ButtonProps) {
  return (
    <button
      type="button"
      className={cn(
        'inline-flex min-h-[44px] items-center justify-center gap-2 rounded-xl px-5 py-3 text-body font-medium transition-colors duration-150 focus:outline-none focus:ring-2 focus:ring-offset-2 disabled:pointer-events-none',
        variants[variant],
        className
      )}
      disabled={disabled}
      {...props}
    >
      {leftIcon}
      {children}
      {rightIcon}
    </button>
  )
}
