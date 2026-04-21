'use client'

import { motion } from 'framer-motion'
import { PriceChange } from './PriceChange'
import { formatCurrency } from '@/constants'
import type { HoldingChange, PortfolioResponse } from '@/types'

interface Props {
  data: PortfolioResponse
}

function HoldingRow({ holding, index }: { holding: HoldingChange; index: number }) {
  return (
    <motion.div
      initial={{ opacity: 0, x: 10 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ delay: index * 0.07 + 0.3 }}
      className="flex items-center justify-between py-2.5 border-b border-slate-800/60 last:border-0"
    >
      <div className="flex items-center gap-3">
        <div className="w-8 h-8 bg-slate-800 rounded-lg flex items-center justify-center">
          <span className="text-slate-400 text-xs font-bold">
            {holding.stock.slice(0, 2)}
          </span>
        </div>
        <span className="text-slate-300 text-sm font-medium">{holding.stock}</span>
      </div>
      <div className="text-right">
        <PriceChange value={holding.price_change} size="sm" />
        <div className={`text-xs font-mono ${holding.value_change >= 0 ? 'text-emerald-500/60' : 'text-rose-500/60'}`}>
          {holding.value_change >= 0 ? '+' : ''}{formatCurrency(holding.value_change)}
        </div>
      </div>
    </motion.div>
  )
}

export function PortfolioSummary({ data }: Props) {
  const isLoss = data.total_change_pct < 0

  return (
    <motion.div
      initial={{ opacity: 0, y: 24 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.45, delay: 0.1, ease: 'easeOut' }}
      className="bg-slate-900 border border-slate-800 rounded-2xl p-6 flex flex-col gap-6"
    >
      {/* Total value */}
      <div>
        <p className="text-slate-500 text-xs font-medium uppercase tracking-widest mb-2">
          Portfolio value
        </p>
        <p className="text-slate-50 text-2xl font-bold font-mono tabular-nums">
          {formatCurrency(data.total_value)}
        </p>
        <div className="mt-1">
          <PriceChange value={data.total_change_pct} size="sm" />
          <span className="text-slate-500 text-xs ml-2">today</span>
        </div>
      </div>

      {/* Visual change bar */}
      <div className="h-1.5 bg-slate-800 rounded-full overflow-hidden">
        <motion.div
          className={`h-full rounded-full ${isLoss ? 'bg-rose-500' : 'bg-emerald-500'}`}
          initial={{ width: 0 }}
          animate={{ width: `${Math.min(Math.abs(data.total_change_pct) * 8, 100)}%` }}
          transition={{ duration: 0.8, delay: 0.4, ease: 'easeOut' }}
        />
      </div>

      {/* Gainers */}
      {data.top_gainers.length > 0 && (
        <div>
          <p className="text-slate-500 text-xs font-medium uppercase tracking-widest mb-1">
            Top gainers
          </p>
          {data.top_gainers.map((h, i) => (
            <HoldingRow key={h.stock} holding={h} index={i} />
          ))}
        </div>
      )}

      {/* Losers */}
      {data.top_losers.length > 0 && (
        <div>
          <p className="text-slate-500 text-xs font-medium uppercase tracking-widest mb-1">
            Top losers
          </p>
          {data.top_losers.map((h, i) => (
            <HoldingRow key={h.stock} holding={h} index={i + (data.top_gainers.length)} />
          ))}
        </div>
      )}
    </motion.div>
  )
}
