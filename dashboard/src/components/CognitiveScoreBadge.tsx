import { TrendingUp, TrendingDown, Minus } from 'lucide-react'
import { cn, cognitiveScoreBg } from '@/lib/utils'

interface CognitiveScoreBadgeProps {
  score: number
  trend?: 'improving' | 'stable' | 'declining'
}

export default function CognitiveScoreBadge({ score, trend }: CognitiveScoreBadgeProps) {
  const TrendIcon = trend === 'improving' ? TrendingUp : trend === 'declining' ? TrendingDown : Minus

  return (
    <div className="inline-flex items-center gap-1.5">
      <div
        className={cn(
          'flex h-10 w-10 items-center justify-center rounded-full text-sm font-bold',
          cognitiveScoreBg(score)
        )}
        aria-label={`Cognitive score: ${score}`}
      >
        {score}
      </div>
      {trend && (
        <TrendIcon
          className={cn(
            'h-4 w-4',
            trend === 'improving' && 'text-green-500',
            trend === 'stable' && 'text-gray-400',
            trend === 'declining' && 'text-red-500'
          )}
          aria-label={trend}
        />
      )}
    </div>
  )
}
