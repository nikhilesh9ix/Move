'use client'

import { motion } from 'framer-motion'
import type { WhyCardResponse } from '@/types'

interface Props {
  data: WhyCardResponse | null
}

const DRIVER_MESSAGES: Record<string, string> = {
  'Sector-wide pressure':  'Sector-wide selling is impacting your IT holdings simultaneously.',
  'Macro headwinds':       'Global macro forces are creating broad-based pressure across your portfolio.',
  'Rate sensitivity':      'Bond yield movements are compressing valuations across your rate-sensitive holdings.',
  'Earnings revision':     'Analyst estimate revisions are repricing multiple holdings in your portfolio.',
  'Company-specific news': 'Company-level events are moving individual holdings independently of the market.',
}

export function EventAlert({ data }: Props) {
  if (!data) return null
  const absPct = Math.abs(data.total_portfolio_change_pct)
  if (absPct < 1.5) return null          // only show for significant moves

  const isLoss   = data.total_portfolio_change_pct < 0
  const driver   = data.primary_driver_label || ''
  const message  = DRIVER_MESSAGES[driver] ?? `${driver} is the primary force in today's move.`
  const emoji    = isLoss ? '⚡' : '📈'
  const severity = absPct > 3 ? 'high' : 'medium'

  const containerCls =
    severity === 'high'
      ? 'bg-rose-500/8 border-rose-500/25'
      : isLoss
      ? 'bg-amber-500/8 border-amber-500/25'
      : 'bg-emerald-500/8 border-emerald-500/25'

  const textCls =
    severity === 'high'
      ? 'text-rose-300'
      : isLoss
      ? 'text-amber-300'
      : 'text-emerald-300'

  const subCls =
    severity === 'high'
      ? 'text-rose-400/70'
      : isLoss
      ? 'text-amber-400/70'
      : 'text-emerald-400/70'

  return (
    <motion.div
      initial={{ opacity: 0, y: -8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.35 }}
      className={`border rounded-xl px-5 py-3.5 flex items-start gap-3 ${containerCls}`}
    >
      <span className="text-base mt-px shrink-0">{emoji}</span>
      <div>
        <p className={`text-sm font-semibold ${textCls}`}>
          {isLoss ? 'Market event detected' : 'Portfolio momentum alert'} ·{' '}
          <span className="font-mono">{data.total_portfolio_change_pct > 0 ? '+' : ''}{data.total_portfolio_change_pct.toFixed(2)}%</span>
        </p>
        <p className={`text-xs mt-0.5 leading-relaxed ${subCls}`}>
          {driver && <span className="font-medium">{driver}: </span>}
          {message}
        </p>
      </div>
    </motion.div>
  )
}
