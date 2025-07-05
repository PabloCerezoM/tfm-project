import os
from dotenv import load_dotenv
from typing import Callable
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END
from agents.state_types import State
from agents.command_parser import parse_command_node
from agents.tools import (
    tool_store_interest_node, 
    tool_fetch_news_node, 
    tool_list_interests_node, 
    tool_remove_interest_node,
    summarize_article_stream
)
from services.news import fetch_news
from agents.tools import is_news_about_interest, summarize_article_stream
from concurrent.futures import ThreadPoolExecutor

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

load_dotenv()
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
graph.add_node("fetch_news", make_node(tool_fetch_news_node(llm), "fetch_news"))
graph.add_node("final_output", make_node(lambda state: {
    "output": state.get("result", "Error"),
    "visited_nodes": state.get("visited_nodes", [])
}, "final_output"))

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
        return "final_output"

graph.add_conditional_edges(
    "parse_command",
    route_action,
    {
        "store_interest": "store_interest",
        "fetch_news": "fetch_news",
        "list_interests": "list_interests",
        "remove_interest": "remove_interest",  
        "final_output": "final_output",
    },
)
graph.add_edge("store_interest", "final_output")
graph.add_edge("fetch_news", "final_output")
graph.add_edge("list_interests", "final_output")
graph.add_edge("remove_interest", "final_output")
graph.add_edge("final_output", END)
graph.set_entry_point("parse_command")

my_graph = graph.compile()

def process_command(message: str) -> State:
    inputs: State = {"user_input": message}
    result = my_graph.invoke(inputs)
    return result

def process_command_stream(message: str):
    """
    Si la acción es fetch_news, hace streaming de los resúmenes de noticias.
    Para el resto de acciones, devuelve solo el resultado final.
    """
    inputs: State = {"user_input": message}
    result = my_graph.invoke(inputs)
    visited = result.get("visited_nodes", [])
    action = result.get("action")
    if action == "fetch_news":
        from services.memory import load_interests
        from services.news import fetch_news
        from agents.tools import is_news_about_interest, summarize_article_stream
        interests = load_interests()
        news = fetch_news(page_size=10, language="en")
        any_found = False
        accumulated = ""
        def check_match(n):
            match, _ = is_news_about_interest(llm, n, interests)
            return (n, match)
        with ThreadPoolExecutor() as executor:
            results = list(executor.map(check_match, news))
        for n, match in results:
            if match and n["url"]:
                any_found = True
                summary = ""
                for partial in summarize_article_stream(llm, n["url"]):
                    if partial:
                        summary = partial
                        formatted = f"**[{n['title']}]({n['url']})**\n{summary}\n\n"
                        yield accumulated + formatted, visited + ["fetch_news"]
                formatted = f"**[{n['title']}]({n['url']})**\n{summary}\n\n"
                accumulated += formatted
        if not any_found:
            yield "There is no news for your current interests.", visited + ["fetch_news"]
    else:
        output = result.get("result") or result.get("output") or ""
        yield output, visited
