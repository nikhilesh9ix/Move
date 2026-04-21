'use client'

import { motion } from 'framer-motion'
import { WhyCard } from '@/components/WhyCard'
import { PortfolioSummary } from '@/components/PortfolioSummary'
import { AttributionChart } from '@/components/AttributionChart'
import { LiveFeed } from '@/components/LiveFeed'
import { LiveStatus } from '@/components/LiveStatus'
import { DemoFlow } from '@/components/DemoFlow'
import { EventAlert } from '@/components/EventAlert'
import { InsightCard } from '@/components/InsightCard'
import { PersonalizationPanel } from '@/components/PersonalizationPanel'
import { WhyCardSkeleton, PortfolioSkeleton, ChartSkeleton } from '@/components/LoadingSkeleton'
import { useWhyCard } from '@/hooks/useWhyCard'
import { usePortfolio } from '@/hooks/usePortfolio'
import { useRealtimeUpdates } from '@/hooks/useRealtimeUpdates'
import { DEFAULT_DATE } from '@/constants'

export default function DashboardPage() {
  // REST data
  const { data: whyCard, loading: whyLoading } = useWhyCard(DEFAULT_DATE)
  const { data: portfolio, loading: portLoading, error: portError } = usePortfolio(DEFAULT_DATE)

  // Real-time WebSocket data
  const { events, latestTicker, connected } = useRealtimeUpdates()

  // Patch WhyCard with freshest live attribution when available
  const liveWhyCard = latestTicker && events[latestTicker]
    ? {
        ...(whyCard ?? {
          date: DEFAULT_DATE,
          total_portfolio_change_pct: 0,
          top_causes: [],
          explanation_summary: '',
          confidence_pct: 70,
          confidence_label: 'Medium',
          primary_driver_label: '',
        }),
        top_causes:
          events[latestTicker].attribution?.map((a) => ({
            cause: a.factor,
            impact: a.contribution,
          })) ?? whyCard?.top_causes ?? [],
        explanation_summary:
          events[latestTicker].explanation ?? whyCard?.explanation_summary ?? '',
      }
    : whyCard

  const portfolioAttribution = liveWhyCard?.top_causes?.map((c) => ({
    factor: c.cause,
    contribution: c.impact,
  }))

  const liveEventCount = Object.keys(events).length
  const backendDown    = portError && !connected

  return (
    <>
      {/* Guided demo tour — floating bottom-right, auto-dismisses */}
      <DemoFlow />

      <div className="space-y-8">
        {/* ── Page header ── */}
        <motion.div
          initial={{ opacity: 0, y: -12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4 }}
          className="flex items-start justify-between"
        >
          <div>
            <h1 className="text-slate-100 text-2xl font-bold tracking-tight">
              Good evening.
            </h1>
            <p className="text-slate-500 text-sm mt-1">
              Here&apos;s why your portfolio moved on{' '}
              <span className="text-slate-400 font-mono">{DEFAULT_DATE}</span>
            </p>
          </div>
          <LiveStatus connected={connected} eventCount={liveEventCount} />
        </motion.div>

        {/* ── Event alert — only when |change| ≥ 1.5% ── */}
        {!whyLoading && liveWhyCard && (
          <EventAlert data={liveWhyCard} />
        )}

        {/* ── Backend offline warning ── */}
        {backendDown && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="bg-amber-500/10 border border-amber-500/30 rounded-xl px-5 py-3"
          >
            <p className="text-amber-400 text-sm">
              Cannot reach backend.{' '}
              <span className="font-mono text-amber-500">uvicorn main:app --reload</span> in{' '}
              <span className="font-mono">move_backend/</span> then refresh.
            </p>
          </motion.div>
        )}

        {/* ── Hero grid: WhyCard + PortfolioSummary ── */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">
          <div className="lg:col-span-2">
            {whyLoading ? (
              <WhyCardSkeleton />
            ) : liveWhyCard ? (
              <WhyCard data={liveWhyCard} totalValue={portfolio?.total_value} />
            ) : null}
          </div>
          <div className="lg:col-span-1">
            {portLoading ? (
              <PortfolioSkeleton />
            ) : portfolio ? (
              <PortfolioSummary data={portfolio} />
            ) : null}
          </div>
        </div>

        {/* ── Personalised insights ── */}
        {!whyLoading && !portLoading && (
          <PersonalizationPanel whyCard={liveWhyCard ?? null} portfolio={portfolio ?? null} />
        )}

        {/* ── Attribution chart ── */}
        <div>
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-slate-300 text-base font-semibold">Portfolio attribution</h2>
            <span className="text-slate-600 text-xs">Weighted across all holdings</span>
          </div>
          {whyLoading ? (
            <ChartSkeleton />
          ) : portfolioAttribution ? (
            <AttributionChart
              attribution={portfolioAttribution}
              title="Portfolio-level factor breakdown"
            />
          ) : null}
        </div>

        {/* ── Insight card: "If you held" + top insight ── */}
        {!whyLoading && liveWhyCard && (
          <div>
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-slate-300 text-base font-semibold">Intelligence</h2>
              <span className="text-slate-600 text-xs">Pattern matching · simulated history</span>
            </div>
            <InsightCard data={liveWhyCard} totalValue={portfolio?.total_value} />
          </div>
        )}

        {/* ── Real-time feed ── */}
        <div>
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-slate-300 text-base font-semibold">Real-time feed</h2>
            <div className="flex items-center gap-2">
              {connected && (
                <span className="text-slate-600 text-xs">
                  Polling every 20 s · threshold ±0.8%
                </span>
              )}
              <LiveStatus connected={connected} />
            </div>
          </div>
          <LiveFeed events={events} latestTicker={latestTicker} />
        </div>

        {/* ── Footer ── */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.8 }}
          className="text-center py-4"
        >
          <p className="text-slate-700 text-xs">
            Want to dig deeper?{' '}
            <a href="/analyze" className="text-blue-600 hover:text-blue-400 transition-colors">
              Analyse a specific stock →
            </a>
          </p>
        </motion.div>
      </div>
    </>
  )
}
