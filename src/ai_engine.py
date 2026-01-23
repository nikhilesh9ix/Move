"""
AI Explanation Engine
Uses OpenRouter LLMs to generate structured, evidence-based explanations.
"""

import os
from typing import Dict, List, Optional
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()


class AIExplanationEngine:
    """Generates natural language explanations using LLMs."""
    
    def __init__(self):
        """Initialize the AI engine with OpenRouter."""
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        self.model = os.getenv("OPENROUTER_MODEL", "meta-llama/llama-3.1-70b-instruct")
        
        if not self.api_key or self.api_key == "your_openrouter_key_here":
            raise ValueError("OPENROUTER_API_KEY not configured in .env file")
        
        # OpenRouter uses OpenAI-compatible API
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=self.api_key,
        )
    
    def generate_explanation(
        self,
        symbol: str,
        date: str,
        price_metrics: Dict,
        volume_metrics: Dict,
        context_analysis: Dict,
        news_summary: Dict
    ) -> Dict:
        """
        Generate a comprehensive explanation for a stock movement.
        
        Args:
            symbol: Stock ticker symbol
            date: Date of movement
            price_metrics: Price change metrics
            volume_metrics: Volume anomaly metrics
            context_analysis: Contextual analysis results
            news_summary: News summary
            
        Returns:
            Structured explanation with confidence score
        """
        # Build evidence summary
        evidence = self._build_evidence_summary(
            price_metrics, volume_metrics, context_analysis, news_summary
        )
        
        # Create prompt for LLM
        prompt = self._create_explanation_prompt(
            symbol, date, evidence, news_summary
        )
        
        # Get LLM response
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": self._get_system_prompt()
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,  # Lower temperature for more factual responses
                max_tokens=800
            )
            
            explanation_text = response.choices[0].message.content
            
            # Parse the explanation
            parsed = self._parse_explanation(explanation_text)
            
            # Calculate confidence score
            confidence = self._calculate_confidence(
                evidence, news_summary, context_analysis
            )
            
            return {
                "symbol": symbol,
                "date": date,
                "price_change_pct": price_metrics["price_change_pct"],
                "primary_driver": parsed.get("primary_driver", "Unknown"),
                "supporting_factors": parsed.get("supporting_factors", []),
                "explanation": parsed.get("explanation", explanation_text),
                "move_classification": context_analysis["classification"],
                "confidence": confidence,
                "evidence": evidence,
                "news_headlines": news_summary.get("top_headlines", [])[:3]
            }
            
        except Exception as e:
            print(f"Error generating explanation: {e}")
            # Return fallback explanation
            return self._generate_fallback_explanation(
                symbol, date, price_metrics, context_analysis, evidence
            )
    
    def _get_system_prompt(self) -> str:
        """Get the system prompt that defines the AI's role."""
        return """You are a financial analyst AI that explains stock movements using evidence-based reasoning.

Your role:
- Explain WHY a stock moved on a specific day (not predict future movements)
- Base all explanations on provided evidence (price data, volume, market context, news)
- Be clear, concise, and objective
- Acknowledge uncertainty when evidence is limited
- Never provide trading advice or recommendations

Output format:
PRIMARY DRIVER: [main reason in one sentence]
SUPPORTING FACTORS:
- [factor 1]
- [factor 2]
- [factor 3 if applicable]

EXPLANATION:
[2-3 sentence clear explanation of what happened and why]

Guidelines:
- If news is significant and stock-specific, news is likely the primary driver
- If the move follows the market/sector closely, cite that as the primary driver
- If volume is unusual without clear news, mention unusual trading activity
- Always acknowledge confidence level in your explanation"""
    
    def _create_explanation_prompt(
        self,
        symbol: str,
        date: str,
        evidence: Dict,
        news_summary: Dict
    ) -> str:
        """Create the user prompt with all evidence."""
        prompt_parts = [
            f"Explain why {symbol} moved on {date}.\n",
            f"\nPRICE MOVEMENT:",
            f"- Changed {evidence['price_change_pct']}%",
            f"- Intraday change: {evidence.get('intraday_change_pct', 'N/A')}%",
            f"\nVOLUME:",
            f"- Volume was {evidence['volume_ratio']}x normal average",
            f"- Volume spike detected: {evidence['volume_spike']}",
            f"\nMARKET CONTEXT:",
            f"- Market ({evidence['market_index']}): {evidence['market_change_pct']}%",
        ]
        
        if evidence.get('sector_change_pct'):
            prompt_parts.append(f"- Sector: {evidence['sector_change_pct']}%")
        
        prompt_parts.append(f"- Move classification: {evidence['classification']}")
        prompt_parts.append(f"- Relative strength vs market: {evidence['relative_strength']}%")
        
        prompt_parts.append(f"\nNEWS COVERAGE:")
        prompt_parts.append(f"- {evidence['news_count']} articles found")
        prompt_parts.append(f"- Significant news detected: {evidence.get('has_significant_news', False)}")
        
        if news_summary.get('top_headlines'):
            prompt_parts.append(f"\nTOP HEADLINES:")
            for headline in news_summary['top_headlines'][:3]:
                prompt_parts.append(f"- {headline['title']} ({headline['source']})")
        
        return "\n".join(prompt_parts)
    
    def _build_evidence_summary(
        self,
        price_metrics: Dict,
        volume_metrics: Dict,
        context_analysis: Dict,
        news_summary: Dict
    ) -> Dict:
        """Build a structured evidence summary."""
        return {
            "price_change_pct": price_metrics["price_change_pct"],
            "intraday_change_pct": price_metrics.get("intraday_change_pct"),
            "is_significant": price_metrics["is_significant"],
            "volume": volume_metrics["volume"],
            "avg_volume": volume_metrics["avg_volume"],
            "volume_ratio": volume_metrics["volume_ratio"],
            "volume_spike": volume_metrics["volume_spike"],
            "market_index": context_analysis["market"]["index"],
            "market_change_pct": context_analysis["market"]["change_pct"],
            "sector_change_pct": context_analysis.get("sector", {}).get("change_pct"),
            "classification": context_analysis["classification"],
            "relative_strength": context_analysis["relative_strength"]["vs_market"],
            "news_count": news_summary["count"],
            "has_significant_news": news_summary["has_significant_news"],
            "news_sources": len(news_summary.get("sources", []))
        }
    
    def _parse_explanation(self, explanation_text: str) -> Dict:
        """Parse the LLM's explanation into structured format."""
        lines = explanation_text.strip().split('\n')
        
        parsed = {
            "primary_driver": "",
            "supporting_factors": [],
            "explanation": ""
        }
        
        current_section = None
        explanation_lines = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            if line.startswith("PRIMARY DRIVER:"):
                parsed["primary_driver"] = line.replace("PRIMARY DRIVER:", "").strip()
                current_section = "primary"
            elif line.startswith("SUPPORTING FACTORS:"):
                current_section = "supporting"
            elif line.startswith("EXPLANATION:"):
                current_section = "explanation"
            elif line.startswith("-") and current_section == "supporting":
                parsed["supporting_factors"].append(line[1:].strip())
            elif current_section == "explanation":
                explanation_lines.append(line)
        
        if explanation_lines:
            parsed["explanation"] = " ".join(explanation_lines)
        
        # Fallback if parsing failed
        if not parsed["primary_driver"] and not parsed["explanation"]:
            parsed["explanation"] = explanation_text
        
        return parsed
    
    def _calculate_confidence(
        self,
        evidence: Dict,
        news_summary: Dict,
        context_analysis: Dict
    ) -> float:
        """
        Calculate confidence score based on evidence strength.
        
        Returns:
            Confidence score between 0 and 1
        """
        confidence = 0.5  # Base confidence
        
        # Increase confidence if there's clear news
        if evidence["has_significant_news"] and evidence["news_count"] >= 3:
            confidence += 0.2
        elif evidence["news_count"] >= 1:
            confidence += 0.1
        
        # Increase confidence if volume confirms the move
        if evidence["volume_spike"]:
            confidence += 0.15
        
        # Increase confidence if classification is clear
        if context_analysis["classification"] in ["market_driven", "stock_specific"]:
            confidence += 0.1
        elif context_analysis["classification"] == "sector_driven":
            confidence += 0.05
        
        # Decrease confidence if move is very small
        if abs(evidence["price_change_pct"]) < 1.0:
            confidence -= 0.1
        
        # Decrease confidence if there's conflicting signals
        if evidence["volume_spike"] and not evidence["has_significant_news"]:
            confidence -= 0.05
        
        # Clamp between 0.3 and 0.95
        return max(0.3, min(0.95, confidence))
    
    def _generate_fallback_explanation(
        self,
        symbol: str,
        date: str,
        price_metrics: Dict,
        context_analysis: Dict,
        evidence: Dict
    ) -> Dict:
        """Generate a simple rule-based explanation if AI fails."""
        classification = context_analysis["classification"]
        price_change = price_metrics["price_change_pct"]
        
        if classification == "market_driven":
            primary = f"Moved in line with broader market ({evidence['market_change_pct']}%)"
        elif classification == "sector_driven":
            primary = f"Followed sector trend ({evidence.get('sector_change_pct', 'N/A')}%)"
        else:
            primary = f"Stock-specific movement of {price_change}%"
        
        return {
            "symbol": symbol,
            "date": date,
            "price_change_pct": price_change,
            "primary_driver": primary,
            "supporting_factors": [
                f"Volume was {evidence['volume_ratio']}x average",
                f"Market context: {evidence['market_change_pct']}%"
            ],
            "explanation": f"{symbol} {('rose' if price_change > 0 else 'fell')} {abs(price_change)}% on {date}. {primary}.",
            "move_classification": classification,
            "confidence": 0.4,
            "evidence": evidence,
            "news_headlines": []
        }
