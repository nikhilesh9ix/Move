"""
News service using NewsAPI.org.
Fetches relevant news headlines for stocks on specific dates with sentiment analysis.
"""

import requests
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
import logging
from config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class NewsService:
    """Service for fetching news headlines with sentiment analysis."""

    BASE_URL = "https://newsapi.org/v2/everything"
    
    # Source credibility scores (0-1 scale)
    SOURCE_CREDIBILITY = {
        "Reuters": 0.95,
        "Bloomberg": 0.95,
        "The Wall Street Journal": 0.93,
        "Financial Times": 0.93,
        "CNBC": 0.85,
        "MarketWatch": 0.82,
        "Barron's": 0.85,
        "The New York Times": 0.88,
        "Associated Press": 0.92,
        "Yahoo Finance": 0.75,
        "Seeking Alpha": 0.70,
        "Investor's Business Daily": 0.78,
        "Forbes": 0.80,
    }

    def __init__(self, api_key: str):
        """Initialize with NewsAPI key."""
        self.api_key = api_key
        self._init_sentiment_analyzer()

    def _init_sentiment_analyzer(self):
        """Initialize sentiment analysis (using TextBlob)."""
        try:
            from textblob import TextBlob
            self.TextBlob = TextBlob
            self.sentiment_available = True
            logger.info("Sentiment analysis initialized")
        except ImportError:
            logger.warning("TextBlob not available, sentiment analysis disabled")
            self.sentiment_available = False
            self.TextBlob = None

    def _analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """
        Analyze sentiment of text.
        
        Returns:
            Dictionary with sentiment_score (-1 to 1) and sentiment_label
        """
        if not self.sentiment_available or not text:
            return {
                "sentiment_score": 0.0,
                "sentiment_label": "neutral"
            }
        
        try:
            blob = self.TextBlob(text)
            polarity = blob.sentiment.polarity  # -1 to 1
            
            # Classify sentiment
            if polarity > 0.1:
                label = "positive"
            elif polarity < -0.1:
                label = "negative"
            else:
                label = "neutral"
            
            return {
                "sentiment_score": round(polarity, 3),
                "sentiment_label": label
            }
        except Exception as e:
            logger.warning(f"Sentiment analysis error: {str(e)}")
            return {
                "sentiment_score": 0.0,
                "sentiment_label": "neutral"
            }

    def _get_source_credibility(self, source_name: str) -> float:
        """Get credibility score for a news source."""
        # Check exact match
        if source_name in self.SOURCE_CREDIBILITY:
            return self.SOURCE_CREDIBILITY[source_name]
        
        # Check partial matches
        for known_source, score in self.SOURCE_CREDIBILITY.items():
            if known_source.lower() in source_name.lower():
                return score
        
        # Default credibility for unknown sources
        return 0.65

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
            query = symbol

            params = {
                "q": query,
                "from": from_date,
                "to": to_date,
                "language": "en",
                "sortBy": "relevancy",
                "pageSize": max_articles * 2,  # Fetch more to filter
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

            # Format articles with sentiment
            news_items = []
            for article in articles[:max_articles * 2]:
                title = article.get("title", "No title")
                description = article.get("description", "")
                source_name = article.get("source", {}).get("name", "Unknown")
                
                # Analyze sentiment
                text_for_sentiment = f"{title}. {description}"
                sentiment = self._analyze_sentiment(text_for_sentiment)
                
                # Get credibility
                credibility = self._get_source_credibility(source_name)
                
                news_items.append({
                    "title": title,
                    "source": source_name,
                    "published_at": article.get("publishedAt", ""),
                    "description": description,
                    "sentiment_score": sentiment["sentiment_score"],
                    "sentiment_label": sentiment["sentiment_label"],
                    "credibility_score": credibility,
                    "price_impact": None,  # Can be enhanced with correlation analysis
                })
            
            # Sort by credibility and relevance
            news_items.sort(key=lambda x: x["credibility_score"], reverse=True)
            news_items = news_items[:max_articles]

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

    def get_news_with_sentiment(
        self, symbol: str, target_date: str, max_articles: int = 10
    ) -> List[Dict]:
        """
        Get news with enhanced sentiment analysis for timeline visualization.
        
        Args:
            symbol: Stock ticker symbol
            target_date: Target date in YYYY-MM-DD format
            max_articles: Maximum articles to return
            
        Returns:
            List of news articles with sentiment analysis
        """
        return self.get_news(symbol, target_date, max_articles)

    def get_news_timeline(
        self, symbol: str, target_date: str, days_back: int = 7
    ) -> List[Dict]:
        """
        Get news timeline over multiple days.
        
        Args:
            symbol: Stock ticker symbol
            target_date: End date in YYYY-MM-DD format
            days_back: Number of days to look back
            
        Returns:
            List of news articles chronologically ordered
        """
        try:
            target_dt = datetime.strptime(target_date, "%Y-%m-%d")
            start_dt = target_dt - timedelta(days=days_back)
            
            from_date = start_dt.strftime("%Y-%m-%d")
            to_date = target_date
            
            params = {
                "q": symbol,
                "from": from_date,
                "to": to_date,
                "language": "en",
                "sortBy": "publishedAt",  # Chronological order
                "pageSize": 20,
                "apiKey": self.api_key,
            }
            
            response = requests.get(self.BASE_URL, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if data["status"] != "ok":
                return []
            
            articles = data.get("articles", [])
            
            timeline = []
            for article in articles:
                title = article.get("title", "No title")
                description = article.get("description", "")
                source_name = article.get("source", {}).get("name", "Unknown")
                
                text_for_sentiment = f"{title}. {description}"
                sentiment = self._analyze_sentiment(text_for_sentiment)
                credibility = self._get_source_credibility(source_name)
                
                timeline.append({
                    "title": title,
                    "source": source_name,
                    "published_at": article.get("publishedAt", ""),
                    "description": description,
                    "sentiment_score": sentiment["sentiment_score"],
                    "sentiment_label": sentiment["sentiment_label"],
                    "credibility_score": credibility,
                    "price_impact": None,
                })
            
            logger.info(f"Found {len(timeline)} articles in timeline for {symbol}")
            return timeline
            
        except Exception as e:
            logger.error(f"Error fetching news timeline: {str(e)}")
            return []


# Global instance
news_service = NewsService(settings.newsapi_key)
