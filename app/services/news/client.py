"""
News API client for fetching news articles.
"""
import requests
from typing import List
from config.settings import settings
from core.exceptions import NewsAPIError
from core.constants import APIStatus
from core.models import NewsArticle
from services.news.models import RawNewsArticle


class NewsAPIClient:
    """Client for interacting with News API."""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or settings.NEWS_API_KEY
        self.base_url = "https://newsapi.org/v2"
        
        if not self.api_key:
            raise NewsAPIError("News API key not configured")
    
    def fetch_top_headlines(
        self, 
        page_size: int = None, 
        language: str = None,
        country: str = None,
        category: str = None
    ) -> List[NewsArticle]:
        """
        Fetch top headlines from News API.
        
        Args:
            page_size: Number of articles to return
            language: Language code (e.g., 'en', 'es')
            country: Country code (e.g., 'us', 'es')
            category: Category (business, entertainment, general, health, science, sports, technology)
        """
        url = f"{self.base_url}/top-headlines"
        
        params = {
            "apiKey": self.api_key,
            "pageSize": page_size or settings.DEFAULT_PAGE_SIZE,
            "language": language or settings.DEFAULT_LANGUAGE,
        }
        
        # Add optional parameters
        if country:
            params["country"] = country
        if category:
            params["category"] = category
        
        try:
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get("status") != APIStatus.OK:
                error_msg = data.get("message", "Unknown News API error")
                raise NewsAPIError(f"News API error: {error_msg}")
            
            # Convert raw articles to NewsArticle instances
            articles = []
            for article_data in data.get("articles", []):
                try:
                    raw_article = RawNewsArticle.from_api_response(article_data)
                    news_article = NewsArticle(
                        title=raw_article.title,
                        content=raw_article.description,
                        url=raw_article.url,
                        source=raw_article.source.name,
                    )
                    articles.append(news_article)
                except Exception as e:
                    # Log error but continue processing other articles
                    print(f"[WARNING] Failed to process article: {e}")
                    continue
            
            return articles
            
        except requests.RequestException as e:
            raise NewsAPIError(f"Failed to fetch news: {str(e)}")
        except Exception as e:
            raise NewsAPIError(f"Unexpected error while fetching news: {str(e)}")


# Global news client instance
news_client = NewsAPIClient()
