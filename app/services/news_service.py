"""
Service for fetching news headlines from NewsAPI.org
"""
import os
import requests
from typing import List, Dict

NEWSAPI_KEY = os.getenv("NEWSAPI_KEY")
NEWSAPI_URL = "https://newsapi.org/v2/everything"

class NewsService:
    def __init__(self):
        self.api_key = NEWSAPI_KEY

    def fetch_headlines(self, symbol: str, date: str, max_results: int = 5) -> List[Dict]:
        if not self.api_key:
            return []
        params = {
            "q": symbol,
            "from": date,
            "to": date,
            "sortBy": "relevancy",
            "language": "en",
            "apiKey": self.api_key,
            "pageSize": max_results
        }
        resp = requests.get(NEWSAPI_URL, params=params)
        if resp.status_code != 200:
            return []
        data = resp.json()
        return [
            {
                "title": a["title"],
                "url": a["url"],
                "source": a["source"]["name"]
            }
            for a in data.get("articles", [])
        ]
