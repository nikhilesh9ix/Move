"""
Service for generating explanations using OpenRouter API (meta-llama/llama-3-8b-instruct)
"""
import os
import requests
from typing import Dict

OPENROUTER_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
OPENROUTER_MODEL = "meta-llama/llama-3-8b-instruct"

class AIEngine:
    def __init__(self):
        self.api_key = OPENROUTER_KEY
        self.model = OPENROUTER_MODEL

    def explain(self, evidence: Dict) -> Dict:
        if not self.api_key:
            return {"error": "OpenRouter API key not set"}
        prompt = self._build_prompt(evidence)
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": self._system_prompt()},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.2,
            "max_tokens": 600
        }
        resp = requests.post(OPENROUTER_URL, headers=headers, json=payload)
        if resp.status_code != 200:
            return {"error": f"OpenRouter error: {resp.text}"}
        data = resp.json()
        return {"explanation": data["choices"][0]["message"]["content"]}

    def _system_prompt(self) -> str:
        return (
            "You are a financial analyst AI. You explain why a stock moved on a specific day using only the provided evidence. "
            "Never predict future prices. Never give trading advice. Always mention uncertainty if evidence is weak."
        )

    def _build_prompt(self, evidence: Dict) -> str:
        # Format evidence into a strict prompt
        return f"""
WHY DID {evidence['symbol']} MOVE ON {evidence['date']}?

SUMMARY:
Price Change: {evidence['price_change']}%
Volume: {evidence['volume']} ({evidence['volume_ratio']}x 20d avg)
Index Change: {evidence['index_change']}%
Sector Change: {evidence['sector_change']}%
News Headlines: {', '.join([h['title'] for h in evidence['headlines']])}

PRIMARY DRIVER:
SUPPORTING FACTORS:
MOVE CLASSIFICATION:
CONFIDENCE SCORE:
UNCERTAINTY NOTE:
"""