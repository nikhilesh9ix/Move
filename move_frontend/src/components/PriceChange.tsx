interface Props {
  value: number
  suffix?: string
  size?: 'sm' | 'md' | 'lg'
}

const SIZE = {
  sm: 'text-sm',
  md: 'text-base',
  lg: 'text-2xl font-bold',
}

export function PriceChange({ value, suffix = '%', size = 'md' }: Props) {
  const isPositive = value >= 0
  const colorClass = isPositive ? 'text-emerald-400' : 'text-rose-400'
  const arrow = isPositive ? '▲' : '▼'

  return (
    <span className={`font-mono tabular-nums ${colorClass} ${SIZE[size]}`}>
      {arrow} {Math.abs(value).toFixed(2)}{suffix}
    </span>
  )
}
