/**
 * API client tests: mock fetch and verify URL construction and response handling.
 */
const mockFetch = jest.fn()
beforeAll(() => {
  // @ts-expect-error global fetch
  global.fetch = mockFetch
})
afterEach(() => {
  mockFetch.mockReset()
})

describe('API client', () => {
  beforeEach(() => {
    process.env.NEXT_PUBLIC_API_URL = ''
    process.env.NEXT_PUBLIC_PATIENT_ID = 'patient-test-001'
  })

  it('getPatient calls correct URL and returns patient', async () => {
    const patient = { id: 'p1', name: 'Test', preferred_name: 'T', date_of_birth: '1950-01-01', birth_year: 1950, age: 74, location: { city: 'A', state: 'B', timezone: 'UTC' }, medical_notes: '', medications: [], preferences: { favorite_topics: [], communication_style: '', interests: [] }, cognitive_thresholds: { deviation_threshold: 0.2, consecutive_trigger: 3 } }
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ patient }),
    })
    const api = await import('../api')
    const result = await api.getPatient('patient-1')
    expect(mockFetch).toHaveBeenCalledWith(
      '/backend-api/patients/patient-1',
      expect.objectContaining({ headers: expect.any(Object) })
    )
    expect(result).toEqual(patient)
  })

  it('getPatient returns null on 404', async () => {
    mockFetch.mockResolvedValueOnce({ ok: false })
    const api = await import('../api')
    const result = await api.getPatient('missing')
    expect(result).toBeNull()
  })

  it('getConversations calls correct URL and returns array', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ conversations: [] }),
    })
    const api = await import('../api')
    const result = await api.getConversations('patient-1', 10, 0)
    expect(mockFetch).toHaveBeenCalledWith(
      expect.stringContaining('/backend-api/conversations?patient_id=patient-1&limit=10&offset=0'),
      expect.any(Object)
    )
    expect(result).toEqual([])
  })

  it('getAlerts appends severity when provided', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ alerts: [] }),
    })
    const api = await import('../api')
    await api.getAlerts('patient-1', 'high')
    expect(mockFetch).toHaveBeenCalledWith(
      expect.stringContaining('severity=high'),
      expect.any(Object)
    )
  })

  it('getPatientId returns env patient id', async () => {
    const api = await import('../api')
    expect(api.getPatientId()).toBe('patient-test-001')
  })

  it('downloadReport uses proxy path and returns blob', async () => {
    const blob = new Blob(['report content'], { type: 'application/pdf' })
    mockFetch.mockResolvedValueOnce({ ok: true, blob: async () => blob })
    const api = await import('../api')
    const result = await api.downloadReport('patient-1', 30)
    expect(mockFetch).toHaveBeenCalledWith('/backend-api/reports/patient-1/cognitive-report?days=30')
    expect(result).toEqual(blob)
  })

  it('downloadReport returns null on non-ok response', async () => {
    mockFetch.mockResolvedValueOnce({ ok: false })
    const api = await import('../api')
    const result = await api.downloadReport('patient-1', 7)
    expect(result).toBeNull()
  })
})
