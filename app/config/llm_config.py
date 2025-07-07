"""
LLM configuration and client setup.
"""
from langchain_openai import ChatOpenAI
from config.settings import settings


def create_llm_client() -> ChatOpenAI:
    """Create and configure LLM client."""
    return ChatOpenAI(
        model=settings.MODEL_ID,
        openai_api_key=settings.API_KEY,
        openai_api_base=settings.SERVER_URL,
        max_tokens=settings.MAX_TOKENS,
        temperature=settings.TEMPERATURE,
        top_p=settings.TOP_P,
        streaming=True,
    )


# Global LLM instance
llm = create_llm_client()
