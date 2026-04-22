export interface PricePoint {
  date: string
  price: number
  ma50: number
  ma200: number
}

export interface StockMockData {
  name: string
  sector: string
  competitors: string[]
  revenue: { year: string; value: number }[]
  profit: { year: string; value: number }[]
  revenueGrowth: number
  profitGrowth: number
  balance: {
    totalDebt: string
    cash: string
    healthScore: number
    healthLabel: 'Strong' | 'Moderate' | 'Weak'
  }
  promoterHolding: number
  pros: string[]
  cons: string[]
  ratios: {
    pe: number
    eps: number
    roe: number
    debtToEquity: number
    marketCap: string
    dividendYield: number
  }
  technical: {
    rsi: number
    trend: 'Bullish' | 'Bearish' | 'Neutral'
    ma50: number
    ma200: number
    currentPrice: number
    support: number
    resistance: number
    fibonacci: { level: string; value: number }[]
  }
  priceHistory: PricePoint[]
}

// Lehmer LCG — deterministic, no globals
function genPriceHistory(
  basePrice: number,
  seed: number,
  trend: 'up' | 'down' | 'flat',
  n = 60
): PricePoint[] {
  let s = seed
  const trendBias = trend === 'up' ? 0.0009 : trend === 'down' ? -0.0009 : 0.0001
  // Start from offset so final price ≈ basePrice
  let price = basePrice * (trend === 'up' ? 0.91 : trend === 'down' ? 1.09 : 0.99)

  const rawPrices: number[] = []
  for (let i = 0; i < n; i++) {
    s = (s * 48271) % 2147483647
    price *= 1 + (s / 2147483647 - 0.5) * 0.022 + trendBias
    rawPrices.push(price)
  }

  // Actual rolling MAs (window capped at available data)
  return rawPrices.map((p, i) => {
    const w50  = rawPrices.slice(Math.max(0, i - 49), i + 1)
    const w200 = rawPrices.slice(Math.max(0, i - 199), i + 1)
    const avg  = (arr: number[]) => arr.reduce((s, v) => s + v, 0) / arr.length

    const d = new Date('2026-04-21')
    d.setDate(d.getDate() - (n - 1 - i))

    return {
      date: `${d.getMonth() + 1}/${d.getDate()}`,
      price:  +p.toFixed(2),
      ma50:   +avg(w50).toFixed(2),
      ma200:  +avg(w200).toFixed(2),
    }
  })
}

const STOCKS: Record<string, StockMockData> = {
  TCS: {
    name: 'Tata Consultancy Services',
    sector: 'IT Services',
    competitors: ['Infosys', 'Wipro', 'HCL Tech', 'Accenture'],
    revenue: [
      { year: 'FY22', value: 191754 },
      { year: 'FY23', value: 225458 },
      { year: 'FY24', value: 240893 },
    ],
    profit: [
      { year: 'FY22', value: 38327 },
      { year: 'FY23', value: 42147 },
      { year: 'FY24', value: 45908 },
    ],
    revenueGrowth: 6.8,
    profitGrowth: 8.9,
    balance: { totalDebt: '₹4,200 Cr', cash: '₹10,620 Cr', healthScore: 88, healthLabel: 'Strong' },
    promoterHolding: 72.3,
    pros: [
      'Market leader in Indian IT',
      'Consistent dividend history',
      'Strong dollar revenue hedge',
      'Diversified across 55+ countries',
    ],
    cons: [
      'Revenue growth slowing post-pandemic',
      'High attrition in mid-level talent',
      'Limited B2C exposure',
    ],
    ratios: { pe: 24.8, eps: 124.6, roe: 46.8, debtToEquity: 0.08, marketCap: '₹13.9L Cr', dividendYield: 1.8 },
    technical: {
      rsi: 58,
      trend: 'Bullish',
      ma50: 3620,
      ma200: 3480,
      currentPrice: 3682,
      support: 3520,
      resistance: 3820,
      fibonacci: [
        { level: '23.6%', value: 3591 },
        { level: '38.2%', value: 3635 },
        { level: '50.0%', value: 3670 },
        { level: '61.8%', value: 3705 },
      ],
    },
    priceHistory: genPriceHistory(3682, 42, 'up'),
  },

  INFY: {
    name: 'Infosys',
    sector: 'IT Services',
    competitors: ['TCS', 'Wipro', 'HCL Tech', 'Capgemini'],
    revenue: [
      { year: 'FY22', value: 121641 },
      { year: 'FY23', value: 146767 },
      { year: 'FY24', value: 153670 },
    ],
    profit: [
      { year: 'FY22', value: 22110 },
      { year: 'FY23', value: 24095 },
      { year: 'FY24', value: 26248 },
    ],
    revenueGrowth: 4.7,
    profitGrowth: 8.9,
    balance: { totalDebt: '₹2,810 Cr', cash: '₹14,308 Cr', healthScore: 82, healthLabel: 'Strong' },
    promoterHolding: 14.9,
    pros: [
      'Strong large-deal pipeline',
      'Cobalt cloud platform gaining traction',
      'Healthy free cash flow conversion',
      'Improving margins post-restructuring',
    ],
    cons: [
      'Low promoter holding = governance risk',
      'Employee utilization below target',
      'Growth guidance soft for FY25',
    ],
    ratios: { pe: 22.1, eps: 62.4, roe: 31.2, debtToEquity: 0.13, marketCap: '₹6.4L Cr', dividendYield: 2.6 },
    technical: {
      rsi: 45,
      trend: 'Neutral',
      ma50: 1510,
      ma200: 1455,
      currentPrice: 1492,
      support: 1430,
      resistance: 1580,
      fibonacci: [
        { level: '23.6%', value: 1449 },
        { level: '38.2%', value: 1491 },
        { level: '50.0%', value: 1505 },
        { level: '61.8%', value: 1519 },
      ],
    },
    priceHistory: genPriceHistory(1492, 137, 'flat'),
  },

  RELIANCE: {
    name: 'Reliance Industries',
    sector: 'Conglomerate',
    competitors: ['Adani Group', 'BPCL', 'Bharti Airtel'],
    revenue: [
      { year: 'FY22', value: 792756 },
      { year: 'FY23', value: 874154 },
      { year: 'FY24', value: 901981 },
    ],
    profit: [
      { year: 'FY22', value: 60705 },
      { year: 'FY23', value: 73670 },
      { year: 'FY24', value: 79020 },
    ],
    revenueGrowth: 3.2,
    profitGrowth: 7.3,
    balance: { totalDebt: '₹3.32L Cr', cash: '₹1.89L Cr', healthScore: 64, healthLabel: 'Moderate' },
    promoterHolding: 50.3,
    pros: [
      'Jio — 480M+ subscriber base',
      'Reliance Retail fastest-growing in Asia',
      'Green energy capex underway',
      'Conglomerate diversification',
    ],
    cons: [
      'Elevated debt from capex cycle',
      'Telecom ARPU still low vs global peers',
      'Complex group structure, limited transparency',
    ],
    ratios: { pe: 27.9, eps: 116.2, roe: 9.8, debtToEquity: 0.44, marketCap: '₹19.3L Cr', dividendYield: 0.4 },
    technical: {
      rsi: 62,
      trend: 'Bullish',
      ma50: 2800,
      ma200: 2710,
      currentPrice: 2852,
      support: 2720,
      resistance: 2980,
      fibonacci: [
        { level: '23.6%', value: 2751 },
        { level: '38.2%', value: 2770 },
        { level: '50.0%', value: 2850 },
        { level: '61.8%', value: 2880 },
      ],
    },
    priceHistory: genPriceHistory(2852, 251, 'up'),
  },

  HDFC: {
    name: 'HDFC Bank',
    sector: 'Banking & Finance',
    competitors: ['ICICI Bank', 'Kotak Mahindra', 'Axis Bank', 'SBI'],
    revenue: [
      { year: 'FY22', value: 89539 },
      { year: 'FY23', value: 106959 },
      { year: 'FY24', value: 109218 },
    ],
    profit: [
      { year: 'FY22', value: 36961 },
      { year: 'FY23', value: 44109 },
      { year: 'FY24', value: 60812 },
    ],
    revenueGrowth: 2.1,
    profitGrowth: 37.9,
    balance: { totalDebt: '₹20.2L Cr', cash: '₹3.4L Cr', healthScore: 71, healthLabel: 'Moderate' },
    promoterHolding: 0,
    pros: [
      'Largest private sector bank in India',
      'HDFC merger synergies unlocking',
      'Asset quality among best-in-class',
      'Massive retail distribution network',
    ],
    cons: [
      'CD ratio elevated post-merger',
      'NIM compression in near term',
      'Opex pressure from integration',
    ],
    ratios: { pe: 19.4, eps: 73.1, roe: 16.4, debtToEquity: 1.18, marketCap: '₹12.7L Cr', dividendYield: 1.2 },
    technical: {
      rsi: 52,
      trend: 'Neutral',
      ma50: 1695,
      ma200: 1640,
      currentPrice: 1718,
      support: 1640,
      resistance: 1800,
      fibonacci: [
        { level: '23.6%', value: 1659 },
        { level: '38.2%', value: 1701 },
        { level: '50.0%', value: 1720 },
        { level: '61.8%', value: 1739 },
      ],
    },
    priceHistory: genPriceHistory(1718, 388, 'flat'),
  },

  WIPRO: {
    name: 'Wipro',
    sector: 'IT Services',
    competitors: ['TCS', 'Infosys', 'HCL Tech', 'Tech Mahindra'],
    revenue: [
      { year: 'FY22', value: 79312 },
      { year: 'FY23', value: 90488 },
      { year: 'FY24', value: 89776 },
    ],
    profit: [
      { year: 'FY22', value: 12246 },
      { year: 'FY23', value: 14060 },
      { year: 'FY24', value: 11969 },
    ],
    revenueGrowth: -0.8,
    profitGrowth: -14.9,
    balance: { totalDebt: '₹5,100 Cr', cash: '₹22,410 Cr', healthScore: 78, healthLabel: 'Strong' },
    promoterHolding: 72.9,
    pros: [
      'High cash balance — buyback potential',
      'Focus shift to profitable growth',
      'Strong promoter backing',
    ],
    cons: [
      'Revenue declining YoY',
      'Weak deal TCV vs peers',
      'Margin pressure from investments',
      'Growth guidance remains cautious',
    ],
    ratios: { pe: 20.3, eps: 21.4, roe: 17.1, debtToEquity: 0.19, marketCap: '₹2.6L Cr', dividendYield: 0.2 },
    technical: {
      rsi: 38,
      trend: 'Bearish',
      ma50: 498,
      ma200: 512,
      currentPrice: 488,
      support: 465,
      resistance: 530,
      fibonacci: [
        { level: '23.6%', value: 471 },
        { level: '38.2%', value: 479 },
        { level: '50.0%', value: 497 },
        { level: '61.8%', value: 504 },
      ],
    },
    priceHistory: genPriceHistory(488, 512, 'down'),
  },
}

export function getMockData(ticker: string): StockMockData {
  return STOCKS[ticker.toUpperCase()] ?? STOCKS['TCS']
}
