'use client'

import { ChevronRight, Clock } from 'lucide-react'
import type { Conversation } from '@/lib/api'
import { formatTimeAgo, formatDuration } from '@/lib/utils'
import MoodBadge from './MoodBadge'

interface ConversationCardProps {
  conversation: Conversation
  onClick?: () => void
}

export default function ConversationCard({ conversation, onClick }: ConversationCardProps) {
  const summary =
    conversation.summary.length > 80
      ? conversation.summary.slice(0, 80) + '…'
      : conversation.summary

  return (
    <button
      onClick={onClick}
      className="flex w-full items-center gap-3 rounded-2xl border border-gray-100 bg-white p-4 text-left shadow-sm transition-all active:scale-[0.995] active:bg-gray-50"
      type="button"
    >
      <div className="min-w-0 flex-1">
        <div className="mb-1.5 flex items-center gap-2">
          <MoodBadge mood={conversation.detected_mood} size="sm" />
          <span className="flex items-center gap-1 text-[11px] text-gray-400">
            <Clock className="h-3 w-3" />
            {formatDuration(conversation.duration)}
          </span>
        </div>
        <p className="mb-1 text-sm font-medium leading-snug text-gray-800">{summary}</p>
        <p className="text-[11px] text-gray-500">{formatTimeAgo(conversation.timestamp)}</p>
      </div>
      <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-gray-50">
        <ChevronRight className="h-4 w-4 text-gray-400" />
      </div>
    </button>
  )
}
