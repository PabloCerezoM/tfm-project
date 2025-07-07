"""
Content scraper for extracting full article content.
"""
from newspaper import Article
from typing import Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
from core.exceptions import ContentScrapingError
from core.models import NewsArticle


class ContentScraper:
    """Scraper for extracting full content from news articles."""
    
    def __init__(self, max_workers: int = 5, timeout: int = 30):
        self.max_workers = max_workers
        self.timeout = timeout
    
    def scrape_article_content(self, url: str) -> Optional[str]:
        """
        Scrape full content from a single article URL.
        
        Args:
            url: The URL to scrape
            
        Returns:
            The article content or None if scraping failed
        """
        if not url:
            return None
        
        try:
            article = Article(url)
            article.download()
            article.parse()
            return article.text
        except Exception as e:
            print(f"[WARNING] Failed to scrape content from {url}: {e}")
            return None
    
    def scrape_articles_content(self, articles: list[NewsArticle]) -> list[NewsArticle]:
        """
        Scrape full content for multiple articles concurrently.
        
        Args:
            articles: List of NewsArticle instances
            
        Returns:
            List of NewsArticle instances with updated content
        """
        if not articles:
            return articles
        
        # Create a mapping of URLs to articles for easier updates
        url_to_article = {article.url: article for article in articles if article.url}
        
        if not url_to_article:
            return articles
        
        # Scrape content concurrently
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit scraping tasks
            future_to_url = {
                executor.submit(self.scrape_article_content, url): url 
                for url in url_to_article.keys()
            }
            
            # Process results as they complete
            for future in as_completed(future_to_url):
                url = future_to_url[future]
                try:
                    content = future.result(timeout=self.timeout)
                    if content:
                        url_to_article[url].content = content
                except Exception as e:
                    print(f"[WARNING] Failed to get result for {url}: {e}")
        
        return articles


# Global scraper instance
content_scraper = ContentScraper()
