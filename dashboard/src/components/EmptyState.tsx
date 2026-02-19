import type { LucideIcon } from 'lucide-react'

interface EmptyStateProps {
  icon: LucideIcon
  title: string
  description: string
}

export default function EmptyState({ icon: Icon, title, description }: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center justify-center px-4 py-12 text-center">
      <div className="mb-4 flex h-14 w-14 items-center justify-center rounded-2xl border border-gray-100 bg-white shadow-sm">
        <Icon className="h-7 w-7 text-gray-400" strokeWidth={1.8} />
      </div>
      <h3 className="mb-1 text-base font-semibold text-gray-800">{title}</h3>
      <p className="max-w-xs text-sm leading-relaxed text-gray-500">{description}</p>
    </div>
  )
}
