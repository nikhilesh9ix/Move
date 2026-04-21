'use client'

import { motion } from 'framer-motion'
import { StockAnalyzer } from '@/components/StockAnalyzer'

const QUICK_PICKS = ['TCS', 'INFY', 'RELIANCE', 'HDFC', 'WIPRO']

export default function AnalyzePage() {
  return (
    <div className="max-w-3xl mx-auto space-y-8">
      {/* Page header */}
      <motion.div
        initial={{ opacity: 0, y: -12 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4 }}
      >
        <h1 className="text-slate-100 text-2xl font-bold tracking-tight">
          Stock analyzer
        </h1>
        <p className="text-slate-500 text-sm mt-1">
          Enter any stock to get causal attribution for a specific date
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
          <a
            key={ticker}
            href={`#${ticker}`}
            onClick={(e) => {
              e.preventDefault()
              // Pre-fill the input field by firing a custom event — handled by StockAnalyzer
              const input = document.querySelector<HTMLInputElement>('input[type="text"]')
              if (input) {
                const nativeInputValueSetter = Object.getOwnPropertyDescriptor(
                  window.HTMLInputElement.prototype,
                  'value'
                )?.set
                nativeInputValueSetter?.call(input, ticker)
                input.dispatchEvent(new Event('input', { bubbles: true }))
              }
            }}
            className="px-3 py-1 text-xs bg-slate-800 border border-slate-700 text-slate-400
                       hover:border-blue-500/50 hover:text-blue-400 rounded-lg transition-all cursor-pointer"
          >
            {ticker}
          </a>
        ))}
      </motion.div>

      {/* Main analyzer */}
      <motion.div
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
      >
        <StockAnalyzer />
      </motion.div>

      {/* How it works section */}
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
    </div>
  )
}
