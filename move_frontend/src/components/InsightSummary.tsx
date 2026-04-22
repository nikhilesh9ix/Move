'use client'

import { motion } from 'framer-motion'
import type { StockMockData } from '@/data/mockStockData'

interface Props {
  data: StockMockData
  ticker: string
}

type Verdict = 'Bullish' | 'Bearish' | 'Neutral'

interface Signal {
  label: string
  detail: string
  weight: number  // how much it contributed
}

interface Insight {
  verdict: Verdict
  score: number
  positives: Signal[]
  negatives: Signal[]
  narrative: string
  tags: string[]
}

// ── Rule engine ──────────────────────────────────────────────
function buildInsight(data: StockMockData, ticker: string): Insight {
  const { ratios, technical, revenueGrowth, profitGrowth, balance } = data
  let score = 0
  const positives: Signal[] = []
  const negatives: Signal[] = []
  const tags: string[] = []

  // ── Fundamental signals ──────────────────────────────────

  if (revenueGrowth > 8) {
    score += 1
    positives.push({ label: 'Strong revenue growth', detail: `+${revenueGrowth.toFixed(1)}% YoY`, weight: 1 })
    tags.push('Revenue ↑')
  } else if (revenueGrowth > 0) {
    positives.push({ label: 'Steady revenue growth', detail: `+${revenueGrowth.toFixed(1)}% YoY`, weight: 0.5 })
    tags.push('Revenue ↑')
  } else {
    score -= 1
    negatives.push({ label: 'Revenue declining', detail: `${revenueGrowth.toFixed(1)}% YoY`, weight: 1 })
    tags.push('Revenue ↓')
  }

  if (profitGrowth > 10) {
    score += 1
    positives.push({ label: 'Expanding profit margins', detail: `+${profitGrowth.toFixed(1)}% profit growth`, weight: 1 })
    tags.push('Profit ↑')
  } else if (profitGrowth < 0) {
    score -= 1
    negatives.push({ label: 'Compressing profits', detail: `${profitGrowth.toFixed(1)}% profit growth`, weight: 1 })
    tags.push('Profit ↓')
  }

  if (balance.healthLabel === 'Strong') {
    score += 1
    positives.push({ label: 'Healthy balance sheet', detail: `${balance.cash} cash vs ${balance.totalDebt} debt`, weight: 1 })
    tags.push('Low Debt')
  } else if (balance.healthLabel === 'Weak') {
    score -= 1
    negatives.push({ label: 'Elevated debt burden', detail: `Health score ${balance.healthScore}/100`, weight: 1 })
    tags.push('High Debt')
  }

  // ── Valuation signals ─────────────────────────────────────

  if (ratios.pe > 35) {
    score -= 1
    negatives.push({ label: 'High valuation', detail: `P/E ${ratios.pe.toFixed(1)}x — above fair value`, weight: 1 })
    tags.push('Overvalued')
  } else if (ratios.pe < 15) {
    score += 1
    positives.push({ label: 'Attractively valued', detail: `P/E ${ratios.pe.toFixed(1)}x — potential upside`, weight: 1 })
    tags.push('Undervalued')
  } else {
    tags.push('Fair Value')
  }

  if (ratios.roe > 25) {
    score += 1
    positives.push({ label: 'Exceptional capital efficiency', detail: `ROE ${ratios.roe.toFixed(1)}% — top quartile`, weight: 1 })
    tags.push('High ROE')
  } else if (ratios.roe < 10) {
    score -= 1
    negatives.push({ label: 'Weak capital efficiency', detail: `ROE ${ratios.roe.toFixed(1)}% — below benchmark`, weight: 0.8 })
  }

  // ── Technical signals ─────────────────────────────────────

  const maGoldenCross = technical.ma50 > technical.ma200
  if (maGoldenCross) {
    score += 1
    positives.push({ label: 'Golden cross in play', detail: `MA50 (₹${technical.ma50}) above MA200 (₹${technical.ma200})`, weight: 1 })
    tags.push('Golden Cross')
  } else {
    score -= 1
    negatives.push({ label: 'Death cross active', detail: `MA50 (₹${technical.ma50}) below MA200 (₹${technical.ma200})`, weight: 1 })
    tags.push('Death Cross')
  }

  if (technical.rsi > 70) {
    score -= 1
    negatives.push({ label: 'Overbought — correction risk', detail: `RSI ${technical.rsi} — well above 70 threshold`, weight: 1 })
    tags.push('Overbought')
  } else if (technical.rsi < 30) {
    score += 1
    positives.push({ label: 'Oversold — bounce potential', detail: `RSI ${technical.rsi} — below 30 support level`, weight: 1 })
    tags.push('Oversold')
  } else if (technical.rsi >= 45 && technical.rsi <= 60) {
    positives.push({ label: 'RSI in healthy zone', detail: `RSI ${technical.rsi} — momentum intact`, weight: 0.5 })
    tags.push('RSI Neutral')
  }

  const priceVsRange =
    ((technical.currentPrice - technical.support) / (technical.resistance - technical.support)) * 100
  if (priceVsRange < 25) {
    score += 0.5
    positives.push({ label: 'Near strong support', detail: `₹${technical.currentPrice} close to ₹${technical.support} support`, weight: 0.5 })
  } else if (priceVsRange > 80) {
    negatives.push({ label: 'Near key resistance', detail: `₹${technical.currentPrice} approaching ₹${technical.resistance} ceiling`, weight: 0.5 })
  }

  // ── Sort by weight, cap at top 2 ─────────────────────────
  const top2 = (arr: Signal[]) =>
    [...arr].sort((a, b) => b.weight - a.weight).slice(0, 2)

  const topPositives = top2(positives)
  const topNegatives = top2(negatives)

  // ── Verdict ───────────────────────────────────────────────
  const verdict: Verdict = score >= 2 ? 'Bullish' : score <= -2 ? 'Bearish' : 'Neutral'

  // ── Narrative sentence ────────────────────────────────────
  const posPhrase = topPositives.map((p) => p.label.toLowerCase()).join(' and ')
  const negPhrase = topNegatives.map((n) => n.label.toLowerCase()).join(' and ')

  const openings: Record<Verdict, string> = {
    Bullish:  `${ticker} looks compelling`,
    Bearish:  `${ticker} carries meaningful risk`,
    Neutral:  `${ticker} presents a mixed picture`,
  }

  let narrative = openings[verdict]

  if (posPhrase && negPhrase) {
    const connector: Record<Verdict, string> = {
      Bullish: ', driven primarily by',
      Bearish: ' — despite',
      Neutral: ', balancing',
    }
    const caveat: Record<Verdict, string> = {
      Bullish: ', though investors should watch for',
      Bearish: ', the stock is weighed down by',
      Neutral: ' against headwinds from',
    }
    narrative += `${connector[verdict]} ${posPhrase}${caveat[verdict]} ${negPhrase}.`
  } else if (posPhrase) {
    narrative += `, supported by ${posPhrase} with no major red flags.`
  } else if (negPhrase) {
    narrative += ` — ${negPhrase} dominate the risk picture here.`
  } else {
    narrative += ' with no strong directional signals at this time.'
  }

  return {
    verdict,
    score,
    positives: topPositives,
    negatives: topNegatives,
    narrative,
    tags,
  }
}

// ── Verdict config ───────────────────────────────────────────
const VERDICT_CONFIG = {
  Bullish: {
    color: '#10b981',
    bg: 'linear-gradient(135deg, rgba(16,185,129,0.07) 0%, rgba(16,185,129,0.025) 100%)',
    border: 'rgba(16,185,129,0.2)',
    glow: 'rgba(16,185,129,0.1)',
    icon: '↑',
  },
  Bearish: {
    color: '#f43f5e',
    bg: 'linear-gradient(135deg, rgba(244,63,94,0.07) 0%, rgba(244,63,94,0.025) 100%)',
    border: 'rgba(244,63,94,0.2)',
    glow: 'rgba(244,63,94,0.1)',
    icon: '↓',
  },
  Neutral: {
    color: '#f59e0b',
    bg: 'linear-gradient(135deg, rgba(245,158,11,0.06) 0%, rgba(245,158,11,0.02) 100%)',
    border: 'rgba(245,158,11,0.2)',
    glow: 'rgba(245,158,11,0.08)',
    icon: '→',
  },
}

// ── Signal row ───────────────────────────────────────────────
function SignalRow({
  signal,
  type,
  index,
}: {
  signal: Signal
  type: 'positive' | 'negative'
  index: number
}) {
  const color   = type === 'positive' ? '#10b981' : '#f43f5e'
  const icon    = type === 'positive' ? '+' : '−'

  return (
    <motion.div
      initial={{ opacity: 0, x: type === 'positive' ? -8 : 8 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ delay: 0.3 + index * 0.08, duration: 0.25 }}
      className="flex items-start gap-2.5"
    >
      <span
        className="w-4 h-4 rounded-md flex items-center justify-center text-[10px] font-bold shrink-0 mt-0.5"
        style={{ background: `${color}18`, color, border: `1px solid ${color}28` }}
      >
        {icon}
      </span>
      <div>
        <p className="text-xs font-medium" style={{ color: 'rgba(226,232,240,0.85)' }}>
          {signal.label}
        </p>
        <p className="text-[10px] mt-0.5" style={{ color: '#64748b' }}>
          {signal.detail}
        </p>
      </div>
    </motion.div>
  )
}

// ── Main component ───────────────────────────────────────────
export function InsightSummary({ data, ticker }: Props) {
  const insight = buildInsight(data, ticker)
  const cfg     = VERDICT_CONFIG[insight.verdict]

  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, ease: 'easeOut' }}
      className="relative rounded-xl overflow-hidden"
      style={{
        background: cfg.bg,
        border: `1px solid ${cfg.border}`,
        boxShadow: `0 0 32px ${cfg.glow}, inset 0 1px 0 rgba(255,255,255,0.04)`,
      }}
    >
      {/* Ambient corner glow */}
      <div
        className="absolute top-0 right-0 w-56 h-56 rounded-full pointer-events-none"
        style={{
          background: `radial-gradient(circle, ${cfg.glow} 0%, transparent 70%)`,
          transform: 'translate(35%, -35%)',
        }}
      />

      <div className="relative z-10 p-5">
        {/* Header */}
        <div className="flex items-start justify-between mb-4">
          <div className="flex items-center gap-2.5">
            <div
              className="w-8 h-8 rounded-lg flex items-center justify-center shrink-0 text-base font-bold"
              style={{
                background: `${cfg.color}18`,
                border: `1px solid ${cfg.color}35`,
                color: cfg.color,
              }}
            >
              {cfg.icon}
            </div>
            <div>
              <p className="text-[10px] font-semibold uppercase tracking-[0.18em]" style={{ color: cfg.color }}>
                AI Insight Summary
              </p>
              <p className="text-slate-600 text-[10px] mt-0.5">
                Fundamentals · Ratios · Technicals
              </p>
            </div>
          </div>

          {/* Verdict badge */}
          <motion.div
            initial={{ opacity: 0, scale: 0.85 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.15, duration: 0.3 }}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg shrink-0"
            style={{ background: `${cfg.color}15`, border: `1px solid ${cfg.color}30` }}
          >
            <span
              className="w-1.5 h-1.5 rounded-full"
              style={{ backgroundColor: cfg.color, boxShadow: `0 0 6px ${cfg.color}` }}
            />
            <span className="text-sm font-bold" style={{ color: cfg.color }}>
              {insight.verdict}
            </span>
          </motion.div>
        </div>

        {/* Narrative */}
        <motion.p
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.2, duration: 0.35 }}
          className="text-sm leading-relaxed mb-5"
          style={{ color: 'rgba(203,213,225,0.88)' }}
        >
          {insight.narrative}
        </motion.p>

        {/* Signals grid */}
        {(insight.positives.length > 0 || insight.negatives.length > 0) && (
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-x-6 gap-y-4 mb-5">
            {/* Positive drivers */}
            {insight.positives.length > 0 && (
              <div>
                <div className="flex items-center gap-1.5 mb-3">
                  <span className="text-emerald-600 text-[10px] font-bold">✔</span>
                  <p className="text-[10px] font-semibold uppercase tracking-[0.14em] text-emerald-600">
                    Positive Drivers
                  </p>
                </div>
                <div className="space-y-3">
                  {insight.positives.map((s, i) => (
                    <SignalRow key={s.label} signal={s} type="positive" index={i} />
                  ))}
                </div>
              </div>
            )}

            {/* Risk factors */}
            {insight.negatives.length > 0 && (
              <div>
                <div className="flex items-center gap-1.5 mb-3">
                  <span className="text-rose-500 text-[10px] font-bold">⚠</span>
                  <p className="text-[10px] font-semibold uppercase tracking-[0.14em] text-rose-500">
                    Risk Factors
                  </p>
                </div>
                <div className="space-y-3">
                  {insight.negatives.map((s, i) => (
                    <SignalRow key={s.label} signal={s} type="negative" index={i} />
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {/* Divider + Tags */}
        <div
          className="flex flex-wrap gap-1.5 pt-4"
          style={{ borderTop: '1px solid rgba(255,255,255,0.05)' }}
        >
          {insight.tags.map((tag, i) => (
            <motion.span
              key={tag}
              initial={{ opacity: 0, y: 3 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.45 + i * 0.04 }}
              className="text-[10px] px-2 py-0.5 rounded-md font-mono"
              style={{
                background: 'rgba(255,255,255,0.04)',
                color: '#475569',
                border: '1px solid rgba(255,255,255,0.07)',
              }}
            >
              {tag}
            </motion.span>
          ))}
        </div>
      </div>
    </motion.div>
  )
}
