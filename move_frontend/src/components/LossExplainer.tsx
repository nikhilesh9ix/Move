'use client'

import { motion } from 'framer-motion'
import type { WhyCardResponse } from '@/types'

interface Props {
  data: WhyCardResponse
}

interface LossAnalysis {
  whatWentWrong: string[]
  whatToLearn: string[]
}

// ── Rule engine ──────────────────────────────────────────────
function analyseLoss(data: WhyCardResponse): LossAnalysis {
  const dominant       = data.top_causes[0]
  const dominantFactor = dominant?.cause ?? data.primary_driver_label ?? 'market'
  const dominantImpact = dominant?.impact ?? 0
  const severity       = Math.abs(data.total_portfolio_change_pct)
  const isLowConf      = data.confidence_label === 'Low'

  const whatWentWrong: string[] = []
  const whatToLearn: string[]   = []

  // ── Factor-specific "what went wrong" ─────────────────────
  const factorDiagnosis: Record<string, string> = {
    sector:
      'Sector-wide selling pressure hit concentrated holdings simultaneously',
    macro:
      'Macro headwinds (rates / inflation data) triggered systematic de-risking',
    earnings:
      'Earnings revision risk crystallised — analyst downgrades accelerated selling',
    idiosyncratic:
      'Company-specific news drove an outsized move disconnected from the broader market',
    rates:
      'Rising rate environment compressed valuations across rate-sensitive positions',
  }
  whatWentWrong.push(
    factorDiagnosis[dominantFactor] ??
      `${dominantFactor} factor drove the bulk of the drawdown`
  )

  // ── Concentration ──────────────────────────────────────────
  if (dominantImpact >= 55) {
    whatWentWrong.push(
      `${dominantFactor} explained ${dominantImpact}% of the move — single-factor concentration amplified losses`
    )
  }

  // ── Severity / predictability ──────────────────────────────
  if (isLowConf) {
    whatWentWrong.push(
      'Multiple conflicting signals were active — the move was unusually hard to anticipate'
    )
  } else if (severity > 2.5) {
    whatWentWrong.push(
      `At ${severity.toFixed(1)}%, this was a larger-than-normal daily drawdown — tail-risk event`
    )
  }

  // ── Factor-specific lessons ────────────────────────────────
  const lessons: Record<string, string[]> = {
    sector: [
      'Diversify across 3+ sectors — avoid >30% in any single sector',
      'Track sector ETF flows; broad outflows often precede individual stock drops',
    ],
    macro: [
      'Mark macro event dates (Fed, RBI, CPI) in your calendar — position sizing before them matters',
      'Defensive allocations (FMCG, pharma, gold) buffer macro-driven drawdowns',
    ],
    earnings: [
      'Set stop-losses before earnings releases — surprises move stocks 5–15% overnight',
      'Check analyst consensus vs street expectations before holding through earnings',
    ],
    idiosyncratic: [
      'Cap single-stock weight at 15–20% of portfolio to limit idiosyncratic blow-ups',
      'Monitoring news feeds for held positions gives early warning on company-specific risk',
    ],
    rates: [
      'Rate-sensitive sectors (real estate, utilities) need duration hedges in hiking cycles',
      'Shorter-duration instruments and cash provide a buffer during rate-tightening phases',
    ],
  }

  whatToLearn.push(
    ...(lessons[dominantFactor] ?? [
      'Review factor concentration — diversified exposure smooths portfolio returns',
      'Set systematic stop-losses to cap drawdowns before they compound',
    ])
  )

  return {
    whatWentWrong: whatWentWrong.slice(0, 3),
    whatToLearn:   whatToLearn.slice(0, 2),
  }
}

// ── Component ────────────────────────────────────────────────
export function LossExplainer({ data }: Props) {
  // Only render on losing days
  if (data.total_portfolio_change_pct >= 0) return null

  const { whatWentWrong, whatToLearn } = analyseLoss(data)
  const lossAmt = Math.abs(data.total_portfolio_change_pct).toFixed(2)

  return (
    <motion.div
      initial={{ opacity: 0, y: 14 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, ease: 'easeOut' }}
      className="relative rounded-xl overflow-hidden"
      style={{
        background: 'linear-gradient(135deg, rgba(244,63,94,0.06) 0%, rgba(244,63,94,0.02) 100%)',
        border: '1px solid rgba(244,63,94,0.18)',
        boxShadow: '0 0 28px rgba(244,63,94,0.07), inset 0 1px 0 rgba(255,255,255,0.03)',
      }}
    >
      {/* Subtle corner glow */}
      <div
        className="absolute top-0 left-0 w-48 h-48 rounded-full pointer-events-none"
        style={{
          background: 'radial-gradient(circle, rgba(244,63,94,0.08) 0%, transparent 70%)',
          transform: 'translate(-30%, -30%)',
        }}
      />

      <div className="relative z-10 p-5">
        {/* Title row */}
        <div className="flex items-center justify-between mb-5">
          <div className="flex items-center gap-2.5">
            <div
              className="w-7 h-7 rounded-lg flex items-center justify-center shrink-0 text-sm"
              style={{
                background: 'rgba(244,63,94,0.12)',
                border: '1px solid rgba(244,63,94,0.25)',
              }}
            >
              ⚠
            </div>
            <div>
              <p
                className="text-sm font-semibold"
                style={{ color: 'rgba(251,113,133,0.95)' }}
              >
                Why you lost money
              </p>
              <p className="text-slate-600 text-[10px] mt-0.5">
                Closes the loop · loss → cause → lesson
              </p>
            </div>
          </div>
          <span
            className="text-xs font-mono font-bold px-2.5 py-1 rounded-lg shrink-0"
            style={{
              background: 'rgba(244,63,94,0.1)',
              color: '#f43f5e',
              border: '1px solid rgba(244,63,94,0.2)',
            }}
          >
            −{lossAmt}%
          </span>
        </div>

        {/* Two-col layout */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-x-6 gap-y-5">
          {/* What went wrong */}
          <div>
            <div className="flex items-center gap-1.5 mb-3">
              <span className="text-rose-500 text-xs">●</span>
              <p
                className="text-[10px] font-semibold uppercase tracking-[0.14em]"
                style={{ color: 'rgba(251,113,133,0.7)' }}
              >
                What went wrong
              </p>
            </div>
            <ul className="space-y-2.5">
              {whatWentWrong.map((item, i) => (
                <motion.li
                  key={i}
                  initial={{ opacity: 0, x: -6 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.2 + i * 0.09, duration: 0.25 }}
                  className="flex items-start gap-2.5"
                >
                  <span
                    className="w-1 h-1 rounded-full mt-1.5 shrink-0"
                    style={{ backgroundColor: '#f43f5e' }}
                  />
                  <p className="text-slate-400 text-xs leading-relaxed">{item}</p>
                </motion.li>
              ))}
            </ul>
          </div>

          {/* What to learn */}
          <div>
            <div className="flex items-center gap-1.5 mb-3">
              <span className="text-slate-500 text-xs">🧠</span>
              <p
                className="text-[10px] font-semibold uppercase tracking-[0.14em] text-slate-500"
              >
                What you can learn
              </p>
            </div>
            <ul className="space-y-2.5">
              {whatToLearn.map((item, i) => (
                <motion.li
                  key={i}
                  initial={{ opacity: 0, x: 6 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.3 + i * 0.09, duration: 0.25 }}
                  className="flex items-start gap-2.5"
                >
                  <span
                    className="w-4 h-4 rounded-md flex items-center justify-center text-[9px] font-bold shrink-0 mt-0.5"
                    style={{
                      background: 'rgba(100,116,139,0.15)',
                      color: '#94a3b8',
                      border: '1px solid rgba(100,116,139,0.2)',
                    }}
                  >
                    {i + 1}
                  </span>
                  <p className="text-slate-400 text-xs leading-relaxed">{item}</p>
                </motion.li>
              ))}
            </ul>
          </div>
        </div>
      </div>
    </motion.div>
  )
}
