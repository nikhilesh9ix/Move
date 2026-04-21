'use client'

import { AnimatePresence, motion } from 'framer-motion'
import { PriceChange } from './PriceChange'
import { factorColor } from '@/constants'
import type { RealtimeEvent } from '@/hooks/useRealtimeUpdates'

interface Props {
  events: Record<string, RealtimeEvent>
  latestTicker: string | null
}

function FactorChip({ factor, contribution }: { factor: string; contribution: number }) {
  const color = factorColor(factor)
  return (
    <span
      className="text-xs px-2.5 py-1 rounded-lg font-mono font-medium"
      style={{
        backgroundColor: `${color}12`,
        color,
        border: `1px solid ${color}28`,
      }}
    >
      {factor} <span style={{ opacity: 0.7 }}>{contribution}%</span>
    </span>
  )
}

function ConfidencePill({ pct }: { pct: number }) {
  const level = pct >= 78 ? 'High' : pct >= 62 ? 'Medium' : 'Low'
  const color =
    level === 'High' ? '#10b981' : level === 'Medium' ? '#f59e0b' : '#64748b'
  return (
    <span
      className="text-xs px-2 py-0.5 rounded-md font-medium"
      style={{
        backgroundColor: `${color}12`,
        color,
        border: `1px solid ${color}28`,
      }}
    >
      {level} · {pct}%
    </span>
  )
}

export function LiveFeed({ events, latestTicker }: Props) {
  const updates = Object.values(events).filter(
    (e): e is Required<RealtimeEvent> => e.type === 'analysis_update'
  )

  if (updates.length === 0) {
    return (
      <div
        className="rounded-2xl p-10 text-center"
        style={{
          background: 'rgba(255,255,255,0.015)',
          border: '1px dashed rgba(255,255,255,0.07)',
        }}
      >
        <div className="flex justify-center mb-3">
          <span
            className="w-2 h-2 rounded-full animate-pulse"
            style={{ background: 'rgba(255,255,255,0.15)' }}
          />
        </div>
        <p className="text-slate-500 text-sm">Waiting for price movements…</p>
        <p className="text-slate-700 text-xs mt-1">
          Watcher checks every 20 s · threshold ±0.8%
        </p>
      </div>
    )
  }

  return (
    <div className="space-y-3">
      <AnimatePresence initial={false}>
        {updates.map((event) => {
          const isLatest = event.ticker === latestTicker
          const hasHint = Boolean(event.historical_hint)
          const hasInsight = Boolean(event.actionable_insight)

          return (
            <motion.div
              key={event.ticker}
              layout
              initial={{ opacity: 0, y: -14, scale: 0.98 }}
              animate={{ opacity: 1, y: 0, scale: 1 }}
              exit={{ opacity: 0, scale: 0.97 }}
              transition={{ duration: 0.3 }}
              className="rounded-xl p-4"
              style={{
                background: isLatest
                  ? 'linear-gradient(135deg, #0d1a2e 0%, #050e1a 100%)'
                  : 'rgba(255,255,255,0.02)',
                border: isLatest
                  ? '1px solid rgba(59,130,246,0.35)'
                  : '1px solid rgba(255,255,255,0.05)',
                boxShadow: isLatest
                  ? '0 0 24px rgba(59,130,246,0.08), inset 0 1px 0 rgba(255,255,255,0.04)'
                  : 'none',
              }}
            >
              {/* Header */}
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center gap-2.5">
                  {isLatest && (
                    <span
                      className="w-1.5 h-1.5 rounded-full bg-blue-400 shrink-0"
                      style={{ boxShadow: '0 0 6px #60a5fa', animation: 'pulse 2s infinite' }}
                    />
                  )}
                  {/* Ticker avatar */}
                  <div
                    className="w-8 h-8 rounded-lg flex items-center justify-center shrink-0"
                    style={{
                      background: 'rgba(255,255,255,0.04)',
                      border: '1px solid rgba(255,255,255,0.08)',
                    }}
                  >
                    <span className="text-slate-300 font-bold text-xs">
                      {event.ticker.slice(0, 2)}
                    </span>
                  </div>
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="text-slate-100 font-semibold text-sm">{event.ticker}</span>
                      {isLatest && (
                        <span
                          className="text-[10px] font-semibold px-1.5 py-0.5 rounded-md"
                          style={{
                            background: 'rgba(59,130,246,0.15)',
                            color: '#93c5fd',
                            border: '1px solid rgba(59,130,246,0.25)',
                          }}
                        >
                          LIVE
                        </span>
                      )}
                    </div>
                  </div>
                  <PriceChange value={event.price_change ?? 0} size="sm" />
                </div>
                <div className="flex items-center gap-2 shrink-0">
                  {event.confidence_pct != null && (
                    <ConfidencePill pct={event.confidence_pct} />
                  )}
                  <span className="text-slate-700 text-xs font-mono">
                    {event.timestamp?.split('T')[1]?.slice(0, 8) ?? ''}
                  </span>
                </div>
              </div>

              {/* Attribution chips */}
              {event.attribution && (
                <div className="flex flex-wrap gap-1.5 mb-3">
                  {event.attribution
                    .slice()
                    .sort((a, b) => b.contribution - a.contribution)
                    .map((a) => (
                      <FactorChip
                        key={a.factor}
                        factor={a.factor}
                        contribution={a.contribution}
                      />
                    ))}
                </div>
              )}

              {/* Explanation */}
              <p
                className="text-sm leading-relaxed mb-2.5 line-clamp-2"
                style={{ color: isLatest ? 'rgba(203,213,225,0.9)' : 'rgba(100,116,139,0.9)' }}
              >
                {event.explanation}
              </p>

              {/* Historical hint */}
              {hasHint && (
                <div
                  className="flex items-start gap-2 rounded-lg px-3 py-2 mb-2"
                  style={{
                    background: 'rgba(255,255,255,0.03)',
                    border: '1px solid rgba(255,255,255,0.05)',
                  }}
                >
                  <span className="text-slate-600 text-xs mt-px shrink-0">◷</span>
                  <p className="text-slate-500 text-xs leading-relaxed">
                    {event.historical_hint}
                  </p>
                </div>
              )}

              {/* Actionable insight */}
              {hasInsight && (
                <div
                  className="flex items-start gap-2 rounded-lg px-3 py-2"
                  style={{
                    background: 'rgba(59,130,246,0.05)',
                    border: '1px solid rgba(59,130,246,0.15)',
                  }}
                >
                  <span className="text-blue-500 text-xs mt-px shrink-0">↗</span>
                  <p className="text-blue-300/70 text-xs leading-relaxed">
                    {event.actionable_insight}
                  </p>
                </div>
              )}
            </motion.div>
          )
        })}
      </AnimatePresence>
    </div>
  )
}
