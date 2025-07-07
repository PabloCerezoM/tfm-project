"""
Formatting utilities for display and output.
"""
from typing import List
from core.models import NewsArticle, StreamingUpdate
from core.constants import MatchStatus, ProcessingIndicators, UIMessages


class NewsFormatter:
    """Formatter for news-related display content."""
    
    @staticmethod
    def format_visited_nodes(nodes: List[str]) -> str:
        """
        Format visited nodes for display.
        
        Args:
            nodes: List of node names
            
        Returns:
            Formatted nodes string
        """
        if not nodes:
            return ""
        
        return ProcessingIndicators.ARROW.join(str(node) for node in nodes)
    
    @staticmethod
    def format_filter_results(articles: List[NewsArticle]) -> str:
        """
        Format news filter results for display.
        
        Args:
            articles: List of NewsArticle instances with match information
            
        Returns:
            Formatted filter results string
        """
        if not articles:
            return "No news articles were processed."
        
        filter_info = []
        matched_count = 0
        
        for article in articles:
            title = article.title or 'No title'
            match_status = MatchStatus.MATCH if article.matched_interests else MatchStatus.NO_MATCH
            
            if article.matched_interests:
                matched_count += 1
            
            filter_info.append(f"{match_status}: {title}")
        
        result = "\n".join(filter_info)
        summary = f"\nFiltered {len(articles)} news articles. {matched_count} matched your interests."
        
        return result + summary
    
    @staticmethod
    def format_article_summary(article: NewsArticle) -> str:
        """
        Format a single article summary for display.
        
        Args:
            article: NewsArticle instance with summary
            
        Returns:
            Formatted article summary
        """
        title = article.title or 'No title'
        source = article.source or 'Unknown source'
        url = article.url
        summary = article.summary or 'No summary available'
        
        # Format: Title and source with link, then line break, then summary
        summary_text = f"**{title}**\n"
        
        if url:
            summary_text += f"*{source}* - [Link to article]({url})\n\n"
        else:
            summary_text += f"*{source}*\n\n"
        
        summary_text += f"{summary}\n"
        
        return summary_text
    
    @staticmethod
    def format_article_summaries(articles: List[NewsArticle]) -> str:
        """
        Format multiple article summaries for display.
        
        Args:
            articles: List of NewsArticle instances with summaries
            
        Returns:
            Formatted summaries string
        """
        if not articles:
            return ""
        
        summaries = []
        for article in articles:
            summary_text = NewsFormatter.format_article_summary(article)
            summaries.append(summary_text)
        
        return "\n".join(summaries)
    
    @staticmethod
    def format_processing_status(current_article: int, total_articles: int) -> str:
        """
        Format processing status message.
        
        Args:
            current_article: Current article index (0-based)
            total_articles: Total number of articles
            
        Returns:
            Formatted status message
        """
        return f"{UIMessages.GENERATING_SUMMARIES} (Article {current_article + 1}/{total_articles})"
    
    @staticmethod
    def format_completion_message(article_count: int) -> str:
        """
        Format completion message.
        
        Args:
            article_count: Number of articles processed
            
        Returns:
            Formatted completion message
        """
        return f"{UIMessages.SUMMARIES_COMPLETED} {article_count} news articles"


class InterestFormatter:
    """Formatter for interest-related display content."""
    
    @staticmethod
    def format_interests_list(interests: List[str]) -> str:
        """
        Format interests list for display.
        
        Args:
            interests: List of interest strings
            
        Returns:
            Formatted interests string
        """
        if not interests:
            return "You have no interests stored."
        
        return "Your current interests: " + ", ".join(interests)
    
    @staticmethod
    def format_interest_added(interest: str, current_interests: List[str]) -> str:
        """
        Format message for added interest.
        
        Args:
            interest: The added interest
            current_interests: Current list of interests
            
        Returns:
            Formatted message
        """
        interests_str = InterestFormatter.format_interests_list(current_interests)
        return f"Interest '{interest}' added. Current interests: {', '.join(current_interests)}"
    
    @staticmethod
    def format_interest_removed(interest: str, current_interests: List[str]) -> str:
        """
        Format message for removed interest.
        
        Args:
            interest: The removed interest
            current_interests: Current list of interests
            
        Returns:
            Formatted message
        """
        return f"Interest '{interest}' removed. Current interests: {', '.join(current_interests)}"
    
    @staticmethod
    def format_interest_not_found(interest: str) -> str:
        """
        Format message for interest not found.
        
        Args:
            interest: The interest that wasn't found
            
        Returns:
            Formatted message
        """
        return f"Interest '{interest}' not found in your current interests."
