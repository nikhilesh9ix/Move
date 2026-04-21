export interface Attribution {
  factor: string
  contribution: number
}

export interface AnalyzeResponse {
  stock: string
  price_change: number
  attribution: Attribution[]
  explanation: string
  historical_hint: string
  actionable_insight: string
  confidence_pct: number
}

export interface HoldingChange {
  stock: string
  price_change: number
  value_change: number
}

export interface PortfolioResponse {
  total_value: number
  total_change_pct: number
  top_gainers: HoldingChange[]
  top_losers: HoldingChange[]
}

export interface CauseItem {
  cause: string
  impact: number
}

export interface WhyCardResponse {
  date: string
  total_portfolio_change_pct: number
  top_causes: CauseItem[]
  explanation_summary: string
  confidence_pct: number
  confidence_label: string
  primary_driver_label: string
}
