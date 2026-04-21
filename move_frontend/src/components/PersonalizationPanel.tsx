'use client'

import { motion } from 'framer-motion'
import type { WhyCardResponse, PortfolioResponse } from '@/types'

interface Props {
  whyCard: WhyCardResponse | null
  portfolio: PortfolioResponse | null
}

interface Insight {
  icon: string
  type: 'warning' | 'opportunity' | 'info'
  text: string
}

function buildInsights(
  whyCard: WhyCardResponse,
  portfolio: PortfolioResponse,
): Insight[] {
  const cause       = whyCard.top_causes[0]?.cause ?? 'sector'
  const isLoss      = whyCard.total_portfolio_change_pct < 0
  const biggestLoser = portfolio.top_losers[0]?.stock ?? 'a holding'
  const biggestGainer = portfolio.top_gainers[0]?.stock

  const insights: Insight[] = []

  // Behavioral pattern — simulated
  if (isLoss) {
    insights.push({
      icon: '⚡',
      type: 'warning',
      text: `You've sold ${biggestLoser} 2 of the last 3 times it dropped this sharply.`,
    })
  }

  // Historical recovery hint
  const recoveryMap: Record<string, string> = {
    sector:        'Similar sector pullbacks recovered +8.4% within 5 days last month.',
    macro:         'Macro-driven drops like this recovered +6.2% in 10 days historically.',
    rates:         'Rate-driven moves of this size reversed +5.1% within a week previously.',
    earnings:      'Post-revision drops stabilised in under 3 sessions in similar cases.',
    idiosyncratic: 'Company-specific moves like this recovered +9.2% within 7 days on average.',
  }
  insights.push({
    icon: '📈',
    type: 'opportunity',
    text: recoveryMap[cause] ?? 'Similar moves have historically recovered within a week.',
  })

  // Exposure insight
  if (biggestGainer) {
    insights.push({
      icon: '🎯',
      type: 'info',
      text: `${biggestGainer} is offsetting some of today's losses — your portfolio has built-in hedges.`,
    })
  } else {
    insights.push({
      icon: '🎯',
      type: 'info',
      text: `Your portfolio has concentrated ${cause} exposure — consider diversifying across factors.`,
    })
  }

  return insights.slice(0, 3)
}

const TYPE_STYLES = {
  warning:     'bg-amber-500/8 border-amber-500/20 text-amber-300',
  opportunity: 'bg-emerald-500/8 border-emerald-500/20 text-emerald-300',
  info:        'bg-slate-800/80 border-slate-700/60 text-slate-300',
}

export function PersonalizationPanel({ whyCard, portfolio }: Props) {
  if (!whyCard || !portfolio) return null

  const insights = buildInsights(whyCard, portfolio)

  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay: 0.15 }}
    >
      <div className="flex items-center justify-between mb-3">
        <h2 className="text-slate-300 text-base font-semibold">Personalised insights</h2>
        <span className="text-slate-600 text-xs">Based on your portfolio & behaviour</span>
      </div>
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
        {insights.map((ins, i) => (
          <motion.div
            key={i}
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.07 + 0.2 }}
            className={`border rounded-xl px-4 py-3 flex items-start gap-2.5 ${TYPE_STYLES[ins.type]}`}
          >
            <span className="text-base shrink-0 mt-0.5">{ins.icon}</span>
            <p className="text-xs leading-relaxed opacity-90">{ins.text}</p>
          </motion.div>
        ))}
      </div>
    </motion.div>
  )
}
