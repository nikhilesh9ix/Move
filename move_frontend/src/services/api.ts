import axios from 'axios'
import type { AnalyzeResponse, PortfolioResponse, WhyCardResponse } from '@/types'

const client = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_BASE_URL || '/move-api',
  timeout: 10_000,
  headers: { 'Content-Type': 'application/json' },
})

export async function fetchWhyCard(date: string): Promise<WhyCardResponse> {
  const { data } = await client.get<WhyCardResponse>('/daily-why-card', {
    params: { date },
  })
  return data
}

export async function fetchPortfolioSummary(date: string): Promise<PortfolioResponse> {
  const { data } = await client.get<PortfolioResponse>('/portfolio-summary', {
    params: { date },
  })
  return data
}

export async function analyzeMove(stock: string, date: string): Promise<AnalyzeResponse> {
  const { data } = await client.post<AnalyzeResponse>('/analyze-move', { stock, date })
  return data
}
