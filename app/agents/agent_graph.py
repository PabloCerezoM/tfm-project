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
    """
    inputs: State = {"user_input": message}
    last_state = None
    for event_type, value in my_graph.stream(inputs, stream_mode=["values", "custom"]):  
        if event_type == "values":
            last_state = value  # Store the last state
            last_node = value.get("visited_nodes", [None])[-1]

            # print the state without the "content" key of each news item
            if last_node == "filter_news":
                yield ("filtered_news", value.get("news", []))
            elif last_node == "summarize":
                yield ("summarized_news", value.get("news", []))
        else:
            yield ("partial_summarized_news", value.get("partial_summaries", (None, None)))

    yield ("last_state", last_state)

def main():
    load_dotenv()
    for event_type, value in process_command_stream("Show me the news"):
        print("=" * 100)
        if event_type == "filtered_news":
            # print the filtered news
            news = [ {k: v for k, v in n.items() if k != "content"} for n in value ]
            print("Filtered News:", json.dumps(news, indent=2))
        elif event_type == "summarized_news":
            # print the summarized news
            news = [ {k: v for k, v in n.items() if k != "content"} for n in value ]
            print("Summarized News:", json.dumps(news, indent=2))
        elif event_type == "partial_summarized_news":
            # print the partial summaries
            print("Partial Summary:", value)
        elif event_type == "last_state":
            # print the last state
            print("Last State:", json.dumps(value, indent=2))
        print("=" * 100)

if __name__ == "__main__":
    main()