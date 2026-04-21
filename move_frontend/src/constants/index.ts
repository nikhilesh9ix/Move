export const FACTOR_COLORS: Record<string, string> = {
  sector: '#3b82f6',       // blue
  macro: '#8b5cf6',        // violet
  rates: '#06b6d4',        // cyan
  earnings: '#f59e0b',     // amber
  idiosyncratic: '#f43f5e', // rose
}

export const FACTOR_COLOR_DEFAULT = '#64748b'

export const DEFAULT_DATE = '2026-04-20'

export const CURRENCY_FORMAT = new Intl.NumberFormat('en-IN', {
  style: 'currency',
  currency: 'INR',
  minimumFractionDigits: 2,
  maximumFractionDigits: 2,
})

export function formatCurrency(value: number): string {
  return CURRENCY_FORMAT.format(value)
}

export function factorColor(factor: string): string {
  return FACTOR_COLORS[factor] ?? FACTOR_COLOR_DEFAULT
}
