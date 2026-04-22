'use client'

import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  ResponsiveContainer,
  ComposedChart,
  Area,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
} from 'recharts'
import type { StockMockData } from '@/data/mockStockData'

interface Props {
  data: StockMockData
}

// ── Custom chart tooltip ────────────────────────────────────
function ChartTooltip({ active, payload, label }: {
  active?: boolean
  payload?: { name: string; value: number; color: string }[]
  label?: string
}) {
  if (!active || !payload?.length) return null
  return (
    <div
      className="rounded-lg px-3 py-2.5 text-xs"
      style={{
        background: '#0d1829',
        border: '1px solid rgba(255,255,255,0.1)',
        boxShadow: '0 8px 24px rgba(0,0,0,0.4)',
      }}
    >
      <p className="text-slate-500 mb-1.5 font-mono">{label}</p>
      {payload.map((p) => (
        <p key={p.name} className="font-mono" style={{ color: p.color }}>
          {p.name}: ₹{p.value.toFixed(2)}
        </p>
      ))}
    </div>
  )
}

// ── RSI Gauge ───────────────────────────────────────────────
function RsiGauge({ value }: { value: number }) {
  const pct = value / 100
  const isOversold  = value < 30
  const isOverbought = value > 70
  const color = isOversold ? '#10b981' : isOverbought ? '#f43f5e' : '#64748b'
  const label = isOversold ? 'Oversold' : isOverbought ? 'Overbought' : 'Neutral'

  return (
    <div>
      <div className="flex items-center justify-between mb-2">
        <span className="text-slate-500 text-[10px] uppercase tracking-[0.12em]">RSI (14)</span>
        <span className="font-mono text-sm font-bold" style={{ color }}>{value}</span>
      </div>
      {/* Zone bar */}
      <div className="relative h-2 rounded-full overflow-hidden mb-2" style={{ background: 'rgba(255,255,255,0.05)' }}>
        {/* Oversold zone 0-30 */}
        <div className="absolute left-0 top-0 h-full w-[30%] rounded-l-full" style={{ background: 'rgba(16,185,129,0.2)' }} />
        {/* Overbought zone 70-100 */}
        <div className="absolute right-0 top-0 h-full w-[30%] rounded-r-full" style={{ background: 'rgba(244,63,94,0.2)' }} />
        {/* Current marker */}
        <motion.div
          className="absolute top-1/2 -translate-y-1/2 w-2 h-2 rounded-full"
          style={{ backgroundColor: color, boxShadow: `0 0 6px ${color}`, left: `calc(${pct * 100}% - 4px)` }}
          initial={{ left: 0 }}
          animate={{ left: `calc(${pct * 100}% - 4px)` }}
          transition={{ duration: 1, delay: 0.3, ease: [0.16, 1, 0.3, 1] }}
        />
      </div>
      <div className="flex justify-between text-[9px] text-slate-700 font-mono">
        <span>0 · Oversold</span>
        <span>70 · Overbought</span>
      </div>
      <span
        className="mt-2 inline-block text-[10px] px-2 py-0.5 rounded-md font-medium"
        style={{ background: `${color}15`, color, border: `1px solid ${color}25` }}
      >
        {label}
      </span>
    </div>
  )
}

// ── MA Status card ──────────────────────────────────────────
function MaStatus({ currentPrice, ma50, ma200 }: { currentPrice: number; ma50: number; ma200: number }) {
  const above50  = currentPrice > ma50
  const above200 = currentPrice > ma200

  return (
    <div className="space-y-3">
      <p className="text-slate-500 text-[10px] uppercase tracking-[0.12em]">Moving Averages</p>
      {[
        { label: 'MA 50',  value: ma50,  above: above50,  color: '#f59e0b' },
        { label: 'MA 200', value: ma200, above: above200, color: '#8b5cf6' },
      ].map(({ label, value, above, color }) => (
        <div key={label} className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="inline-block w-3 h-0.5 rounded" style={{ background: color, boxShadow: `0 0 4px ${color}` }} />
            <span className="text-slate-500 text-xs">{label}</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="text-slate-400 text-xs font-mono">₹{value.toFixed(0)}</span>
            <span
              className="text-[10px] px-1.5 py-0.5 rounded font-medium"
              style={{
                background: above ? 'rgba(16,185,129,0.12)' : 'rgba(244,63,94,0.12)',
                color: above ? '#10b981' : '#f43f5e',
              }}
            >
              {above ? '↑ Above' : '↓ Below'}
            </span>
          </div>
        </div>
      ))}
    </div>
  )
}

// ── Trend badge ─────────────────────────────────────────────
function TrendBadge({ trend }: { trend: 'Bullish' | 'Bearish' | 'Neutral' }) {
  const cfg = {
    Bullish: { color: '#10b981', arrow: '↑', bg: 'rgba(16,185,129,0.08)', border: 'rgba(16,185,129,0.25)' },
    Bearish: { color: '#f43f5e', arrow: '↓', bg: 'rgba(244,63,94,0.08)',  border: 'rgba(244,63,94,0.25)'  },
    Neutral: { color: '#64748b', arrow: '→', bg: 'rgba(100,116,139,0.08)', border: 'rgba(100,116,139,0.25)' },
  }[trend]

  return (
    <div>
      <p className="text-slate-500 text-[10px] uppercase tracking-[0.12em] mb-3">Overall Trend</p>
      <div
        className="inline-flex items-center gap-2 px-4 py-2 rounded-xl"
        style={{ background: cfg.bg, border: `1px solid ${cfg.border}` }}
      >
        <span className="text-xl font-bold" style={{ color: cfg.color }}>{cfg.arrow}</span>
        <span className="font-semibold text-sm" style={{ color: cfg.color }}>{trend}</span>
      </div>
      <p className="text-slate-700 text-xs mt-2">Based on price action &amp; MA cross</p>
    </div>
  )
}

// ── Support / Resistance bar ─────────────────────────────────
function SRBar({ support, resistance, current }: { support: number; resistance: number; current: number }) {
  const range = resistance - support
  const pct = Math.min(Math.max(((current - support) / range) * 100, 0), 100)

  return (
    <div>
      <p className="text-slate-500 text-[10px] uppercase tracking-[0.12em] mb-3">Support &amp; Resistance</p>
      <div className="flex items-center justify-between text-xs font-mono mb-2">
        <span style={{ color: '#10b981' }}>S ₹{support.toFixed(0)}</span>
        <span className="text-slate-400">₹{current.toFixed(0)}</span>
        <span style={{ color: '#f43f5e' }}>R ₹{resistance.toFixed(0)}</span>
      </div>
      <div className="relative h-2 rounded-full overflow-hidden" style={{ background: 'rgba(255,255,255,0.05)' }}>
        <div className="absolute left-0 top-0 h-full w-full rounded-full"
          style={{ background: 'linear-gradient(90deg, rgba(16,185,129,0.3) 0%, rgba(244,63,94,0.3) 100%)' }} />
        <motion.div
          className="absolute top-1/2 -translate-y-1/2 w-2.5 h-2.5 rounded-full bg-white"
          style={{ boxShadow: '0 0 8px rgba(255,255,255,0.5)', left: `calc(${pct}% - 5px)` }}
          initial={{ left: 0 }}
          animate={{ left: `calc(${pct}% - 5px)` }}
          transition={{ duration: 1, ease: [0.16, 1, 0.3, 1] }}
        />
      </div>
    </div>
  )
}

// ── Fibonacci table ──────────────────────────────────────────
function FibTable({ levels }: { levels: { level: string; value: number }[] }) {
  return (
    <div>
      <p className="text-slate-500 text-[10px] uppercase tracking-[0.12em] mb-3">Fibonacci Retracements</p>
      <div className="space-y-1.5">
        {levels.map(({ level, value }) => (
          <div key={level} className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <span className="text-slate-700 text-[10px] font-mono">{level}</span>
              <div className="h-px w-6" style={{ background: 'rgba(251,191,36,0.3)' }} />
            </div>
            <span className="text-slate-400 text-xs font-mono">₹{value.toFixed(0)}</span>
          </div>
        ))}
      </div>
    </div>
  )
}

// ── Main component ───────────────────────────────────────────
export function TechnicalAnalysis({ data }: Props) {
  const [toolsOpen, setToolsOpen] = useState(false)
  const { technical, priceHistory } = data

  // Only show every Nth label to avoid clutter
  const labelInterval = Math.floor(priceHistory.length / 6)

  return (
    <div>
      <p className="text-slate-500 text-[10px] font-semibold uppercase tracking-[0.18em] mb-4">
        Technical Analysis
      </p>

      <motion.div
        initial={{ opacity: 0, y: 14 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4 }}
        className="rounded-xl overflow-hidden"
        style={{
          background: 'rgba(255,255,255,0.025)',
          border: '1px solid rgba(255,255,255,0.06)',
        }}
      >
        {/* Chart */}
        <div className="p-5 pb-2">
          <div className="flex items-center justify-between mb-4">
            <p className="text-slate-400 text-xs font-semibold">60-Day Price Chart</p>
            <div className="flex items-center gap-4">
              {[
                { label: 'MA50',  color: '#f59e0b' },
                { label: 'MA200', color: '#8b5cf6' },
              ].map(({ label, color }) => (
                <div key={label} className="flex items-center gap-1.5">
                  <span className="inline-block w-4 border-t border-dashed" style={{ borderColor: color }} />
                  <span className="text-[10px] text-slate-600">{label}</span>
                </div>
              ))}
            </div>
          </div>

          <ResponsiveContainer width="100%" height={200}>
            <ComposedChart data={priceHistory} margin={{ top: 4, right: 4, bottom: 0, left: 0 }}>
              <defs>
                <linearGradient id="priceGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%"  stopColor="#3b82f6" stopOpacity={0.25} />
                  <stop offset="95%" stopColor="#3b82f6" stopOpacity={0}    />
                </linearGradient>
              </defs>
              <CartesianGrid
                strokeDasharray="3 3"
                stroke="rgba(255,255,255,0.04)"
                vertical={false}
              />
              <XAxis
                dataKey="date"
                tick={{ fill: '#475569', fontSize: 10, fontFamily: 'monospace' }}
                tickLine={false}
                axisLine={false}
                interval={labelInterval}
              />
              <YAxis
                tick={{ fill: '#475569', fontSize: 10, fontFamily: 'monospace' }}
                tickLine={false}
                axisLine={false}
                domain={['auto', 'auto']}
                tickFormatter={(v: number) => `₹${v.toFixed(0)}`}
                width={62}
              />
              <Tooltip content={<ChartTooltip />} />
              <Area
                type="monotone"
                dataKey="price"
                stroke="#3b82f6"
                strokeWidth={2}
                fill="url(#priceGrad)"
                dot={false}
                name="Price"
              />
              <Line
                type="monotone"
                dataKey="ma50"
                stroke="#f59e0b"
                strokeWidth={1.5}
                strokeDasharray="4 3"
                dot={false}
                name="MA50"
              />
              <Line
                type="monotone"
                dataKey="ma200"
                stroke="#8b5cf6"
                strokeWidth={1.5}
                strokeDasharray="4 3"
                dot={false}
                name="MA200"
              />
            </ComposedChart>
          </ResponsiveContainer>
        </div>

        {/* Divider */}
        <div style={{ height: '1px', background: 'rgba(255,255,255,0.05)' }} />

        {/* Indicator row */}
        <div className="grid grid-cols-1 sm:grid-cols-3 divide-y sm:divide-y-0 sm:divide-x"
          style={{ borderColor: 'rgba(255,255,255,0.05)' }}>
          {[
            <RsiGauge key="rsi" value={technical.rsi} />,
            <TrendBadge key="trend" trend={technical.trend} />,
            <MaStatus key="ma" currentPrice={technical.currentPrice} ma50={technical.ma50} ma200={technical.ma200} />,
          ].map((el, i) => (
            <div
              key={i}
              className="p-5"
              style={{ borderColor: 'rgba(255,255,255,0.05)' }}
            >
              {el}
            </div>
          ))}
        </div>

        {/* Advanced tools toggle */}
        <div style={{ borderTop: '1px solid rgba(255,255,255,0.05)' }}>
          <button
            onClick={() => setToolsOpen((o) => !o)}
            className="w-full flex items-center justify-between px-5 py-3 transition-colors"
            style={{ color: '#64748b' }}
            onMouseEnter={(e) => ((e.currentTarget as HTMLButtonElement).style.background = 'rgba(255,255,255,0.03)')}
            onMouseLeave={(e) => ((e.currentTarget as HTMLButtonElement).style.background = 'transparent')}
          >
            <span className="text-xs font-semibold uppercase tracking-[0.15em]">
              Advanced Tools
            </span>
            <motion.span
              animate={{ rotate: toolsOpen ? 180 : 0 }}
              transition={{ duration: 0.2 }}
              className="text-xs"
            >
              ▾
            </motion.span>
          </button>

          <AnimatePresence initial={false}>
            {toolsOpen && (
              <motion.div
                initial={{ height: 0, opacity: 0 }}
                animate={{ height: 'auto', opacity: 1 }}
                exit={{ height: 0, opacity: 0 }}
                transition={{ duration: 0.28, ease: 'easeInOut' }}
                style={{ overflow: 'hidden' }}
              >
                <div
                  className="grid grid-cols-1 sm:grid-cols-2 gap-6 px-5 pt-4 pb-5"
                  style={{ borderTop: '1px solid rgba(255,255,255,0.04)' }}
                >
                  <SRBar
                    support={technical.support}
                    resistance={technical.resistance}
                    current={technical.currentPrice}
                  />
                  <FibTable levels={technical.fibonacci} />
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </motion.div>
    </div>
  )
}
