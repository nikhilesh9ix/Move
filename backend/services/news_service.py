"""
News service using NewsAPI.org.
Fetches relevant news headlines for stocks on specific dates.
"""

import requests
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import logging
from config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class NewsService:
    """Service for fetching news headlines."""

    BASE_URL = "https://newsapi.org/v2/everything"

    def __init__(self, api_key: str):
        """Initialize with NewsAPI key."""
        self.api_key = api_key

    def get_news(
        self, symbol: str, target_date: str, max_articles: int = 5
    ) -> List[Dict]:
        """
        Fetch news headlines for a stock around the target date.

        Args:
            symbol: Stock ticker symbol
            target_date: Date in YYYY-MM-DD format
            max_articles: Maximum number of articles to return

        Returns:
            List of news articles with title, source, and published date
        """
        try:
            target_dt = datetime.strptime(target_date, "%Y-%m-%d")

            # Search window: 1 day before to 1 day after
            from_date = (target_dt - timedelta(days=1)).strftime("%Y-%m-%d")
            to_date = (target_dt + timedelta(days=1)).strftime("%Y-%m-%d")

            # Build search query
            # Try to get company name for better results
            query = symbol

            params = {
                "q": query,
                "from": from_date,
                "to": to_date,
                "language": "en",
                "sortBy": "relevancy",
                "pageSize": max_articles,
                "apiKey": self.api_key,
            }

            response = requests.get(self.BASE_URL, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()

            if data["status"] != "ok":
                logger.warning(
                    f"NewsAPI returned non-ok status: {data.get('message', 'Unknown error')}"
                )
                return []

            articles = data.get("articles", [])

            # Format articles
            news_items = []
            for article in articles[:max_articles]:
                news_items.append(
                    {
                        "title": article.get("title", "No title"),
                        "source": article.get("source", {}).get("name", "Unknown"),
                        "published_at": article.get("publishedAt", ""),
                        "description": article.get("description", ""),
                    }
                )

            logger.info(
                f"Found {len(news_items)} news articles for {symbol} around {target_date}"
            )
            return news_items

        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching news: {str(e)}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error in news service: {str(e)}")
            return []


# Global instance
news_service = NewsService(settings.newsapi_key)
