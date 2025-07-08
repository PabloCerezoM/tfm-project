"""
Legacy tools - delegates to new node implementations.
This file is kept for backward compatibility with existing code.
"""
from agents.nodes.interest_nodes import InterestManagerNode
from agents.nodes.news_nodes import NewsProcessorNode
from agents.nodes.content_nodes import ContentProcessorNode
from config.llm_config import llm

# Initialize node instances
interest_manager = InterestManagerNode()
news_processor = NewsProcessorNode(llm)
content_processor = ContentProcessorNode(llm)

# Export legacy functions that delegate to new implementations
def tool_store_interest_node(state):
    """Legacy function - delegates to InterestManagerNode."""
    return interest_manager.store_interest(state)

def tool_list_interests_node(state):
    """Legacy function - delegates to InterestManagerNode."""
    return interest_manager.list_interests(state)

def tool_remove_interest_node(state):
    """Legacy function - delegates to InterestManagerNode."""
    return interest_manager.remove_interest(state)

def fetch_news_node(state):
    """Legacy function - delegates to NewsProcessorNode."""
    return news_processor.fetch_news(state)

def build_tools_filter_news_node(llm):
    """Legacy function - returns filter function that delegates to NewsProcessorNode."""
    def filter_node(state):
        return news_processor.filter_news(state)
    return filter_node

def scrape_content_node(state):
    """Legacy function - delegates to ContentProcessorNode."""
    return content_processor.scrape_content(state)

def build_summarize_node(llm):
    """Legacy function - returns summarize function that delegates to ContentProcessorNode."""
    def summarize_node(state):
        return content_processor.summarize(state)
    return summarize_node
