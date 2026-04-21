'use client'

import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { AttributionChart } from './AttributionChart'
import { PriceChange } from './PriceChange'
import { useAnalysis } from '@/hooks/useAnalysis'
import { DEFAULT_DATE } from '@/constants'

export function StockAnalyzer() {
  const [stock, setStock] = useState('')
  const [date, setDate] = useState(DEFAULT_DATE)
  const { data, loading, error, analyze } = useAnalysis()

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    if (stock.trim()) analyze(stock.trim().toUpperCase(), date)
  }

  return (
    <div className="space-y-5">
      {/* Search form */}
      <form onSubmit={handleSubmit} className="flex gap-3 flex-wrap">
        <input
          type="text"
          value={stock}
          onChange={(e) => setStock(e.target.value)}
          placeholder="e.g. TCS, INFY, RELIANCE"
          className="flex-1 min-w-0 bg-slate-900 border border-slate-700 rounded-xl px-4 py-3 text-slate-100
                     placeholder-slate-600 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/50
                     focus:border-blue-500/50 transition-all"
        />
        <input
          type="date"
          value={date}
          onChange={(e) => setDate(e.target.value)}
          className="bg-slate-900 border border-slate-700 rounded-xl px-4 py-3 text-slate-300 text-sm
                     focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500/50 transition-all"
        />
        <button
          type="submit"
          disabled={loading || !stock.trim()}
          className="bg-blue-600 hover:bg-blue-500 disabled:bg-slate-800 disabled:text-slate-600
                     text-white px-6 py-3 rounded-xl text-sm font-medium transition-all duration-150
                     shadow-lg shadow-blue-500/20 hover:shadow-blue-500/30 disabled:shadow-none"
        >
          {loading ? (
            <span className="flex items-center gap-2">
              <svg className="animate-spin w-4 h-4" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
              </svg>
              Analyzing...
            </span>
          ) : (
            'Analyze →'
          )}
        </button>
      </form>

      {/* Error state */}
      <AnimatePresence>
        {error && (
          <motion.div
            initial={{ opacity: 0, y: -8 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0 }}
            className="bg-rose-500/10 border border-rose-500/20 rounded-xl px-4 py-3"
          >
            <p className="text-rose-400 text-sm">
              Backend error: {error}. Make sure the Move backend is running on port 8000.
            </p>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Results */}
      <AnimatePresence mode="wait">
        {data && (
          <motion.div
            key={data.stock + data.price_change}
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -8 }}
            transition={{ duration: 0.4 }}
            className="space-y-4"
          >
            {/* Price hero card */}
            <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6">
              <div className="flex items-start justify-between mb-4">
                <div>
                  <div className="flex items-center gap-3 mb-1">
                    <div className="w-9 h-9 bg-slate-800 rounded-xl flex items-center justify-center">
                      <span className="text-slate-300 font-bold text-xs">
                        {data.stock.slice(0, 2)}
                      </span>
                    </div>
                    <h3 className="text-slate-100 text-xl font-bold">{data.stock}</h3>
                  </div>
                  <p className="text-slate-500 text-xs ml-12">{date}</p>
                </div>
                <div className={`px-4 py-2 rounded-xl font-mono text-2xl font-bold
                  ${data.price_change >= 0
                    ? 'bg-emerald-500/10 border border-emerald-500/20 text-emerald-400'
                    : 'bg-rose-500/10 border border-rose-500/20 text-rose-400'}`}
                >
                  <PriceChange value={data.price_change} size="lg" />
                </div>
              </div>

              {/* Explanation */}
              <div className="mt-3 pt-4 border-t border-slate-800">
                <p className="text-slate-500 text-xs font-medium uppercase tracking-widest mb-2">
                  AI explanation
                </p>
                <p className="text-slate-300 text-sm leading-relaxed">{data.explanation}</p>
              </div>
            </div>

            {/* Attribution chart */}
            <AttributionChart attribution={data.attribution} title="Factor attribution" />
          </motion.div>
        )}
      </AnimatePresence>

      {/* Empty state */}
      {!data && !loading && !error && (
        <div className="bg-slate-900/50 border border-slate-800/50 border-dashed rounded-2xl p-12 text-center">
          <p className="text-slate-600 text-sm">
            Enter a stock symbol and date to see causal attribution
          </p>
          <p className="text-slate-700 text-xs mt-1">
            Try: TCS, INFY, RELIANCE, HDFC, WIPRO
          </p>
        </div>
      )}
    </div>
  )
}
