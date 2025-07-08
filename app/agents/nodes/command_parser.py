"""
Command parser node for interpreting user commands.
"""
import ast
from typing import Dict, Any
from langchain_openai import ChatOpenAI
from agents.state_types import State
from core.models import ActionType
from core.exceptions import ValidationError
from utils.validation import CommandValidator


class CommandParserNode:
    """Node responsible for parsing user commands using LLM."""
    
    def __init__(self, llm: ChatOpenAI):
        self.llm = llm
        self.validator = CommandValidator()
    
    def _create_system_prompt(self) -> str:
        """Create the system prompt for command parsing."""
        return (
            "You are an assistant that interprets user commands about interests and news.\n"
            "If the message is to add an interest, reply as follows:\n"
            '{"action": "store_interest", "interest": "<INTEREST>"}\n'
            "If the message is to remove/delete an interest, reply as follows:\n"
            '{"action": "remove_interest", "interest": "<INTEREST>"}\n'
            "If the message is to list interests, reply as follows:\n"
            '{"action": "list_interests"}\n'
            "If the message is to show news, reply as follows:\n"
            '{"action": "fetch_news"}\n'
            "Examples:\n"
            " - input = 'Add AI' -> output = {'action': 'store_interest', 'interest': 'AI'}\n"
            " - input = 'Remove IA' -> output = {'action': 'remove_interest', 'interest': 'IA'}\n"
            " - input = 'Show interests' -> output = {'action': 'list_interests'}"
        )
    
    def _parse_llm_response(self, response: str) -> Dict[str, Any]:
        """Parse and validate LLM response."""
        parsed = self.validator.parse_llm_command_response(response)
        
        if parsed is None:
            return {"action": ActionType.UNKNOWN.value}
        
        return parsed
    
    def parse_command(self, state: State) -> State:
        """
        Parse user command using LLM.
        
        Args:
            state: Current state containing user_input
            
        Returns:
            Updated state with parsed action and parameters
        """
        try:
            # Validate user input
            user_input = self.validator.validate_user_input(state["user_input"])
            
            # Create prompt
            prompt = [
                {"role": "system", "content": self._create_system_prompt()},
                {"role": "user", "content": user_input},
            ]
            
            # Get LLM response
            result = self.llm.invoke(prompt)
            response = result.content.strip()
            
            # Parse and validate response
            parsed_command = self._parse_llm_response(response)
            
            # Update state with parsed command
            state.update(parsed_command)
            
            # Validate interest if present
            if "interest" in parsed_command and parsed_command["interest"]:
                try:
                    validated_interest = self.validator.validate_interest(parsed_command["interest"])
                    state["interest"] = validated_interest
                except ValidationError as e:
                    print(f"[WARNING] Interest validation failed: {e}")
                    state["action"] = ActionType.UNKNOWN.value
                    state["result"] = f"Invalid interest: {str(e)}"
            
        except ValidationError as e:
            print(f"[ERROR] Command validation failed: {e}")
            state["action"] = ActionType.UNKNOWN.value
            state["result"] = f"Invalid command: {str(e)}"
        except Exception as e:
            print(f"[ERROR] Command parsing failed: {e}")
            state["action"] = ActionType.UNKNOWN.value
            state["result"] = "Failed to parse command. Please try again."
        
        return state
