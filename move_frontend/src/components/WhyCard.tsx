'use client'

import { motion } from 'framer-motion'
import { CauseBar } from './CauseBar'
import { formatCurrency } from '@/constants'
import type { WhyCardResponse } from '@/types'

interface Props {
  data: WhyCardResponse
  totalValue?: number
}

function ConfidenceRing({ pct, label }: { pct: number; label: string }) {
  const r = 22
  const circumference = 2 * Math.PI * r
  const filled = (pct / 100) * circumference
  const color =
    label === 'High' ? '#10b981' : label === 'Medium' ? '#f59e0b' : '#64748b'
  const trackColor =
    label === 'High' ? '#10b98120' : label === 'Medium' ? '#f59e0b20' : '#64748b20'

  return (
    <div className="flex items-center gap-4">
      <div className="relative">
        <svg
          width="56"
          height="56"
          viewBox="0 0 56 56"
          style={{ transform: 'rotate(-90deg)' }}
        >
          <circle cx="28" cy="28" r={r} fill="none" stroke={trackColor} strokeWidth="3.5" />
          <motion.circle
            cx="28"
            cy="28"
            r={r}
            fill="none"
            stroke={color}
            strokeWidth="3.5"
            strokeLinecap="round"
            strokeDasharray={`${filled} ${circumference}`}
            initial={{ strokeDasharray: `0 ${circumference}` }}
            animate={{ strokeDasharray: `${filled} ${circumference}` }}
            transition={{ duration: 1.2, delay: 0.4, ease: [0.16, 1, 0.3, 1] }}
            style={{ filter: `drop-shadow(0 0 5px ${color}90)` }}
          />
        </svg>
        <div
          className="absolute inset-0 flex items-center justify-center font-bold text-xs font-mono"
          style={{ color }}
        >
          {pct}
        </div>
      </div>
      <div>
        <div className="text-xs font-semibold" style={{ color }}>
          {label} confidence
        </div>
        <div className="text-slate-600 text-xs mt-0.5">AI certainty score</div>
      </div>
    </div>
  )
}

function PrimaryDriverBadge({ label }: { label: string }) {
  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ delay: 0.35, duration: 0.3 }}
      className="inline-flex items-center gap-2 px-3 py-1.5 rounded-lg"
      style={{
        background: 'rgba(59,130,246,0.08)',
        border: '1px solid rgba(59,130,246,0.25)',
        boxShadow: '0 0 12px rgba(59,130,246,0.1)',
      }}
    >
      <span
        className="w-1.5 h-1.5 rounded-full bg-blue-400"
        style={{ boxShadow: '0 0 6px #60a5fa' }}
      />
      <span className="text-xs text-slate-400">Primary driver</span>
      <span className="text-xs font-semibold text-blue-300 capitalize">{label}</span>
    </motion.div>
  )
}

export function WhyCard({ data, totalValue }: Props) {
  const isLoss = data.total_portfolio_change_pct < 0
  const changeColor = isLoss ? '#f43f5e' : '#10b981'
  const changeGradient = isLoss
    ? 'linear-gradient(135deg, #f43f5e, #fb7185)'
    : 'linear-gradient(135deg, #10b981, #34d399)'
  const changeArrow = isLoss ? '▼' : '▲'
  const dollarChange =
    totalValue != null
      ? totalValue * (data.total_portfolio_change_pct / 100)
      : null

  const heroValue =
    dollarChange != null
      ? formatCurrency(Math.abs(dollarChange))
      : `${Math.abs(data.total_portfolio_change_pct).toFixed(2)}%`

  return (
    <motion.div
      initial={{ opacity: 0, y: 24 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.45, ease: 'easeOut' }}
      className="relative rounded-2xl overflow-hidden h-full flex flex-col"
      style={{
        background: 'linear-gradient(160deg, #0d1829 0%, #050e1a 60%, #020617 100%)',
        border: '1px solid rgba(255,255,255,0.06)',
        boxShadow:
          '0 0 0 1px rgba(255,255,255,0.03), 0 24px 48px -12px rgba(0,0,0,0.6), inset 0 1px 0 rgba(255,255,255,0.04)',
      }}
    >
      {/* Ambient glow behind hero number */}
      <div
        className="absolute top-0 left-0 w-64 h-64 rounded-full pointer-events-none"
        style={{
          background: isLoss
            ? 'radial-gradient(circle, rgba(244,63,94,0.07) 0%, transparent 70%)'
            : 'radial-gradient(circle, rgba(16,185,129,0.07) 0%, transparent 70%)',
          transform: 'translate(-30%, -30%)',
        }}
      />

      <div className="relative z-10 p-7 flex flex-col h-full">
        {/* Header */}
        <div className="flex items-center justify-between mb-7">
          <p className="text-slate-500 text-[10px] font-semibold uppercase tracking-[0.18em]">
            Why did your portfolio move?
          </p>
          <span
            className="text-slate-500 text-xs font-mono px-2.5 py-1 rounded-md"
            style={{
              background: 'rgba(255,255,255,0.04)',
              border: '1px solid rgba(255,255,255,0.06)',
            }}
          >
            {data.date}
          </span>
        </div>

        {/* Hero number */}
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1, duration: 0.5 }}
          className="mb-2"
        >
          <p className="text-slate-500 text-xs mb-2">Today&apos;s portfolio change</p>
          <div className="flex items-end gap-3 flex-wrap">
            <span
              className="text-5xl font-bold font-mono tabular-nums leading-none"
              style={{
                background: changeGradient,
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
                backgroundClip: 'text',
                filter: `drop-shadow(0 0 20px ${changeColor}40)`,
              }}
            >
              {heroValue}
            </span>
            <div className="flex items-center gap-1.5 mb-1">
              <span
                className="text-base font-mono font-semibold tabular-nums"
                style={{ color: changeColor }}
              >
                {changeArrow} {Math.abs(data.total_portfolio_change_pct).toFixed(2)}%
              </span>
            </div>
          </div>
        </motion.div>

        {/* Primary driver + Confidence row */}
        <div className="flex items-center gap-3 flex-wrap mb-7">
          {data.primary_driver_label && (
            <PrimaryDriverBadge label={data.primary_driver_label} />
          )}
          {data.confidence_pct > 0 && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.3 }}
            >
              <ConfidenceRing
                pct={data.confidence_pct}
                label={data.confidence_label || 'Medium'}
              />
            </motion.div>
          )}
        </div>

        {/* Divider */}
        <div
          className="mb-5"
          style={{
            height: '1px',
            background:
              'linear-gradient(90deg, rgba(255,255,255,0.06) 0%, transparent 100%)',
          }}
        />

        {/* Cause bars */}
        <div className="flex-1">
          <p className="text-slate-500 text-[10px] font-semibold uppercase tracking-[0.18em] mb-4">
            Factor breakdown
          </p>
          <div className="space-y-3.5">
            {data.top_causes.map((cause, i) => (
              <CauseBar
                key={cause.cause}
                cause={cause}
                index={i}
                animationDelay={0.3}
                isPrimary={i === 0}
              />
            ))}
          </div>
        </div>

        {/* Explanation */}
        <div
          className="mt-6 pt-5"
          style={{ borderTop: '1px solid rgba(255,255,255,0.05)' }}
        >
          <p
            className="text-slate-300 text-sm leading-relaxed"
            style={{ textWrap: 'pretty' } as React.CSSProperties}
          >
            {data.explanation_summary}
          </p>
        </div>
      </div>
    </motion.div>
  )
}
