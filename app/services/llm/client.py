"""
LLM client wrapper for standardized interactions.
"""
from typing import List, Dict, Any, Generator
from langchain_openai import ChatOpenAI
from config.llm_config import llm
from core.exceptions import LLMError


class LLMClient:
    """Wrapper for LLM interactions."""
    
    def __init__(self, llm_instance: ChatOpenAI = None):
        self.llm = llm_instance or llm
    
    def invoke(self, messages: List[Dict[str, str]]) -> str:
        """
        Invoke LLM with messages and return response.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            
        Returns:
            The LLM response content
        """
        try:
            result = self.llm.invoke(messages)
            return result.content.strip()
        except Exception as e:
            raise LLMError(f"LLM invocation failed: {str(e)}")
    
    def stream(self, messages: List[Dict[str, str]]) -> Generator[str, None, None]:
        """
        Stream LLM response token by token.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            
        Yields:
            Individual tokens from the LLM response
        """
        try:
            stream = self.llm.stream(messages)
            for chunk in stream:
                token = getattr(chunk, 'content', None)
                if token:
                    yield token
        except Exception as e:
            raise LLMError(f"LLM streaming failed: {str(e)}")


# Global LLM client instance
llm_client = LLMClient()
