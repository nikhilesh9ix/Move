'use client'

import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { StockAnalyzer } from '@/components/StockAnalyzer'
import { Fundamentals } from '@/components/Fundamentals'
import { KeyRatios } from '@/components/KeyRatios'
import { TechnicalAnalysis } from '@/components/TechnicalAnalysis'
import { getMockData } from '@/data/mockStockData'
import { InsightSummary } from '@/components/InsightSummary'

const QUICK_PICKS = ['TCS', 'INFY', 'RELIANCE', 'HDFC', 'WIPRO']

export default function AnalyzePage() {
  const [analyzedStock, setAnalyzedStock] = useState<string | null>(null)
  const mockData = analyzedStock ? getMockData(analyzedStock) : null

  return (
    <div className="max-w-5xl mx-auto space-y-8">
      {/* Page header */}
      <motion.div
        initial={{ opacity: 0, y: -12 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4 }}
      >
        <h1 className="text-slate-100 text-2xl font-bold tracking-tight">Stock analyzer</h1>
        <p className="text-slate-500 text-sm mt-1">
          Enter any stock to get causal attribution and fundamental analysis
        </p>
      </motion.div>

      {/* Quick pick chips */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.15 }}
        className="flex flex-wrap gap-2"
      >
        <span className="text-slate-600 text-xs self-center">Quick picks:</span>
        {QUICK_PICKS.map((ticker) => (
          <button
            key={ticker}
            onClick={() => {
              // Pre-fill the text input
              const input = document.querySelector<HTMLInputElement>('input[type="text"]')
              if (input) {
                const setter = Object.getOwnPropertyDescriptor(
                  window.HTMLInputElement.prototype,
                  'value'
                )?.set
                setter?.call(input, ticker)
                input.dispatchEvent(new Event('input', { bubbles: true }))
              }
            }}
            className="px-3 py-1 text-xs bg-slate-800 border border-slate-700 text-slate-400
                       hover:border-blue-500/50 hover:text-blue-400 rounded-lg transition-all cursor-pointer"
          >
            {ticker}
          </button>
        ))}
      </motion.div>

      {/* Main analyzer */}
      <motion.div
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
      >
        <StockAnalyzer onAnalyze={setAnalyzedStock} />
      </motion.div>

      {/* ─── Financial insight sections (appear after analysis) ─── */}
      <AnimatePresence>
        {mockData && (
          <motion.div
            key={analyzedStock}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.45, ease: 'easeOut' }}
            className="space-y-8"
          >
            {/* Stock identity header */}
            <div
              className="flex items-center gap-3 px-5 py-3 rounded-xl"
              style={{
                background: 'rgba(59,130,246,0.05)',
                border: '1px solid rgba(59,130,246,0.12)',
              }}
            >
              <div
                className="w-8 h-8 rounded-lg flex items-center justify-center shrink-0"
                style={{ background: 'rgba(59,130,246,0.12)', border: '1px solid rgba(59,130,246,0.2)' }}
              >
                <span className="text-blue-300 font-bold text-xs">
                  {analyzedStock!.slice(0, 2)}
                </span>
              </div>
              <div>
                <p className="text-slate-200 text-sm font-semibold">{mockData.name}</p>
                <p className="text-slate-500 text-xs">{mockData.sector}</p>
              </div>
              <span
                className="ml-auto text-[10px] px-2 py-0.5 rounded-md font-medium"
                style={{
                  background: 'rgba(59,130,246,0.1)',
                  color: '#93c5fd',
                  border: '1px solid rgba(59,130,246,0.2)',
                }}
              >
                {analyzedStock}
              </span>
            </div>

            <InsightSummary data={mockData} ticker={analyzedStock!} />

            <Fundamentals data={mockData} />

            <div
              className="pt-2"
              style={{ borderTop: '1px solid rgba(255,255,255,0.05)' }}
            >
              <KeyRatios data={mockData} />
            </div>

            <div
              className="pt-2"
              style={{ borderTop: '1px solid rgba(255,255,255,0.05)' }}
            >
              <TechnicalAnalysis data={mockData} />
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* How it works — only when no analysis shown */}
      {!analyzedStock && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.5 }}
          className="border-t border-slate-800/60 pt-6"
        >
          <p className="text-slate-600 text-xs font-medium uppercase tracking-widest mb-4">
            How it works
          </p>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            {[
              {
                step: '01',
                title: 'Price signal',
                desc: 'Detects abnormal moves using rolling volatility baselines',
              },
              {
                step: '02',
                title: 'Factor decomposition',
                desc: 'Attributes returns to market, sector, rates, and earnings factors',
              },
              {
                step: '03',
                title: 'AI explanation',
                desc: 'Generates a grounded, source-cited natural language explanation',
              },
            ].map(({ step, title, desc }) => (
              <div
                key={step}
                className="bg-slate-900/50 border border-slate-800/60 rounded-xl p-4"
              >
                <span className="text-blue-500/60 text-xs font-mono font-bold">{step}</span>
                <h3 className="text-slate-300 text-sm font-semibold mt-1 mb-1">{title}</h3>
                <p className="text-slate-600 text-xs leading-relaxed">{desc}</p>
              </div>
            ))}
          </div>
        </motion.div>
      )}
    </div>
  )
}
