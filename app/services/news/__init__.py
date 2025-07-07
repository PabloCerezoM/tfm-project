"""
News service package - exports legacy interface for backward compatibility.
"""
from services.news.client import news_client


def fetch_news(page_size=15, language="en"):
    """
    Fetch news articles - delegates to new client.
    Returns articles in legacy format for compatibility.
    """
    articles = news_client.fetch_top_headlines(page_size=page_size, language=language)
    
    # Convert to legacy format
    legacy_articles = []
    for article in articles:
        legacy_articles.append({
            "title": article.title,
            "content": article.content,
            "url": article.url,
            "source": article.source,
        })
    
    return legacy_articles


# Export functions for backward compatibility
__all__ = ['fetch_news']