'use client'

import { motion } from 'framer-motion'
import { factorColor } from '@/constants'
import type { CauseItem } from '@/types'

interface Props {
  cause: CauseItem
  index: number
  animationDelay?: number
  isPrimary?: boolean
}

export function CauseBar({ cause, index, animationDelay = 0, isPrimary = false }: Props) {
  const color = factorColor(cause.cause)

  return (
    <motion.div
      initial={{ opacity: 0, x: -14 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration: 0.35, delay: index * 0.09 + animationDelay }}
      className="flex items-center gap-3"
    >
      {/* Dot */}
      <div className="relative shrink-0 flex items-center justify-center w-4 h-4">
        <div
          className="w-2 h-2 rounded-full"
          style={{
            backgroundColor: color,
            boxShadow: isPrimary ? `0 0 8px ${color}` : undefined,
          }}
        />
        {isPrimary && (
          <div
            className="absolute inset-0 rounded-full animate-ping opacity-30"
            style={{ backgroundColor: color }}
          />
        )}
      </div>

      {/* Label */}
      <span
        className={`text-xs capitalize w-28 truncate tracking-wide ${
          isPrimary ? 'text-slate-100 font-semibold' : 'text-slate-500'
        }`}
      >
        {cause.cause}
      </span>

      {/* Track + fill */}
      <div
        className="flex-1 h-1.5 rounded-full overflow-hidden"
        style={{ background: 'rgba(255,255,255,0.05)' }}
      >
        <motion.div
          className="h-full rounded-full"
          style={{
            backgroundColor: color,
            boxShadow: isPrimary ? `0 0 10px ${color}80` : undefined,
          }}
          initial={{ width: 0 }}
          animate={{ width: `${Math.min(cause.impact, 100)}%` }}
          transition={{
            duration: 1.1,
            delay: index * 0.09 + animationDelay + 0.15,
            ease: [0.16, 1, 0.3, 1],
          }}
        />
      </div>

      {/* Percentage */}
      <span
        className={`text-xs font-mono tabular-nums w-10 text-right ${
          isPrimary ? 'text-slate-200 font-semibold' : 'text-slate-600'
        }`}
      >
        {cause.impact}%
      </span>
    </motion.div>
  )
}
