'use client'

import { motion } from 'framer-motion'
import type { StockMockData } from '@/data/mockStockData'

interface Props {
  data: StockMockData
}

function formatCr(v: number): string {
  if (v >= 100000) return `₹${(v / 100000).toFixed(2)}L Cr`
  return `₹${v.toLocaleString('en-IN')} Cr`
}

function GrowthBadge({ pct }: { pct: number }) {
  const up = pct >= 0
  const color = up ? '#10b981' : '#f43f5e'
  return (
    <span
      className="text-[10px] font-mono font-semibold px-1.5 py-0.5 rounded"
      style={{ background: `${color}15`, color }}
    >
      {up ? '+' : ''}{pct.toFixed(1)}%
    </span>
  )
}

function MiniBar({ value, max, color }: { value: number; max: number; color: string }) {
  const pct = Math.min((value / max) * 100, 100)
  return (
    <div className="flex-1 h-1 rounded-full overflow-hidden" style={{ background: 'rgba(255,255,255,0.05)' }}>
      <motion.div
        className="h-full rounded-full"
        style={{ backgroundColor: color }}
        initial={{ width: 0 }}
        animate={{ width: `${pct}%` }}
        transition={{ duration: 0.9, ease: [0.16, 1, 0.3, 1] }}
      />
    </div>
  )
}

export function Fundamentals({ data }: Props) {
  const maxRevenue = Math.max(...data.revenue.map((r) => r.value))
  const maxProfit  = Math.max(...data.profit.map((p) => p.value))

  const healthColor =
    data.balance.healthLabel === 'Strong'
      ? '#10b981'
      : data.balance.healthLabel === 'Moderate'
      ? '#f59e0b'
      : '#f43f5e'

  return (
    <div className="space-y-4">
      <p className="text-slate-500 text-[10px] font-semibold uppercase tracking-[0.18em]">
        Fundamental Analysis
      </p>

      {/* Row 1: Financial Performance + Balance Sheet */}
      <div className="grid grid-cols-1 md:grid-cols-5 gap-4">

        {/* Financial Performance — spans 3 cols */}
        <motion.div
          initial={{ opacity: 0, y: 14 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.35 }}
          className="md:col-span-3 rounded-xl p-5"
          style={{
            background: 'rgba(255,255,255,0.025)',
            border: '1px solid rgba(255,255,255,0.06)',
          }}
        >
          <p className="text-slate-400 text-xs font-semibold mb-4">Revenue &amp; Profit Trend</p>

          {/* Revenue rows */}
          <div className="space-y-3 mb-5">
            <p className="text-slate-600 text-[10px] uppercase tracking-[0.12em]">Revenue</p>
            {data.revenue.map((row) => (
              <div key={row.year} className="flex items-center gap-3">
                <span className="text-slate-500 text-xs font-mono w-10 shrink-0">{row.year}</span>
                <MiniBar value={row.value} max={maxRevenue} color="#3b82f6" />
                <span className="text-slate-300 text-xs font-mono w-24 text-right shrink-0">
                  {formatCr(row.value)}
                </span>
              </div>
            ))}
          </div>

          {/* Profit rows */}
          <div className="space-y-3">
            <p className="text-slate-600 text-[10px] uppercase tracking-[0.12em]">Net Profit</p>
            {data.profit.map((row) => (
              <div key={row.year} className="flex items-center gap-3">
                <span className="text-slate-500 text-xs font-mono w-10 shrink-0">{row.year}</span>
                <MiniBar value={row.value} max={maxProfit} color="#10b981" />
                <span className="text-slate-300 text-xs font-mono w-24 text-right shrink-0">
                  {formatCr(row.value)}
                </span>
              </div>
            ))}
          </div>

          {/* YoY growth */}
          <div
            className="flex items-center gap-4 mt-5 pt-4"
            style={{ borderTop: '1px solid rgba(255,255,255,0.05)' }}
          >
            <div className="flex items-center gap-2">
              <span className="text-slate-600 text-xs">Revenue growth</span>
              <GrowthBadge pct={data.revenueGrowth} />
            </div>
            <div className="flex items-center gap-2">
              <span className="text-slate-600 text-xs">Profit growth</span>
              <GrowthBadge pct={data.profitGrowth} />
            </div>
          </div>
        </motion.div>

        {/* Balance Sheet + Industry — spans 2 cols */}
        <div className="md:col-span-2 flex flex-col gap-4">

          {/* Balance Sheet */}
          <motion.div
            initial={{ opacity: 0, y: 14 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.35, delay: 0.08 }}
            className="rounded-xl p-5 flex-1"
            style={{
              background: 'rgba(255,255,255,0.025)',
              border: '1px solid rgba(255,255,255,0.06)',
            }}
          >
            <p className="text-slate-400 text-xs font-semibold mb-4">Balance Sheet</p>
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-slate-500 text-xs">Total Debt</span>
                <span className="text-slate-300 text-xs font-mono">{data.balance.totalDebt}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-slate-500 text-xs">Cash &amp; Equiv.</span>
                <span className="text-slate-300 text-xs font-mono">{data.balance.cash}</span>
              </div>
              <div className="flex items-center justify-between pt-1" style={{ borderTop: '1px solid rgba(255,255,255,0.05)' }}>
                <span className="text-slate-500 text-xs">Financial Health</span>
                <span
                  className="text-[10px] font-semibold px-2 py-0.5 rounded-md"
                  style={{ background: `${healthColor}18`, color: healthColor, border: `1px solid ${healthColor}28` }}
                >
                  {data.balance.healthLabel}
                </span>
              </div>
            </div>

            {/* Health score bar */}
            <div className="mt-3">
              <div className="h-1 rounded-full overflow-hidden" style={{ background: 'rgba(255,255,255,0.05)' }}>
                <motion.div
                  className="h-full rounded-full"
                  style={{ backgroundColor: healthColor }}
                  initial={{ width: 0 }}
                  animate={{ width: `${data.balance.healthScore}%` }}
                  transition={{ duration: 1, delay: 0.2, ease: [0.16, 1, 0.3, 1] }}
                />
              </div>
            </div>
          </motion.div>

          {/* Industry & Competitors */}
          <motion.div
            initial={{ opacity: 0, y: 14 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.35, delay: 0.14 }}
            className="rounded-xl p-5"
            style={{
              background: 'rgba(255,255,255,0.025)',
              border: '1px solid rgba(255,255,255,0.06)',
            }}
          >
            <p className="text-slate-400 text-xs font-semibold mb-3">Industry</p>
            <span
              className="inline-block text-xs px-2.5 py-1 rounded-lg mb-3 font-medium"
              style={{
                background: 'rgba(59,130,246,0.1)',
                color: '#93c5fd',
                border: '1px solid rgba(59,130,246,0.2)',
              }}
            >
              {data.sector}
            </span>
            <p className="text-slate-600 text-[10px] uppercase tracking-[0.12em] mb-2">Competitors</p>
            <div className="flex flex-wrap gap-1.5">
              {data.competitors.map((c) => (
                <span
                  key={c}
                  className="text-[10px] px-2 py-0.5 rounded-md"
                  style={{
                    background: 'rgba(255,255,255,0.05)',
                    color: '#94a3b8',
                    border: '1px solid rgba(255,255,255,0.07)',
                  }}
                >
                  {c}
                </span>
              ))}
            </div>
          </motion.div>
        </div>
      </div>

      {/* Row 2: Promoter Holding + Pros & Cons */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">

        {/* Promoter Holding */}
        <motion.div
          initial={{ opacity: 0, y: 14 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.35, delay: 0.18 }}
          className="rounded-xl p-5"
          style={{
            background: 'rgba(255,255,255,0.025)',
            border: '1px solid rgba(255,255,255,0.06)',
          }}
        >
          <p className="text-slate-400 text-xs font-semibold mb-3">Management</p>
          <div className="flex items-end justify-between mb-2">
            <span className="text-slate-500 text-xs">Promoter holding</span>
            <span
              className="text-xl font-bold font-mono tabular-nums"
              style={{ color: data.promoterHolding > 50 ? '#10b981' : data.promoterHolding > 25 ? '#f59e0b' : '#64748b' }}
            >
              {data.promoterHolding.toFixed(1)}%
            </span>
          </div>
          <div className="h-1.5 rounded-full overflow-hidden" style={{ background: 'rgba(255,255,255,0.05)' }}>
            <motion.div
              className="h-full rounded-full"
              style={{
                background:
                  data.promoterHolding > 50
                    ? 'linear-gradient(90deg, #10b981, #34d399)'
                    : data.promoterHolding > 25
                    ? 'linear-gradient(90deg, #f59e0b, #fbbf24)'
                    : 'linear-gradient(90deg, #64748b, #94a3b8)',
              }}
              initial={{ width: 0 }}
              animate={{ width: `${data.promoterHolding}%` }}
              transition={{ duration: 1, delay: 0.3, ease: [0.16, 1, 0.3, 1] }}
            />
          </div>
          <p className="text-slate-700 text-[10px] mt-2">
            {data.promoterHolding > 50
              ? 'High conviction from founders'
              : data.promoterHolding > 25
              ? 'Moderate promoter confidence'
              : 'Professionally managed'}
          </p>
        </motion.div>

        {/* Pros & Cons */}
        <motion.div
          initial={{ opacity: 0, y: 14 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.35, delay: 0.22 }}
          className="md:col-span-3 rounded-xl p-5"
          style={{
            background: 'rgba(255,255,255,0.025)',
            border: '1px solid rgba(255,255,255,0.06)',
          }}
        >
          <p className="text-slate-400 text-xs font-semibold mb-4">Pros &amp; Cons</p>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {/* Pros */}
            <div>
              <div className="flex items-center gap-1.5 mb-3">
                <div className="w-1.5 h-1.5 rounded-full bg-emerald-500" style={{ boxShadow: '0 0 6px #10b981' }} />
                <p className="text-emerald-500 text-[10px] font-semibold uppercase tracking-[0.12em]">Strengths</p>
              </div>
              <ul className="space-y-2">
                {data.pros.map((pro) => (
                  <li key={pro} className="flex items-start gap-2">
                    <span className="text-emerald-600 text-xs mt-0.5 shrink-0">+</span>
                    <span className="text-slate-400 text-xs leading-relaxed">{pro}</span>
                  </li>
                ))}
              </ul>
            </div>
            {/* Cons */}
            <div>
              <div className="flex items-center gap-1.5 mb-3">
                <div className="w-1.5 h-1.5 rounded-full bg-rose-500" style={{ boxShadow: '0 0 6px #f43f5e' }} />
                <p className="text-rose-500 text-[10px] font-semibold uppercase tracking-[0.12em]">Risks</p>
              </div>
              <ul className="space-y-2">
                {data.cons.map((con) => (
                  <li key={con} className="flex items-start gap-2">
                    <span className="text-rose-600 text-xs mt-0.5 shrink-0">−</span>
                    <span className="text-slate-400 text-xs leading-relaxed">{con}</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </motion.div>
      </div>
    </div>
  )
}
