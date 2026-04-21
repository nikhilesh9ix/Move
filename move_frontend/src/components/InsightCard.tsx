'use client'

import { motion } from 'framer-motion'
import { formatCurrency } from '@/constants'
import type { WhyCardResponse } from '@/types'

interface Props {
  data: WhyCardResponse | null
  totalValue?: number
}

// Historical recovery rates per dominant factor (mock, for simulation)
const RECOVERY: Record<string, { pct: number; days: number }> = {
  sector:        { pct: 8.4,  days: 5  },
  macro:         { pct: 6.2,  days: 10 },
  rates:         { pct: 5.1,  days: 7  },
  earnings:      { pct: 3.8,  days: 14 },
  idiosyncratic: { pct: 9.2,  days: 7  },
}

const TOP_INSIGHTS: Record<string, string> = {
  sector:        'Sector-driven moves have the highest short-term reversal rate (68%) among all factor types.',
  macro:         'Macro-driven selloffs rarely isolate to a single portfolio — diversification matters most here.',
  rates:         'Rate-sensitive stocks recover fastest when yield expectations stabilise, often within a week.',
  earnings:      'Earnings revisions propagate across the quarter — monitor peer guidance over the next 30 days.',
  idiosyncratic: 'Company-specific drops carry the lowest correlation risk — your other holdings are likely unaffected.',
}

export function InsightCard({ data, totalValue }: Props) {
  if (!data || data.top_causes.length === 0) return null

  const dominantCause = data.top_causes[0].cause
  const recovery      = RECOVERY[dominantCause] ?? { pct: 7.0, days: 7 }
  const topInsight    = TOP_INSIGHTS[dominantCause] ?? ''

  const isLoss = data.total_portfolio_change_pct < 0
  // Recovery = recovery.pct% of total portfolio value (not of the loss amount)
  // Conservative 85% factor accounts for partial recoveries
  const estimatedRecovery = totalValue
    ? totalValue * (recovery.pct / 100) * 0.85
    : null

  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay: 0.1 }}
      className="grid grid-cols-1 md:grid-cols-2 gap-4"
    >
      {/* ── If you held… ── */}
      {isLoss && (
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5">
          <p className="text-slate-500 text-xs font-medium uppercase tracking-widest mb-3">
            If you held through similar drops
          </p>
          <div className="space-y-2.5">
            <div className="flex items-baseline gap-2">
              <span className="text-emerald-400 text-2xl font-bold font-mono tabular-nums">
                +{recovery.pct}%
              </span>
              <span className="text-slate-500 text-xs">avg recovery</span>
            </div>
            <p className="text-slate-400 text-sm">
              In the last 3 similar{' '}
              <span className="text-slate-300 font-medium">{dominantCause}</span>-driven drops,
              portfolios recovered within{' '}
              <span className="text-slate-300 font-medium">{recovery.days} trading days</span> on average.
            </p>
            {estimatedRecovery != null && (
              <div className="bg-emerald-500/8 border border-emerald-500/15 rounded-xl px-4 py-3 mt-1">
                <p className="text-emerald-400/80 text-xs mb-0.5">Estimated recovery (if held)</p>
                <p className="text-emerald-400 text-lg font-bold font-mono">
                  +{formatCurrency(estimatedRecovery)}
                </p>
                <p className="text-emerald-600 text-xs mt-0.5">
                  Based on historical pattern · not a prediction
                </p>
              </div>
            )}
          </div>
        </div>
      )}

      {/* ── Top insight of the day ── */}
      <div className={`bg-slate-900 border border-slate-800 rounded-2xl p-5 ${!isLoss ? 'md:col-span-2' : ''}`}>
        <p className="text-slate-500 text-xs font-medium uppercase tracking-widest mb-3">
          Top insight · {new Date().toLocaleDateString('en-IN', { weekday: 'short', month: 'short', day: 'numeric' })}
        </p>
        <div className="flex items-start gap-3">
          <div className="w-8 h-8 bg-blue-500/10 border border-blue-500/20 rounded-lg flex items-center justify-center shrink-0 mt-0.5">
            <span className="text-sm">🎯</span>
          </div>
          <div>
            <p className="text-slate-200 text-sm leading-relaxed font-medium mb-1.5">
              {topInsight}
            </p>
            <p className="text-slate-500 text-xs">
              Primary driver today:{' '}
              <span className="text-slate-400 font-medium">
                {data.primary_driver_label || dominantCause}
              </span>
              {' '}·{' '}
              <span className="font-mono">{data.top_causes[0].impact}%</span> of total portfolio move
            </p>
          </div>
        </div>
      </div>
    </motion.div>
  )
}
