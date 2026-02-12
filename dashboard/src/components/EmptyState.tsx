import type { LucideIcon } from 'lucide-react'

interface EmptyStateProps {
  icon: LucideIcon
  title: string
  description: string
}

export default function EmptyState({ icon: Icon, title, description }: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center justify-center px-6 py-16 text-center">
      <Icon className="mb-4 h-12 w-12 text-gray-300" strokeWidth={1.5} />
      <h3 className="mb-1 text-base font-semibold text-gray-700">{title}</h3>
      <p className="max-w-xs text-sm text-gray-400">{description}</p>
    </div>
  )
}
