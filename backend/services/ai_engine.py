"""
AI Engine using OpenRouter API.
Generates explanations for stock movements using LLaMA 3 8B model.
"""

import requests
from typing import Dict, List, Optional
import json
import logging
from config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AIEngine:
    """AI-powered explanation engine using OpenRouter."""

    OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

    def __init__(self, api_key: str, model: str, temperature: float, max_tokens: int):
        """Initialize AI engine with configuration."""
        self.api_key = api_key
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens

    def generate_explanation(
        self, evidence: str, symbol: str, date: str, price_change_percent: float
    ) -> Dict:
        """
        Generate AI explanation for stock movement.

        Args:
            evidence: Compiled evidence string
            symbol: Stock symbol
            date: Target date
            price_change_percent: Price change percentage

        Returns:
            Dictionary with parsed explanation components
        """
        try:
            # Build the prompt
            prompt = self._build_prompt(evidence, symbol, date, price_change_percent)

            # Call OpenRouter API
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://github.com/ai-stock-explainer",
                "X-Title": "AI Stock Movement Explainer",
            }

            payload = {
                "model": self.model,
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a financial analyst providing evidence-based explanations for stock price movements. You NEVER make predictions or give trading advice. You only analyze what happened based on provided evidence.",
                    },
                    {"role": "user", "content": prompt},
                ],
                "temperature": self.temperature,
                "max_tokens": self.max_tokens,
            }

            response = requests.post(
                self.OPENROUTER_URL, headers=headers, json=payload, timeout=30
            )
            response.raise_for_status()

            result = response.json()
            ai_response = result["choices"][0]["message"]["content"]

            # Parse the structured response
            parsed = self._parse_response(ai_response)

            logger.info(f"Generated explanation for {symbol} on {date}")
            return parsed

        except requests.exceptions.RequestException as e:
            logger.error(f"OpenRouter API error: {str(e)}")
            raise Exception(f"AI service error: {str(e)}")
        except Exception as e:
            logger.error(f"Error generating explanation: {str(e)}")
            raise

    def _build_prompt(
        self, evidence: str, symbol: str, date: str, price_change_percent: float
    ) -> str:
        """Build the prompt for AI analysis."""
        direction = "up" if price_change_percent > 0 else "down"

        prompt = f"""Based on the evidence below, explain WHY {symbol} moved {direction} by {abs(price_change_percent):.2f}% on {date}.

EVIDENCE:
{evidence}

INSTRUCTIONS:
1. Identify the PRIMARY DRIVER (most likely cause of the movement)
2. List 2-3 SUPPORTING FACTORS (additional contributing factors)
3. Classify the move as: STOCK-SPECIFIC, SECTOR-DRIVEN, MARKET-DRIVEN, or MIXED
4. Provide a CONFIDENCE SCORE (0.0 to 1.0) based on evidence strength
5. Include an UNCERTAINTY NOTE if evidence is limited or conflicting

REQUIRED OUTPUT FORMAT:

SUMMARY:
[2-3 sentence summary of what happened and why]

PRIMARY DRIVER:
[Single most important factor]

SUPPORTING FACTORS:
- [Factor 1]
- [Factor 2]
- [Factor 3]

MOVE CLASSIFICATION:
[STOCK-SPECIFIC / SECTOR-DRIVEN / MARKET-DRIVEN / MIXED]

CONFIDENCE SCORE:
[0.0 to 1.0]

UNCERTAINTY NOTE:
[Any caveats, limitations, or alternative explanations. Write "None" if confidence is high]

CRITICAL RULES:
- Base analysis ONLY on provided evidence
- Do NOT make predictions about future prices
- Do NOT give trading advice
- Be explicit about uncertainty when evidence is weak
- If no clear driver exists, say so honestly
"""
        return prompt

    def _parse_response(self, ai_response: str) -> Dict:
        """Parse the structured AI response into components."""
        try:
            lines = ai_response.strip().split("\n")

            result = {
                "full_explanation": ai_response,
                "summary": "",
                "primary_driver": "",
                "supporting_factors": [],
                "move_classification": "",
                "confidence_score": 0.5,
                "uncertainty_note": None,
            }

            current_section = None

            for line in lines:
                line = line.strip()

                if line.startswith("SUMMARY:"):
                    current_section = "summary"
                    continue
                elif line.startswith("PRIMARY DRIVER:"):
                    current_section = "primary_driver"
                    continue
                elif line.startswith("SUPPORTING FACTORS:"):
                    current_section = "supporting_factors"
                    continue
                elif line.startswith("MOVE CLASSIFICATION:"):
                    current_section = "move_classification"
                    continue
                elif line.startswith("CONFIDENCE SCORE:"):
                    current_section = "confidence_score"
                    continue
                elif line.startswith("UNCERTAINTY NOTE:"):
                    current_section = "uncertainty_note"
                    continue

                # Process content based on current section
                if current_section == "summary" and line:
                    result["summary"] += line + " "
                elif current_section == "primary_driver" and line:
                    result["primary_driver"] += line + " "
                elif current_section == "supporting_factors" and line.startswith("-"):
                    result["supporting_factors"].append(line[1:].strip())
                elif current_section == "move_classification" and line:
                    result["move_classification"] = line
                elif current_section == "confidence_score" and line:
                    try:
                        score = float(line)
                        result["confidence_score"] = max(0.0, min(1.0, score))
                    except ValueError:
                        pass
                elif current_section == "uncertainty_note" and line:
                    if line.lower() != "none":
                        result["uncertainty_note"] = line

            # Clean up
            result["summary"] = result["summary"].strip()
            result["primary_driver"] = result["primary_driver"].strip()

            return result

        except Exception as e:
            logger.error(f"Error parsing AI response: {str(e)}")
            # Return a fallback structure
            return {
                "full_explanation": ai_response,
                "summary": "Unable to parse structured response",
                "primary_driver": "Unknown",
                "supporting_factors": [],
                "move_classification": "UNKNOWN",
                "confidence_score": 0.3,
                "uncertainty_note": "Response parsing failed",
            }


# Global instance
ai_engine = AIEngine(
    api_key=settings.openrouter_api_key,
    model=settings.ai_model,
    temperature=settings.ai_temperature,
    max_tokens=settings.ai_max_tokens,
)
