'use client'

import { useEffect, useState } from 'react'
import { fetchWhyCard } from '@/services/api'
import type { WhyCardResponse } from '@/types'

interface State {
  data: WhyCardResponse | null
  loading: boolean
  error: string | null
}

export function useWhyCard(date: string): State {
  const [state, setState] = useState<State>({ data: null, loading: true, error: null })

  useEffect(() => {
    setState({ data: null, loading: true, error: null })
    fetchWhyCard(date)
      .then((data) => setState({ data, loading: false, error: null }))
      .catch((err: Error) => setState({ data: null, loading: false, error: err.message }))
  }, [date])

  return state
}
