'use client'

import { motion } from 'framer-motion'
import type { StockMockData } from '@/data/mockStockData'

interface Props {
  data: StockMockData
}

type Quality = 'good' | 'warn' | 'bad' | 'neutral'

interface RatioCard {
  label: string
  value: string
  sub: string
  quality: Quality
  description: string
}

function qualityColor(q: Quality) {
  return q === 'good' ? '#10b981' : q === 'warn' ? '#f59e0b' : q === 'bad' ? '#f43f5e' : '#64748b'
}

function RatioCell({ card, index }: { card: RatioCard; index: number }) {
  const color = qualityColor(card.quality)
  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3, delay: index * 0.07 }}
      className="relative rounded-xl p-4 overflow-hidden"
      style={{
        background: 'rgba(255,255,255,0.025)',
        border: '1px solid rgba(255,255,255,0.06)',
      }}
    >
      {/* Quality accent bar */}
      <div
        className="absolute top-0 left-0 right-0 h-0.5 rounded-t-xl"
        style={{ background: `linear-gradient(90deg, ${color}80, transparent)` }}
      />

      <p className="text-slate-500 text-[10px] font-semibold uppercase tracking-[0.15em] mb-2">
        {card.label}
      </p>
      <p
        className="text-2xl font-bold font-mono tabular-nums mb-0.5"
        style={{ color: card.quality === 'neutral' ? '#e2e8f0' : color }}
      >
        {card.value}
      </p>
      <p className="text-slate-600 text-xs">{card.sub}</p>

      {/* Quality badge */}
      <div className="mt-3">
        <span
          className="text-[10px] px-2 py-0.5 rounded-md font-medium"
          style={{
            background: `${color}12`,
            color,
            border: `1px solid ${color}25`,
          }}
        >
          {card.description}
        </span>
      </div>
    </motion.div>
  )
}

export function KeyRatios({ data }: Props) {
  const { ratios } = data

  const cards: RatioCard[] = [
    {
      label: 'P/E Ratio',
      value: ratios.pe.toFixed(1) + 'x',
      sub: 'Price to Earnings',
      quality: ratios.pe < 20 ? 'good' : ratios.pe < 35 ? 'warn' : 'bad',
      description: ratios.pe < 20 ? 'Undervalued' : ratios.pe < 35 ? 'Fairly valued' : 'Overvalued',
    },
    {
      label: 'EPS',
      value: '₹' + ratios.eps.toFixed(2),
      sub: 'Earnings per Share',
      quality: ratios.eps > 50 ? 'good' : ratios.eps > 10 ? 'warn' : 'bad',
      description: ratios.eps > 50 ? 'High earnings' : ratios.eps > 10 ? 'Moderate' : 'Low earnings',
    },
    {
      label: 'ROE',
      value: ratios.roe.toFixed(1) + '%',
      sub: 'Return on Equity',
      quality: ratios.roe > 20 ? 'good' : ratios.roe > 10 ? 'warn' : 'bad',
      description: ratios.roe > 20 ? 'Excellent' : ratios.roe > 10 ? 'Acceptable' : 'Below average',
    },
    {
      label: 'Debt / Equity',
      value: ratios.debtToEquity.toFixed(2) + 'x',
      sub: 'Leverage ratio',
      quality: ratios.debtToEquity < 0.5 ? 'good' : ratios.debtToEquity < 1.5 ? 'warn' : 'bad',
      description:
        ratios.debtToEquity < 0.5 ? 'Low leverage' : ratios.debtToEquity < 1.5 ? 'Moderate debt' : 'High leverage',
    },
    {
      label: 'Market Cap',
      value: ratios.marketCap,
      sub: 'Total market value',
      quality: 'neutral',
      description: 'Large cap',
    },
    {
      label: 'Dividend Yield',
      value: ratios.dividendYield.toFixed(2) + '%',
      sub: 'Annual dividend / price',
      quality: ratios.dividendYield > 2 ? 'good' : ratios.dividendYield > 0.5 ? 'warn' : 'neutral',
      description:
        ratios.dividendYield > 2 ? 'High yield' : ratios.dividendYield > 0.5 ? 'Moderate' : 'Low yield',
    },
  ]

  return (
    <div>
      <p className="text-slate-500 text-[10px] font-semibold uppercase tracking-[0.18em] mb-4">
        Key Ratios
      </p>
      <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
        {cards.map((card, i) => (
          <RatioCell key={card.label} card={card} index={i} />
        ))}
      </div>
    </div>
  )
}
