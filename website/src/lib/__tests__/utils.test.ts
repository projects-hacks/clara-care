import {
  cn,
  formatDate,
  formatDateTime,
  formatTimeAgo,
  formatDuration,
  moodEmoji,
  moodLabel,
  moodColor,
  severityColor,
  cognitiveScoreColor,
  cognitiveScoreBg,
  alertTypeLabel,
  metricLabel,
  formatPercent,
} from '../utils'

describe('cn', () => {
  it('joins class names', () => {
    expect(cn('a', 'b')).toBe('a b')
  })
  it('handles conditional classes', () => {
    expect(cn('a', false && 'b', 'c')).toBe('a c')
  })
})

describe('formatDate', () => {
  it('formats ISO date string', () => {
    expect(formatDate('2024-06-15T12:00:00.000Z')).toMatch(/Jun 15, 2024/)
  })
  it('returns original string on invalid input', () => {
    expect(formatDate('not-a-date')).toBe('not-a-date')
  })
})

describe('formatDateTime', () => {
  it('formats ISO date with time', () => {
    const out = formatDateTime('2024-06-15T14:30:00.000Z')
    expect(out).toMatch(/Jun 15, 2024/)
    expect(out).toMatch(/\d{1,2}:\d{2}/)
  })
  it('returns original on invalid input', () => {
    expect(formatDateTime('x')).toBe('x')
  })
})

describe('formatTimeAgo', () => {
  it('returns string with suffix for past date', () => {
    const past = new Date(Date.now() - 3600000).toISOString()
    expect(formatTimeAgo(past)).toMatch(/ago/)
  })
  it('returns original on invalid input', () => {
    expect(formatTimeAgo('invalid')).toBe('invalid')
  })
})

describe('formatDuration', () => {
  it('formats seconds only', () => {
    expect(formatDuration(45)).toBe('45s')
  })
  it('formats minutes only', () => {
    expect(formatDuration(300)).toBe('5m')
  })
  it('formats minutes and seconds', () => {
    expect(formatDuration(285)).toBe('4m 45s')
  })
})

describe('moodEmoji', () => {
  it('returns emoji for known mood', () => {
    expect(moodEmoji('happy')).toBe('😊')
    expect(moodEmoji('nostalgic')).toBe('🥰')
  })
  it('is case insensitive', () => {
    expect(moodEmoji('HAPPY')).toBe('😊')
  })
  it('returns default for unknown mood', () => {
    expect(moodEmoji('unknown')).toBe('😐')
  })
})

describe('moodLabel', () => {
  it('capitalizes first letter', () => {
    expect(moodLabel('happy')).toBe('Happy')
  })
  it('returns Unknown for empty', () => {
    expect(moodLabel('')).toBe('Unknown')
  })
})

describe('moodColor', () => {
  it('returns class string for known mood', () => {
    expect(moodColor('happy')).toContain('green')
  })
  it('returns default for unknown mood', () => {
    expect(moodColor('unknown')).toContain('gray')
  })
})

describe('severityColor', () => {
  it('returns class for low/medium/high', () => {
    expect(severityColor('low')).toContain('blue')
    expect(severityColor('high')).toContain('red')
  })
})

describe('cognitiveScoreColor', () => {
  it('returns green for 80+', () => {
    expect(cognitiveScoreColor(85)).toBe('text-green-600')
  })
  it('returns yellow for 60-79', () => {
    expect(cognitiveScoreColor(70)).toBe('text-yellow-600')
  })
  it('returns red below 60', () => {
    expect(cognitiveScoreColor(50)).toBe('text-red-600')
  })
})

describe('cognitiveScoreBg', () => {
  it('returns green bg for 80+', () => {
    expect(cognitiveScoreBg(80)).toContain('green')
  })
})

describe('alertTypeLabel', () => {
  it('returns human-readable for known type', () => {
    expect(alertTypeLabel('word_finding_difficulty')).toBe('Word Finding Difficulty')
  })
  it('formats unknown with underscores', () => {
    expect(alertTypeLabel('some_alert_type')).toBe('Some Alert Type')
  })
})

describe('metricLabel', () => {
  it('returns label for known key', () => {
    expect(metricLabel('vocabulary_diversity')).toBe('Vocabulary Diversity')
  })
  it('returns key for unknown', () => {
    expect(metricLabel('unknown_key')).toBe('unknown_key')
  })
})

describe('formatPercent', () => {
  it('converts decimal to percentage', () => {
    expect(formatPercent(0.63)).toBe('63%')
  })
  it('rounds', () => {
    expect(formatPercent(0.635)).toBe('64%')
  })
})
