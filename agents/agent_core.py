import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from agents.command_parser import parse_command
from agents.tools import tool_store_interest, tool_fetch_news

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

def process_command(message):
    command = parse_command(message, llm)
    action = command.get("action")
    if action == "store_interest":
        return tool_store_interest(command)
    elif action == "fetch_news":
        return tool_fetch_news(command, llm)
    else:
        return {"result": "No entendí el comando. Por favor, intenta de nuevo."}
