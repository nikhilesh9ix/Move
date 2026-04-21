'use client'

import { useState } from 'react'
import { analyzeMove } from '@/services/api'
import type { AnalyzeResponse } from '@/types'

interface State {
  data: AnalyzeResponse | null
  loading: boolean
  error: string | null
}

export function useAnalysis() {
  const [state, setState] = useState<State>({ data: null, loading: false, error: null })

  async function analyze(stock: string, date: string): Promise<void> {
    setState({ data: null, loading: true, error: null })
    try {
      const data = await analyzeMove(stock, date)
      setState({ data, loading: false, error: null })
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Unknown error'
      setState({ data: null, loading: false, error: message })
    }
  }

  return { ...state, analyze }
}
