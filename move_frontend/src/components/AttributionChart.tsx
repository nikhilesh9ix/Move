'use client'

import { motion } from 'framer-motion'
import {
  Cell,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
} from 'recharts'
import { factorColor } from '@/constants'
import type { Attribution } from '@/types'

interface Props {
  attribution: Attribution[]
  title?: string
}

interface TooltipPayload {
  name: string
  value: number
  payload: { factor: string; contribution: number }
}

function CustomTooltip({
  active,
  payload,
}: {
  active?: boolean
  payload?: TooltipPayload[]
}) {
  if (!active || !payload?.length) return null
  const item = payload[0]
  return (
    <div className="bg-slate-800 border border-slate-700 rounded-xl px-4 py-3 shadow-xl">
      <p className="text-slate-400 text-xs capitalize mb-1">{item.name}</p>
      <p className="text-slate-100 text-sm font-mono font-bold">{item.value}%</p>
    </div>
  )
}

export function AttributionChart({ attribution, title = 'Attribution' }: Props) {
  if (!attribution || attribution.length === 0) return null

  const pieData = attribution.map((a) => ({
    name: a.factor,
    value: a.contribution,
    fill: factorColor(a.factor),
  }))

  const dominant = attribution.reduce(
    (max, a) => (a.contribution > max.contribution ? a : max),
    attribution[0]
  )

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.97 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.45, delay: 0.2 }}
      className="bg-slate-900 border border-slate-800 rounded-2xl p-6"
    >
      <p className="text-slate-500 text-xs font-medium uppercase tracking-widest mb-5">
        {title}
      </p>

      <div className="flex flex-col md:flex-row items-center gap-8">
        {/* Donut chart */}
        <div className="relative w-52 h-52 shrink-0">
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={pieData}
                cx="50%"
                cy="50%"
                innerRadius={68}
                outerRadius={96}
                paddingAngle={3}
                dataKey="value"
                strokeWidth={0}
              >
                {pieData.map((entry) => (
                  <Cell key={entry.name} fill={entry.fill} />
                ))}
              </Pie>
              <Tooltip content={<CustomTooltip />} />
            </PieChart>
          </ResponsiveContainer>
          {/* Center label */}
          <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none">
            <span className="text-slate-400 text-xs capitalize">{dominant?.factor}</span>
            <span
              className="text-2xl font-bold font-mono tabular-nums"
              style={{ color: factorColor(dominant?.factor ?? '') }}
            >
              {dominant?.contribution}%
            </span>
          </div>
        </div>

        {/* Legend */}
        <div className="flex-1 space-y-3 w-full">
          {attribution
            .slice()
            .sort((a, b) => b.contribution - a.contribution)
            .map((a, i) => (
              <motion.div
                key={a.factor}
                initial={{ opacity: 0, x: 10 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: i * 0.08 + 0.3 }}
                className="flex items-center justify-between group"
              >
                <div className="flex items-center gap-3">
                  <div
                    className="w-3 h-3 rounded-sm shrink-0"
                    style={{ backgroundColor: factorColor(a.factor) }}
                  />
                  <span className="text-slate-300 text-sm capitalize">{a.factor}</span>
                </div>
                <div className="flex items-center gap-3">
                  <div className="w-24 h-1.5 bg-slate-800 rounded-full overflow-hidden">
                    <motion.div
                      className="h-full rounded-full"
                      style={{ backgroundColor: factorColor(a.factor) }}
                      initial={{ width: 0 }}
                      animate={{ width: `${a.contribution}%` }}
                      transition={{ duration: 0.8, delay: i * 0.08 + 0.4, ease: 'easeOut' }}
                    />
                  </div>
                  <span className="text-slate-400 text-sm font-mono tabular-nums w-10 text-right">
                    {a.contribution}%
                  </span>
                </div>
              </motion.div>
            ))}
        </div>
      </div>
    </motion.div>
  )
}
