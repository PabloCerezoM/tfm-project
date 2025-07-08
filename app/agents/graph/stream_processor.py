"""
Stream processor for handling agent graph streaming events.
"""
from typing import Generator, Tuple, List, Optional
from agents.state_types import State
from agents.graph.builder import compiled_graph
from core.models import StreamingUpdate
from core.constants import NodeNames, UIMessages, ProcessingIndicators
from utils.formatters import NewsFormatter


class StreamProcessor:
    """Processor for handling streaming events from the agent graph."""
    
    def __init__(self):
        self.graph = compiled_graph
        self.formatter = NewsFormatter()
    
    def _format_filter_results(self, all_news_filtered: List[dict]) -> str:
        """Format news filter results for display."""
        if not all_news_filtered:
            return "No news articles were processed."
        
        return self.formatter.format_filter_results([
            # Convert dict to NewsArticle for formatting
            type('NewsArticle', (), {
                'title': article.get('title', ''),
                'matched_interests': article.get('matched_interests', False)
            })() for article in all_news_filtered
        ])
    
    def _format_summaries(self, news_list: List[dict]) -> str:
        """Format article summaries for display."""
        if not news_list:
            return ""
        
        summaries = []
        for article_dict in news_list:
            title = article_dict.get('title', 'No title')
            source = article_dict.get('source', 'Unknown source')
            url = article_dict.get('url', '')
            summary = article_dict.get('summary', 'No summary available')
            
            summary_text = f"**{title}**\n"
            if url:
                summary_text += f"*{source}* - [Link to article]({url})\n\n"
            else:
                summary_text += f"*{source}*\n\n"
            summary_text += f"{summary}\n"
            
            summaries.append(summary_text)
        
        return "\n".join(summaries)
    
    def process_command_stream(self, message: str) -> Generator[Tuple[str, List[str], str, str], None, None]:
        """
        Process a user command and stream events from the graph.
        
        Args:
            message: User input message
            
        Yields:
            Tuples compatible with Gradio interface: (partial_response, visited_nodes, news_info, summaries_info)
        """
        inputs: State = {"user_input": message}
        last_state = None
        last_response = ""
        filter_news_info = ""
        current_summaries = []
        
        try:
            for event_type, value in self.graph.stream(inputs, stream_mode=["values", "custom"]):
                if event_type == "values":
                    last_state = value
                    visited_nodes = value.get("visited_nodes", [])
                    last_node = visited_nodes[-1] if visited_nodes else None
                    
                    # Update response based on current state
                    if "result" in value and value["result"]:
                        last_response = value["result"]
                    
                    # Handle specific node responses
                    if last_node == NodeNames.FILTER_NEWS:
                        # Extract filter info from current state
                        if "all_news_filtered" in value and value["all_news_filtered"]:
                            all_news = value["all_news_filtered"]
                            filter_news_info = self._format_filter_results(all_news)
                            
                            matched_count = sum(1 for n in all_news if n.get("matched_interests"))
                            last_response = f"Filtered {len(all_news)} news articles. {matched_count} matched your interests."
                        else:
                            if not filter_news_info:
                                filter_news_info = "No news articles were processed."
                                last_response = "No news articles found to filter."
                    
                    elif last_node == NodeNames.SUMMARIZE:
                        # Show completed summaries
                        news = value.get("news", [])
                        if news:
                            current_summaries = news
                            last_response = f"{UIMessages.SUMMARIES_COMPLETED} {len(news)} news articles"
                    
                    elif last_node == NodeNames.STORE_INTEREST:
                        last_response = value.get("result", "Interest stored successfully")
                    
                    elif last_node == NodeNames.LIST_INTERESTS:
                        last_response = value.get("result", "Listed interests")
                    
                    elif last_node == NodeNames.REMOVE_INTEREST:
                        last_response = value.get("result", "Interest removed")
                    
                    yield (last_response, visited_nodes, filter_news_info, "")
                
                else:
                    # Handle partial summaries during streaming
                    partial_data = value.get("partial_summaries", (None, None, None))
                    if partial_data[1] and isinstance(partial_data[1], list):
                        article_idx = partial_data[0]
                        partial_summaries = partial_data[1]
                        total_articles = partial_data[2] if len(partial_data) > 2 else len(partial_summaries)
                        
                        # Format summaries for display
                        formatted_summaries = self._format_summaries(partial_summaries)
                        
                        # Send real-time token updates
                        progress_msg = self.formatter.format_processing_status(article_idx, total_articles)
                        
                        yield (
                            progress_msg,
                            last_state.get("visited_nodes", []) if last_state else [],
                            filter_news_info,
                            formatted_summaries
                        )
            
            # Final yield with complete state
            if last_state:
                final_response = last_state.get("result", last_response)
                final_summaries_display = self._format_summaries(current_summaries) if current_summaries else ""
                
                yield (
                    final_response,
                    last_state.get("visited_nodes", []),
                    filter_news_info,
                    final_summaries_display
                )
                
        except Exception as e:
            print(f"[ERROR] Stream processing failed: {e}")
            error_message = f"An error occurred while processing your command: {str(e)}"
            yield (error_message, [], "", "")


# Global stream processor instance
stream_processor = StreamProcessor()
