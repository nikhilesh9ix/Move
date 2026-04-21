'use client'

import { useEffect, useState } from 'react'
import { fetchPortfolioSummary } from '@/services/api'
import type { PortfolioResponse } from '@/types'

interface State {
  data: PortfolioResponse | null
  loading: boolean
  error: string | null
}

export function usePortfolio(date: string): State {
  const [state, setState] = useState<State>({ data: null, loading: true, error: null })

  useEffect(() => {
    setState({ data: null, loading: true, error: null })
    fetchPortfolioSummary(date)
      .then((data) => setState({ data, loading: false, error: null }))
      .catch((err: Error) => setState({ data: null, loading: false, error: err.message }))
  }, [date])

  return state
}
