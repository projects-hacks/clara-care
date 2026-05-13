/**
 * Enterprise-grade timezone utilities
 * Provides comprehensive IANA timezone support with grouping and metadata
 */

export interface TimezoneOption {
  value: string
  label: string
  offset: string
  region: string
}

/**
 * Get all IANA timezones with current UTC offsets
 * Uses Intl API for accurate, up-to-date timezone data
 */
export function getAllTimezones(): TimezoneOption[] {
  const timezones: TimezoneOption[] = []
  
  // Get all supported timezones from the browser
  const supportedTimezones = Intl.supportedValuesOf('timeZone')
  
  for (const tz of supportedTimezones) {
    try {
      // Get current offset for this timezone
      const offset = getTimezoneOffset(tz)
      const region = tz.split('/')[0]
      
      // Create readable label with city name and offset
      const parts = tz.split('/')
      const city = parts[parts.length - 1].replace(/_/g, ' ')
      const label = `${city} (${offset})`
      
      timezones.push({
        value: tz,
        label,
        offset,
        region,
      })
    } catch {
      // Skip invalid timezones
      continue
    }
  }
  
  // Sort by offset, then by name
  return timezones.sort((a, b) => {
    const offsetA = parseOffset(a.offset)
    const offsetB = parseOffset(b.offset)
    if (offsetA !== offsetB) return offsetA - offsetB
    return a.label.localeCompare(b.label)
  })
}

/**
 * Get commonly used timezones for quick access
 */
export function getCommonTimezones(): TimezoneOption[] {
  const common = [
    'America/New_York',
    'America/Chicago',
    'America/Denver',
    'America/Los_Angeles',
    'America/Phoenix',
    'America/Anchorage',
    'Pacific/Honolulu',
    'America/Toronto',
    'America/Vancouver',
    'Europe/London',
    'Europe/Paris',
    'Europe/Berlin',
    'Asia/Tokyo',
    'Asia/Shanghai',
    'Asia/Dubai',
    'Australia/Sydney',
    'Pacific/Auckland',
  ]
  
  const all = getAllTimezones()
  return all.filter(tz => common.includes(tz.value))
}

/**
 * Get timezones grouped by region
 */
export function getTimezonesByRegion(): Record<string, TimezoneOption[]> {
  const all = getAllTimezones()
  const grouped: Record<string, TimezoneOption[]> = {}
  
  for (const tz of all) {
    if (!grouped[tz.region]) {
      grouped[tz.region] = []
    }
    grouped[tz.region].push(tz)
  }
  
  return grouped
}

/**
 * Get current UTC offset for a timezone in format "UTC±HH:MM"
 */
function getTimezoneOffset(timezone: string): string {
  const now = new Date()
  const formatter = new Intl.DateTimeFormat('en-US', {
    timeZone: timezone,
    timeZoneName: 'longOffset',
  })
  
  const parts = formatter.formatToParts(now)
  const offsetPart = parts.find(p => p.type === 'timeZoneName')
  
  if (offsetPart && offsetPart.value.startsWith('GMT')) {
    const offset = offsetPart.value.replace('GMT', 'UTC')
    return offset === 'UTC' ? 'UTC+00:00' : offset
  }
  
  // Fallback: calculate manually
  const utcDate = new Date(now.toLocaleString('en-US', { timeZone: 'UTC' }))
  const tzDate = new Date(now.toLocaleString('en-US', { timeZone: timezone }))
  const offsetMinutes = (tzDate.getTime() - utcDate.getTime()) / 60000
  
  const hours = Math.floor(Math.abs(offsetMinutes) / 60)
  const minutes = Math.abs(offsetMinutes) % 60
  const sign = offsetMinutes >= 0 ? '+' : '-'
  
  return `UTC${sign}${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}`
}

/**
 * Parse offset string to minutes for sorting
 */
function parseOffset(offset: string): number {
  const match = offset.match(/UTC([+-])(\d{2}):(\d{2})/)
  if (!match) return 0
  
  const sign = match[1] === '+' ? 1 : -1
  const hours = parseInt(match[2], 10)
  const minutes = parseInt(match[3], 10)
  
  return sign * (hours * 60 + minutes)
}

/**
 * Detect user's current timezone
 */
export function detectUserTimezone(): string {
  return Intl.DateTimeFormat().resolvedOptions().timeZone
}
