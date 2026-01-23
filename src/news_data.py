"""
News Data Module
Fetches relevant news articles from NewsAPI and RSS feeds.
"""

import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import requests
from newsapi import NewsApiClient
import feedparser
from dotenv import load_dotenv

load_dotenv()


class NewsDataFetcher:
    """Fetches news articles related to stocks and market events."""
    
    def __init__(self):
        """Initialize the news data fetcher with API keys."""
        self.newsapi_key = os.getenv("NEWSAPI_KEY")
        self.newsapi_client = None
        
        if self.newsapi_key and self.newsapi_key != "your_newsapi_key_here":
            try:
                self.newsapi_client = NewsApiClient(api_key=self.newsapi_key)
            except Exception as e:
                print(f"Warning: Failed to initialize NewsAPI client: {e}")
    
    def fetch_news_for_symbol(self, symbol: str, date: str, days_before: int = 1) -> List[Dict]:
        """
        Fetch news articles related to a stock symbol around a specific date.
        
        Args:
            symbol: Stock ticker symbol
            date: Target date in YYYY-MM-DD format
            days_before: Number of days before target date to search
            
        Returns:
            List of news articles
        """
        target_date = datetime.strptime(date, "%Y-%m-%d")
        from_date = target_date - timedelta(days=days_before)
        to_date = target_date + timedelta(days=1)
        
        articles = []
        
        # Try NewsAPI first
        if self.newsapi_client:
            try:
                newsapi_articles = self._fetch_from_newsapi(
                    symbol, 
                    from_date.strftime("%Y-%m-%d"),
                    to_date.strftime("%Y-%m-%d")
                )
                articles.extend(newsapi_articles)
            except Exception as e:
                print(f"NewsAPI error: {e}")
        
        # Fallback to Google News RSS
        if len(articles) < 3:
            try:
                rss_articles = self._fetch_from_google_news_rss(symbol)
                articles.extend(rss_articles)
            except Exception as e:
                print(f"RSS feed error: {e}")
        
        # Filter articles by date range and remove duplicates
        articles = self._filter_and_deduplicate(articles, from_date, to_date)
        
        return articles[:15]  # Limit to top 15 articles
    
    def _fetch_from_newsapi(self, symbol: str, from_date: str, to_date: str) -> List[Dict]:
        """Fetch articles from NewsAPI."""
        # Get company name for better search (simplified - would need mapping)
        query = f"{symbol} stock OR {symbol} shares"
        
        sources = os.getenv("NEWS_SOURCES", "bloomberg,reuters,cnbc,the-wall-street-journal")
        
        try:
            response = self.newsapi_client.get_everything(
                q=query,
                from_param=from_date,
                to=to_date,
                language='en',
                sort_by='relevancy',
                page_size=20
            )
            
            articles = []
            for article in response.get('articles', []):
                articles.append({
                    'title': article['title'],
                    'description': article.get('description', ''),
                    'url': article['url'],
                    'source': article['source']['name'],
                    'published_at': article['publishedAt'],
                    'content_snippet': article.get('content', '')[:200] if article.get('content') else ''
                })
            
            return articles
        except Exception as e:
            print(f"Error fetching from NewsAPI: {e}")
            return []
    
    def _fetch_from_google_news_rss(self, symbol: str) -> List[Dict]:
        """Fetch articles from Google News RSS feed."""
        query = f"{symbol} stock"
        url = f"https://news.google.com/rss/search?q={query}&hl=en-US&gl=US&ceid=US:en"
        
        try:
            feed = feedparser.parse(url)
            articles = []
            
            for entry in feed.entries[:10]:
                articles.append({
                    'title': entry.title,
                    'description': entry.get('summary', ''),
                    'url': entry.link,
                    'source': entry.get('source', {}).get('title', 'Google News'),
                    'published_at': entry.get('published', ''),
                    'content_snippet': entry.get('summary', '')[:200]
                })
            
            return articles
        except Exception as e:
            print(f"Error fetching from Google News RSS: {e}")
            return []
    
    def _filter_and_deduplicate(self, articles: List[Dict], from_date: datetime, to_date: datetime) -> List[Dict]:
        """Filter articles by date and remove duplicates."""
        seen_titles = set()
        filtered = []
        
        for article in articles:
            # Skip duplicates
            title_lower = article['title'].lower()
            if title_lower in seen_titles:
                continue
            
            seen_titles.add(title_lower)
            filtered.append(article)
        
        return filtered
    
    def summarize_news(self, articles: List[Dict]) -> Dict:
        """
        Create a summary of news articles.
        
        Args:
            articles: List of news articles
            
        Returns:
            Summary dictionary
        """
        if not articles:
            return {
                'count': 0,
                'top_headlines': [],
                'sources': [],
                'has_significant_news': False
            }
        
        # Extract top headlines
        top_headlines = [
            {
                'title': article['title'],
                'source': article['source'],
                'url': article['url']
            }
            for article in articles[:5]
        ]
        
        # Count unique sources
        sources = list(set(article['source'] for article in articles))
        
        # Determine if there's significant news (basic heuristic)
        significant_keywords = [
            'earnings', 'revenue', 'profit', 'loss', 'beat', 'miss',
            'merger', 'acquisition', 'lawsuit', 'investigation', 'fda',
            'approved', 'rejected', 'guidance', 'outlook', 'CEO', 'layoff'
        ]
        
        has_significant = any(
            any(keyword in article['title'].lower() for keyword in significant_keywords)
            for article in articles
        )
        
        return {
            'count': len(articles),
            'top_headlines': top_headlines,
            'sources': sources,
            'has_significant_news': has_significant
        }
    
    def get_market_news(self, date: str, days_before: int = 1) -> List[Dict]:
        """
        Fetch general market news for a specific date.
        
        Args:
            date: Target date in YYYY-MM-DD format
            days_before: Number of days before target date to search
            
        Returns:
            List of market-related articles
        """
        queries = ["stock market", "S&P 500", "market rally", "market sell-off"]
        
        all_articles = []
        for query in queries:
            if self.newsapi_client:
                try:
                    target_date = datetime.strptime(date, "%Y-%m-%d")
                    from_date = target_date - timedelta(days=days_before)
                    
                    response = self.newsapi_client.get_everything(
                        q=query,
                        from_param=from_date.strftime("%Y-%m-%d"),
                        to=target_date.strftime("%Y-%m-%d"),
                        language='en',
                        sort_by='relevancy',
                        page_size=5
                    )
                    
                    for article in response.get('articles', []):
                        all_articles.append({
                            'title': article['title'],
                            'description': article.get('description', ''),
                            'url': article['url'],
                            'source': article['source']['name'],
                            'published_at': article['publishedAt']
                        })
                except Exception as e:
                    print(f"Error fetching market news: {e}")
        
        # Deduplicate
        return self._filter_and_deduplicate(
            all_articles,
            datetime.strptime(date, "%Y-%m-%d") - timedelta(days=days_before),
            datetime.strptime(date, "%Y-%m-%d")
        )[:10]
