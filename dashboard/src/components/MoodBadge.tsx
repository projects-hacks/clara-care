import { cn, moodEmoji, moodColor, moodLabel } from '@/lib/utils'

interface MoodBadgeProps {
  mood: string
  size?: 'sm' | 'md'
}

export default function MoodBadge({ mood, size = 'sm' }: MoodBadgeProps) {
  return (
    <span
      className={cn(
        'inline-flex items-center gap-1 rounded-full font-medium',
        moodColor(mood),
        size === 'sm' ? 'px-2 py-0.5 text-xs' : 'px-3 py-1 text-sm'
      )}
    >
      <span aria-hidden="true">{moodEmoji(mood)}</span>
      <span>{moodLabel(mood)}</span>
    </span>
  )
}
