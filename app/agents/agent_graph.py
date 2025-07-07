import os
import json

from dotenv import load_dotenv
from typing import Callable
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END
from agents.state_types import State
from agents.command_parser import parse_command_node
from agents.tools import (
    tool_store_interest_node, 
    fetch_news_node,
    build_tools_filter_news_node,
    tool_list_interests_node, 
    tool_remove_interest_node,
    scrape_content_node,
    build_summarize_node,
)

def add_visited_node(state: State, node_name: str) -> State:
    if "visited_nodes" not in state or state["visited_nodes"] is None:
        state["visited_nodes"] = []
    state["visited_nodes"].append(node_name)
    return state

def make_node(fn: Callable[[State], State], node_name: str) -> Callable[[State], State]:
    def wrapped(state: State) -> State:
        add_visited_node(state, node_name)
        return fn(state)
    return wrapped

API_KEY = os.environ.get("API_KEY")
SERVER_URL = os.environ.get("SERVER_URL")
MODEL_ID = os.environ.get("MODEL_ID")

llm = ChatOpenAI(
    model=MODEL_ID,
    openai_api_key=API_KEY,
    openai_api_base=SERVER_URL,
    max_tokens=2048,
    temperature=0.7,
    top_p=0.9,
    streaming=True,  # Habilitar streaming
)

graph = StateGraph(State)
graph.add_node("parse_command", make_node(parse_command_node(llm), "parse_command"))
graph.add_node("list_interests", make_node(tool_list_interests_node, "list_interests"))
graph.add_node("remove_interest", make_node(tool_remove_interest_node, "remove_interest"))
graph.add_node("store_interest", make_node(tool_store_interest_node, "store_interest"))
graph.add_node("fetch_news", make_node(fetch_news_node, "fetch_news"))
graph.add_node("filter_news", make_node(build_tools_filter_news_node(llm), "filter_news"))
graph.add_node("scrape_content", make_node(scrape_content_node, "scrape_content"))
graph.add_node("summarize", make_node(build_summarize_node(llm), "summarize"))

def route_action(state: State) -> str:
    action = state.get("action")
    if action == "store_interest":
        return "store_interest"
    elif action == "fetch_news":
        return "fetch_news"
    elif action == "list_interests":
        return "list_interests"
    elif action == "remove_interest":
        return "remove_interest"
    else:
        state["result"] = "Sorry, I didn't understand the command. Please try again."
        return "END"

graph.add_conditional_edges(
    "parse_command",
    route_action,
    {
        "store_interest": "store_interest",
        "fetch_news": "fetch_news",
        "list_interests": "list_interests",
        "remove_interest": "remove_interest",  
        "final_output": END,  # This is a catch-all for unrecognized actions
    },
)
graph.add_edge("store_interest", END)
graph.add_edge("fetch_news", "filter_news")
graph.add_edge("filter_news", "scrape_content")
graph.add_edge("scrape_content", "summarize")
graph.add_edge("summarize", END)
graph.add_edge("list_interests", END)
graph.add_edge("remove_interest", END)

graph.set_entry_point("parse_command")

my_graph = graph.compile()

def process_command_stream(message: str):
    """
    Process a user command and stream events from the graph.
    Returns tuples compatible with Gradio interface: (partial_response, visited_nodes, news_info, summaries_info)
    """
    inputs: State = {"user_input": message}
    last_state = None
    last_response = ""
    filter_news_info = ""  # Separate variable to preserve filter info
    current_summaries = []
    
    for event_type, value in my_graph.stream(inputs, stream_mode=["values", "custom"]):  
        if event_type == "values":
            last_state = value  # Store the last state
            visited_nodes = value.get("visited_nodes", [])
            last_node = visited_nodes[-1] if visited_nodes else None
            
            # Update response based on current state
            if "result" in value and value["result"]:
                last_response = value["result"]
            
            # Handle specific node responses
            if last_node == "filter_news":
                # Extract filter info from current state's all_news_filtered
                if "all_news_filtered" in value and value["all_news_filtered"]:
                    all_news = value["all_news_filtered"]
                    filter_info = []
                    matched_count = 0
                    for n in all_news:
                        title = n.get('title', 'No title')
                        match_status = "✅ MATCH" if n.get("matched_interests") else "❌ NO MATCH"
                        if n.get("matched_interests"):
                            matched_count += 1
                        filter_info.append(f"{match_status}: {title}\n")
                    
                    filter_news_info = "\n".join(filter_info)
                    last_response = f"Filtered {len(all_news)} news articles. {matched_count} matched your interests."
                else:
                    if not filter_news_info:  # Only set if not already set above
                        filter_news_info = "No news articles were processed."
                        last_response = "No news articles found to filter."
                    
            elif last_node == "summarize":
                # Show all completed summaries
                news = value.get("news", [])
                if news:
                    summaries = []
                    for n in news:
                        title = n.get('title', 'No title')
                        source = n.get('source', 'Unknown source')
                        url = n.get('url', '')
                        summary = n.get('summary', 'No summary available')
                        
                        # Format: Title and source with link, then line break, then summary
                        summary_text = f"**{title}**\n"
                        if url:
                            summary_text += f"*{source}* - [Link to article]({url})\n\n"
                        else:
                            summary_text += f"*{source}*\n\n"
                        summary_text += f"{summary}\n"
                        
                        summaries.append(summary_text)
                    current_summaries = summaries
                    last_response = f"✅ Completed summaries for {len(news)} news articles"
                    
            elif last_node == "store_interest":
                last_response = value.get("result", "Interest stored successfully")
                
            elif last_node == "list_interests":
                last_response = value.get("result", "Listed interests")
                
            elif last_node == "remove_interest":
                last_response = value.get("result", "Interest removed")
            
            yield (last_response, visited_nodes, filter_news_info, "")
            
        else:
            # Handle partial summaries during streaming - token by token
            partial_data = value.get("partial_summaries", (None, None, None))
            if partial_data[1] and isinstance(partial_data[1], list):  # List of partial summaries
                summaries = []
                for i, n in enumerate(partial_data[1]):
                    title = n.get('title', 'No title')
                    source = n.get('source', 'Unknown source')
                    url = n.get('url', '')
                    summary = n.get('summary', 'Generating...')
                    
                    # Format: Title and source with link, then line break, then summary
                    summary_text = f"**{title}**\n"
                    if url:
                        summary_text += f"*{source}* - [Link to article]({url})\n\n"
                    else:
                        summary_text += f"*{source}*\n\n"
                    summary_text += f"{summary}\n"
                    
                    summaries.append(summary_text)
                
                current_summaries = summaries
                article_idx = partial_data[0]
                total_articles = partial_data[2] if len(partial_data) > 2 else len(partial_data[1])
                # Send real-time token updates
                yield (f"📝 Generating summaries... (Article {article_idx + 1}/{total_articles})", 
                      last_state.get("visited_nodes", []) if last_state else [], 
                      filter_news_info,
                      "\n".join(current_summaries))  # Send current summaries with each token

    # Final yield with complete state
    if last_state:
        final_response = last_state.get("result", last_response)
        # Use current_summaries for final display if available
        final_summaries_display = "\n".join(current_summaries) if current_summaries else ""
        yield (final_response, last_state.get("visited_nodes", []), filter_news_info, final_summaries_display)

def main():
    """
    Test function for debugging the agent graph.
    This function is kept for testing purposes but not used as main entry point.
    """
    load_dotenv()
    print("🧪 Testing filter news display...")
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