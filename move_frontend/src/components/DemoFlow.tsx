'use client'

import { useEffect, useState } from 'react'
import { AnimatePresence, motion } from 'framer-motion'

const STEPS = [
  {
    title: 'Your portfolio, explained in seconds',
    body: 'The Why Card breaks down exactly what moved your portfolio today — and why — using causal AI, not just news headlines.',
  },
  {
    title: 'Root causes, not noise',
    body: 'Move identifies whether a move was sector-wide, macro-driven, or company-specific — and assigns a confidence score to each explanation.',
  },
  {
    title: 'Live updates as markets move',
    body: 'The real-time feed triggers whenever a holding crosses the movement threshold, delivering fresh attribution within seconds.',
  },
]

const AUTO_ADVANCE_MS = 5000

export function DemoFlow() {
  const [visible, setVisible] = useState(false)
  const [step, setStep] = useState(0)
  const [progress, setProgress] = useState(0)

  useEffect(() => {
    try {
      if (localStorage.getItem('move_tour_done')) return
    } catch { /* storage blocked */ }
    // Small delay so the dashboard renders first
    const show = setTimeout(() => setVisible(true), 900)
    return () => clearTimeout(show)
  }, [])

  // Progress bar + auto-advance
  useEffect(() => {
    if (!visible) return
    setProgress(0)
    const start = performance.now()
    let raf: number

    function tick() {
      const elapsed = performance.now() - start
      const p = Math.min((elapsed / AUTO_ADVANCE_MS) * 100, 100)
      setProgress(p)
      if (p < 100) {
        raf = requestAnimationFrame(tick)
      } else {
        if (step < STEPS.length - 1) {
          setStep((s) => s + 1)
        } else {
          dismiss()
        }
      }
    }

    raf = requestAnimationFrame(tick)
    return () => cancelAnimationFrame(raf)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [step, visible])

  function dismiss() {
    setVisible(false)
    try { localStorage.setItem('move_tour_done', '1') } catch { /* ok */ }
  }

  return (
    <AnimatePresence>
      {visible && (
        <motion.div
          initial={{ opacity: 0, y: 20, scale: 0.97 }}
          animate={{ opacity: 1, y: 0, scale: 1 }}
          exit={{ opacity: 0, y: 16, scale: 0.97 }}
          transition={{ duration: 0.35, ease: 'easeOut' }}
          className="fixed bottom-6 right-6 z-50 w-80 bg-slate-900 border border-slate-700 rounded-2xl shadow-2xl shadow-black/40 overflow-hidden"
        >
          {/* Progress bar */}
          <div className="h-0.5 bg-slate-800">
            <motion.div
              className="h-full bg-blue-500"
              style={{ width: `${progress}%` }}
            />
          </div>

          <div className="p-5">
            {/* Step dots */}
            <div className="flex items-center justify-between mb-4">
              <div className="flex gap-1.5">
                {STEPS.map((_, i) => (
                  <button
                    key={i}
                    onClick={() => setStep(i)}
                    className={`w-1.5 h-1.5 rounded-full transition-all duration-200 ${
                      i === step ? 'bg-blue-400 w-4' : 'bg-slate-600'
                    }`}
                  />
                ))}
              </div>
              <button
                onClick={dismiss}
                className="text-slate-600 hover:text-slate-400 transition-colors text-sm"
                aria-label="Dismiss tour"
              >
                ✕
              </button>
            </div>

            {/* Content */}
            <AnimatePresence mode="wait">
              <motion.div
                key={step}
                initial={{ opacity: 0, x: 12 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -12 }}
                transition={{ duration: 0.2 }}
              >
                <p className="text-blue-400 text-xs font-medium uppercase tracking-widest mb-2">
                  Step {step + 1} of {STEPS.length}
                </p>
                <h3 className="text-slate-100 text-sm font-semibold mb-1.5">
                  {STEPS[step].title}
                </h3>
                <p className="text-slate-500 text-xs leading-relaxed">
                  {STEPS[step].body}
                </p>
              </motion.div>
            </AnimatePresence>

            {/* Actions */}
            <div className="flex items-center justify-between mt-4">
              <button
                onClick={dismiss}
                className="text-slate-600 hover:text-slate-400 text-xs transition-colors"
              >
                Skip tour
              </button>
              {step < STEPS.length - 1 ? (
                <button
                  onClick={() => setStep((s) => s + 1)}
                  className="text-blue-400 hover:text-blue-300 text-xs font-medium transition-colors"
                >
                  Next →
                </button>
              ) : (
                <button
                  onClick={dismiss}
                  className="bg-blue-500/20 text-blue-400 hover:bg-blue-500/30 text-xs font-medium px-3 py-1 rounded-lg transition-colors"
                >
                  Got it
                </button>
              )}
            </div>
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  )
}
