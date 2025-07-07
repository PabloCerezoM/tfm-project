"""
Article summarization service using LLM.
"""
from typing import Generator, List
from core.models import NewsArticle
from core.constants import UIMessages
from services.llm.client import llm_client


class ArticleSummarizer:
    """Service for summarizing news articles using LLM."""
    
    def __init__(self):
        self.llm_client = llm_client
    
    def _create_summary_prompt(self, content: str) -> List[dict]:
        """Create prompt for article summarization."""
        return [
            {
                "role": "user",
                "content": f"Summarize the following news article in 3-4 sentences, and only output the summary:\n{content}"
            }
        ]
    
    def summarize_article(self, article: NewsArticle) -> str:
        """
        Summarize a single article.
        
        Args:
            article: NewsArticle instance with content
            
        Returns:
            Summary text
        """
        if not article.content:
            return UIMessages.CONTENT_NOT_AVAILABLE
        
        try:
            prompt = self._create_summary_prompt(article.content)
            summary = self.llm_client.invoke(prompt)
            return summary
        except Exception as e:
            print(f"[ERROR] Failed to summarize article '{article.title}': {e}")
            return f"Failed to generate summary: {str(e)}"
    
    def summarize_article_stream(self, article: NewsArticle) -> Generator[str, None, None]:
        """
        Summarize an article with streaming output.
        
        Args:
            article: NewsArticle instance with content
            
        Yields:
            Summary tokens as they are generated
        """
        if not article.content:
            yield UIMessages.CONTENT_NOT_AVAILABLE
            return
        
        try:
            prompt = self._create_summary_prompt(article.content)
            for token in self.llm_client.stream(prompt):
                if token:
                    yield token
        except Exception as e:
            print(f"[ERROR] Failed to stream summary for article '{article.title}': {e}")
            yield f"Failed to generate summary: {str(e)}"
    
    def summarize_articles_batch(self, articles: List[NewsArticle]) -> List[NewsArticle]:
        """
        Summarize multiple articles in batch (non-streaming).
        
        Args:
            articles: List of NewsArticle instances
            
        Returns:
            List of articles with updated summaries
        """
        for article in articles:
            article.summary = self.summarize_article(article)
        
        return articles


# Global summarizer instance
article_summarizer = ArticleSummarizer()
