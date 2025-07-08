"""
New modular agent graph implementation.
Exports the same interface as the original for compatibility.
"""
from agents.graph.stream_processor import stream_processor


def process_command_stream(message: str):
    """
    Process a user command and stream events from the graph.
    Returns tuples compatible with Gradio interface: (partial_response, visited_nodes, news_info, summaries_info)
    
    This function maintains compatibility with the original implementation.
    """
    return stream_processor.process_command_stream(message)


def main():
    """
    Test function for debugging the agent graph.
    This function is kept for testing purposes but not used as main entry point.
    """
    from dotenv import load_dotenv
    
    load_dotenv()
    print("🧪 Testing new modular agent graph...")
    
    for partial_response, visited_nodes, news_info, summaries_info in process_command_stream("Show me the news"):
        print("=" * 50)
        print(f"Visited Nodes: {' → '.join(visited_nodes) if visited_nodes else 'None'}")
        print(f"Response: {partial_response}")
        if news_info:
            print(f"News Filter Info (length {len(news_info)}):\n{news_info[:300]}{'...' if len(news_info) > 300 else ''}")
        else:
            print("News Filter Info: EMPTY")
        if summaries_info:
            print(f"Summaries Info:\n{summaries_info[:200]}{'...' if len(summaries_info) > 200 else ''}")
        print("=" * 50)


if __name__ == "__main__":
    main()
