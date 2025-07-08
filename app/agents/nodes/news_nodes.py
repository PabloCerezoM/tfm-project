"""
News processing nodes for fetching and filtering news articles.
"""
from typing import List
from concurrent.futures import ThreadPoolExecutor
from langchain_openai import ChatOpenAI
from agents.state_types import State
from services.news.client import news_client
from services.memory.repository import interests_repository
from services.llm.client import LLMClient
from core.models import NewsArticle
from core.exceptions import NewsAPIError, LLMError
from core.constants import UIMessages
from utils.formatters import NewsFormatter
from config.settings import settings


class NewsProcessorNode:
    """Node responsible for news processing operations."""
    
    def __init__(self, llm: ChatOpenAI):
        self.news_client = news_client
        self.interests_repository = interests_repository
        self.llm_client = LLMClient(llm)
        self.formatter = NewsFormatter()
    
    def _is_news_about_interest(self, article: NewsArticle, interests: List[str]) -> tuple[bool, str]:
        """Check if a news article is related to any of the user's interests."""
        interests_str = ', '.join(interests)
        prompt = [
            {
                "role": "system", 
                "content": f"You are an assistant that determines if a news article is related to any of the following user interests: {interests_str}.\nRespond ONLY with 'yes' or 'no', and if 'yes', indicate which interest(s)."
            },
            {
                "role": "user", 
                "content": f"NEWS:\nTitle: {article.title}\nContent: {article.content}"
            }
        ]
        
        try:
            response = self.llm_client.invoke(prompt)
            content = response.lower()
            
            if "yes" in content:
                return True, content
            return False, content
            
        except LLMError as e:
            print(f"[ERROR] LLM error in interest matching: {e}")
            return False, f"Error checking interest match: {str(e)}"
    
    def fetch_news(self, state: State) -> State:
        """
        Fetch news articles from the news service.
        
        Args:
            state: Current state
            
        Returns:
            Updated state with fetched news articles
        """
        try:
            articles = self.news_client.fetch_top_headlines(
                page_size=settings.DEFAULT_PAGE_SIZE,
                language=settings.DEFAULT_LANGUAGE
            )
            
            # Convert to legacy format for compatibility with existing state structure
            legacy_articles = []
            for article in articles:
                legacy_articles.append({
                    "title": article.title,
                    "content": article.content,
                    "url": article.url,
                    "source": article.source,
                })
            
            state["news"] = legacy_articles
            print(f"[INFO] Fetched {len(legacy_articles)} news articles")
            
        except NewsAPIError as e:
            print(f"[ERROR] Failed to fetch news: {e}")
            state["news"] = []
            state["result"] = f"Failed to fetch news: {str(e)}"
        except Exception as e:
            print(f"[ERROR] Unexpected error fetching news: {e}")
            state["news"] = []
            state["result"] = "An unexpected error occurred while fetching news."
        
        return state
    
    def filter_news(self, state: State) -> State:
        """
        Filter news articles based on user interests.
        
        Args:
            state: Current state containing news articles
            
        Returns:
            Updated state with filtered news and filter information
        """
        try:
            interests = self.interests_repository.get_interests_list()
            original_news = state.get("news", [])
            
            if not interests:
                # If no interests are set, mark all news as no match
                all_news_with_matches = []
                for news_dict in original_news:
                    news_dict_copy = news_dict.copy()
                    news_dict_copy["matched_interests"] = False
                    news_dict_copy["match_reason"] = UIMessages.NO_INTERESTS_CONFIGURED
                    all_news_with_matches.append(news_dict_copy)
                
                state["all_news_filtered"] = all_news_with_matches
                state["news"] = []  # No news matches since no interests
                return state
            
            def check_match(news_dict):
                """Check if a single news article matches interests."""
                try:
                    # Convert to NewsArticle for processing
                    article = NewsArticle.from_dict(news_dict)
                    match, reason = self._is_news_about_interest(article, interests)
                    
                    news_dict_copy = news_dict.copy()
                    news_dict_copy["matched_interests"] = match
                    news_dict_copy["match_reason"] = reason if match else UIMessages.NO_MATCH_WITH_INTERESTS
                    
                    return news_dict_copy
                except Exception as e:
                    print(f"[ERROR] Failed to check match for article: {e}")
                    news_dict_copy = news_dict.copy()
                    news_dict_copy["matched_interests"] = False
                    news_dict_copy["match_reason"] = f"Error checking match: {str(e)}"
                    return news_dict_copy
            
            # Process articles concurrently
            with ThreadPoolExecutor(max_workers=5) as executor:
                all_news_with_matches = list(executor.map(check_match, original_news))
            
            # Store all news with match information for display
            state["all_news_filtered"] = all_news_with_matches
            
            # Keep only matched news for further processing
            filtered_news = [
                n for n in all_news_with_matches 
                if n.get("matched_interests") and n.get("url")
            ]
            state["news"] = filtered_news
            
            matched_count = len(filtered_news)
            total_count = len(original_news)
            
            print(f"[INFO] Filtered {total_count} articles, {matched_count} matched interests")
            
        except Exception as e:
            print(f"[ERROR] Unexpected error filtering news: {e}")
            state["all_news_filtered"] = []
            state["news"] = []
            state["result"] = "An unexpected error occurred while filtering news."
        
        return state
