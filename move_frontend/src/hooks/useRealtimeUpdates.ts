'use client'

import { useEffect, useRef, useState } from 'react'
import type { Attribution } from '@/types'

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

export interface RealtimeEvent {
  type: 'analysis_update' | 'connected' | 'heartbeat' | 'pong'
  ticker?: string
  timestamp?: string
  price_change?: number
  attribution?: Attribution[]
  explanation?: string
  historical_hint?: string
  actionable_insight?: string
  confidence_pct?: number
}

interface ConnectedMessage extends RealtimeEvent {
  type: 'connected'
  initial_events: Record<string, RealtimeEvent>
}

interface RealtimeState {
  events: Record<string, RealtimeEvent>
  latestTicker: string | null
  connected: boolean
}

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------

// Determine WebSocket URL based on current page location
function getWebSocketUrl(): string {
  if (typeof window === 'undefined') {
    return process.env.NEXT_PUBLIC_BACKEND_WS_URL || 'ws://localhost:7860/ws/updates'
  }
  const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
  const host = window.location.host
  return process.env.NEXT_PUBLIC_BACKEND_WS_URL || `${protocol}//${host}/ws/updates`
}

const WS_URL = getWebSocketUrl()
const PING_INTERVAL_MS = 25_000
const RECONNECT_DELAY_MS = 3_000

// ---------------------------------------------------------------------------
// Hook
// ---------------------------------------------------------------------------

export function useRealtimeUpdates(): RealtimeState {
  const [state, setState] = useState<RealtimeState>({
    events: {},
    latestTicker: null,
    connected: false,
  })

  const wsRef = useRef<WebSocket | null>(null)
  const reconnectRef = useRef<ReturnType<typeof setTimeout> | null>(null)
  const mountedRef = useRef(true)

  function connect() {
    if (!mountedRef.current) return
    if (wsRef.current?.readyState === WebSocket.CONNECTING) return
    if (wsRef.current?.readyState === WebSocket.OPEN) return

    const ws = new WebSocket(WS_URL)
    wsRef.current = ws

    ws.onopen = () => {
      if (!mountedRef.current) return
      setState((prev) => ({ ...prev, connected: true }))
    }

    ws.onclose = () => {
      if (!mountedRef.current) return
      setState((prev) => ({ ...prev, connected: false }))
      // Schedule reconnect
      reconnectRef.current = setTimeout(connect, RECONNECT_DELAY_MS)
    }

    ws.onerror = () => {
      ws.close() // triggers onclose → reconnect
    }

    ws.onmessage = (ev: MessageEvent<string>) => {
      if (!mountedRef.current) return
      try {
        const msg = JSON.parse(ev.data) as RealtimeEvent | ConnectedMessage

        if (msg.type === 'connected') {
          const initial = (msg as ConnectedMessage).initial_events ?? {}
          setState((prev) => ({ ...prev, events: initial }))
          return
        }

        if (msg.type === 'analysis_update' && msg.ticker) {
          const { ticker } = msg
          setState((prev) => ({
            ...prev,
            events: { ...prev.events, [ticker]: msg },
            latestTicker: ticker,
          }))
        }
        // heartbeat / pong: no state change needed
      } catch {
        // Malformed JSON — ignore
      }
    }
  }

  useEffect(() => {
    mountedRef.current = true
    connect()

    const pingTimer = setInterval(() => {
      if (wsRef.current?.readyState === WebSocket.OPEN) {
        wsRef.current.send('ping')
      }
    }, PING_INTERVAL_MS)

    return () => {
      mountedRef.current = false
      clearInterval(pingTimer)
      if (reconnectRef.current) clearTimeout(reconnectRef.current)
      wsRef.current?.close()
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  return state
}
