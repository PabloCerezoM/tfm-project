"""
Content processing nodes for scraping and summarizing articles.
"""
from typing import List, Generator
from concurrent.futures import ThreadPoolExecutor
from langchain_openai import ChatOpenAI
from langgraph.config import get_stream_writer
from agents.state_types import State
from services.news.scraper import content_scraper
from services.llm.summarizer import article_summarizer
from core.models import NewsArticle
from core.exceptions import ContentScrapingError
from core.constants import UIMessages
from utils.formatters import NewsFormatter


class ContentProcessorNode:
    """Node responsible for content scraping and summarization."""
    
    def __init__(self, llm: ChatOpenAI):
        self.scraper = content_scraper
        self.summarizer = article_summarizer
        self.formatter = NewsFormatter()
    
    def scrape_content(self, state: State) -> State:
        """
        Scrape full content for each news article.
        
        Args:
            state: Current state containing news articles with URLs
            
        Returns:
            Updated state with articles containing full content
        """
        news_articles = state.get("news", [])
        
        if not news_articles:
            print("[INFO] No news articles to scrape")
            return state
        
        try:
            # Convert to NewsArticle objects
            articles = [NewsArticle.from_dict(article_dict) for article_dict in news_articles]
            
            # Scrape content for all articles
            articles_with_content = self.scraper.scrape_articles_content(articles)
            
            # Convert back to dict format for state compatibility
            updated_news = []
            content_count = 0
            
            for article in articles_with_content:
                article_dict = article.to_dict()
                updated_news.append(article_dict)
                
                if article.content:
                    content_count += 1
            
            state["news"] = updated_news
            print(f"[INFO] Scraped content for {content_count}/{len(articles)} articles")
            
        except Exception as e:
            print(f"[ERROR] Unexpected error scraping content: {e}")
            # Continue with existing content if scraping fails
            print("[WARNING] Continuing with existing article descriptions")
        
        return state
    
    def _summarize_article_stream(self, article: NewsArticle) -> Generator[str, None, None]:
        """Generate streaming summary for a single article."""
        try:
            for token in self.summarizer.summarize_article_stream(article):
                if token:
                    yield token
        except Exception as e:
            print(f"[ERROR] Failed to stream summary for '{article.title}': {e}")
            yield f"Failed to generate summary: {str(e)}"
    
    def summarize(self, state: State) -> State:
        """
        Summarize articles with streaming output.
        
        Args:
            state: Current state containing news articles with content
            
        Returns:
            Updated state with summarized articles
        """
        news_articles = state.get("news", [])
        
        if not news_articles:
            print("[INFO] No news articles to summarize")
            return state
        
        try:
            writer = get_stream_writer()
            completed_summaries = []
            total_articles = len(news_articles)
            
            for news_idx, article_dict in enumerate(news_articles):
                try:
                    # Convert to NewsArticle object
                    article = NewsArticle.from_dict(article_dict)
                    
                    if not article.content:
                        print(f"[DEBUG] No content for article {news_idx}: {article.title}")
                        article.summary = UIMessages.CONTENT_NOT_AVAILABLE
                        completed_summaries.append(article)
                        
                        # Send partial update
                        writer({"partial_summaries": (news_idx, [a.to_dict() for a in completed_summaries], total_articles)})
                        continue
                    
                    # Generate streaming summary
                    summary = ""
                    for token in self._summarize_article_stream(article):
                        if token is None:
                            continue
                        
                        summary += token
                        
                        # Send partial summary for current article
                        current_partial = NewsArticle(
                            title=article.title,
                            content=article.content,
                            url=article.url,
                            source=article.source,
                            summary=summary + "...",
                            matched_interests=article.matched_interests,
                            match_reason=article.match_reason
                        )
                        temp_summaries = completed_summaries + [current_partial]
                        
                        writer({"partial_summaries": (news_idx, [a.to_dict() for a in temp_summaries], total_articles)})
                    
                    # Complete the summary
                    article.summary = summary
                    completed_summaries.append(article)
                    
                    # Send completed summary
                    writer({"partial_summaries": (news_idx, [a.to_dict() for a in completed_summaries], total_articles)})
                    
                except Exception as e:
                    print(f"[ERROR] Failed to summarize article {news_idx}: {e}")
                    # Create a fallback article with error message
                    article = NewsArticle.from_dict(article_dict)
                    article.summary = f"Failed to generate summary: {str(e)}"
                    completed_summaries.append(article)
                    
                    writer({"partial_summaries": (news_idx, [a.to_dict() for a in completed_summaries], total_articles)})
            
            # Update state with completed summaries
            state["news"] = [article.to_dict() for article in completed_summaries]
            
            print(f"[INFO] Completed summaries for {len(completed_summaries)} articles")
            
        except Exception as e:
            print(f"[ERROR] Unexpected error during summarization: {e}")
            state["result"] = f"An error occurred during summarization: {str(e)}"
        
        return state
