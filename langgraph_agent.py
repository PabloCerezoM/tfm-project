import os
from dotenv import load_dotenv
from typing import TypedDict
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END
from agent_functions import tool_store_interest, tool_fetch_news

load_dotenv()

API_KEY = os.environ.get("API_KEY")
SERVER_URL = os.environ.get("SERVER_URL", "http://g4.etsisi.upm.es:8833/v1")
MODEL_ID = os.environ.get("MODEL_ID", "meta-llama/Llama-3.1-8B-Instruct")

llm = ChatOpenAI(
    model=MODEL_ID,
    openai_api_key=API_KEY,
    openai_api_base=SERVER_URL,
    max_tokens=2048,
    temperature=0.7,
    top_p=0.9,
    streaming=False,
)

class State(TypedDict, total=False):
    user_input: str
    interest: str
    action: str
    result: str
    output: str

def parse_command_node(input_dict):
    print("[DEBUG] parse_command_node input:", input_dict)
    message = input_dict["user_input"]
    system_prompt = (
        "You are an assistant that interprets user commands about interests and news.\n"
        "If the message is to add an interest, reply as follows:\n"
        '{"action": "store_interest", "interest": "<INTEREST>"}\n'
        "If the message is to show news, reply as follows:\n"
        '{"action": "fetch_news"}\n'
        "Example: input = 'Add AI' -> output = {'action': 'store_interest', 'interest': 'AI'}"
    )
    prompt = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": message},
    ]
    res = llm.invoke(prompt)
    print("[DEBUG] LLM response:", repr(res))
    import json
    action_dict = {}
    try:
        action_dict = json.loads(res.content)
    except Exception as e:
        print("[DEBUG] JSON parsing error:", e)
    print("[DEBUG] action_dict:", action_dict)
    return action_dict

def join_output_node(input_dict):
    print("[DEBUG] join_output_node input:", input_dict)
    return {"output": input_dict.get("result", "The action could not be completed.")}

def branch_func(state):
    action = state.get("action")
    if action == "store_interest":
        return "store_interest"
    elif action == "fetch_news":
        return "fetch_news"
    else:
        return "join_output"

def build_graph():
    sg = StateGraph(State)
    sg.add_node("parse_command", parse_command_node)
    sg.add_node("store_interest", tool_store_interest)
    # Usa una lambda para pasar el llm a tool_fetch_news
    sg.add_node("fetch_news", lambda input_dict: tool_fetch_news(input_dict, llm))
    sg.add_node("join_output", join_output_node)

    sg.add_conditional_edges(
        "parse_command", branch_func,
        {
            "store_interest": "store_interest",
            "fetch_news": "fetch_news",
            "join_output": "join_output",
        }
    )

    sg.add_edge("store_interest", "join_output")
    sg.add_edge("fetch_news", "join_output")
    sg.add_edge("join_output", END)

    sg.set_entry_point("parse_command")
    return sg.compile()

graph = build_graph()

def process_command(command: str):
    result = graph.invoke({"user_input": command})
    return result["output"]
