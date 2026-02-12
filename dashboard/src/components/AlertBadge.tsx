import { cn, severityColor } from '@/lib/utils'

interface AlertBadgeProps {
  severity: 'low' | 'medium' | 'high'
  className?: string
}

export default function AlertBadge({ severity, className }: AlertBadgeProps) {
  return (
    <span
      className={cn(
        'inline-flex items-center rounded-full px-2 py-0.5 text-[10px] font-semibold uppercase tracking-wide',
        severityColor(severity),
        className
      )}
    >
      {severity}
    </span>
  )
}
