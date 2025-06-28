import os

from openai import OpenAI
from dotenv import dotenv_values
from langchain_openai import ChatOpenAI

ENV_CONFIG = dotenv_values(".env")
API_KEY = ENV_CONFIG.get("API_KEY")
SERVER_URL = ENV_CONFIG.get("SERVER_URL", "http://g4.etsisi.upm.es:8833/v1")
MODEL_ID = ENV_CONFIG.get("MODEL_ID", "meta-llama/Llama-3.1-8B-Instruct")

chat_llm = ChatOpenAI(
    model=MODEL_ID,
    openai_api_key=API_KEY,
    openai_api_base=SERVER_URL,
    max_tokens=2048,
    temperature=0.7,
    top_p=0.9,
    streaming=True,
)

USER_PROMPT_TEMPLATE = """
Hi, my name is {name}. What time is it?
""".strip()

def main():
    messages = [
        ("system", "You are a helpful assistant."),
        ("user", USER_PROMPT_TEMPLATE.format(name="John")),
    ]
    response = chat_llm.invoke(messages)
    print(response)


if __name__ == "__main__":
    main()
