"""
Interest management nodes for storing, listing, and removing user interests.
"""
from typing import List
from agents.state_types import State
from services.memory.repository import interests_repository
from utils.formatters import InterestFormatter
from core.exceptions import InterestManagementError


class InterestManagerNode:
    """Node responsible for managing user interests."""
    
    def __init__(self):
        self.repository = interests_repository
        self.formatter = InterestFormatter()
    
    def store_interest(self, state: State) -> State:
        """
        Add a new interest to the user's interest list.
        
        Args:
            state: Current state containing interest to add
            
        Returns:
            Updated state with result message
        """
        interest = state.get("interest")
        
        if not interest:
            state["result"] = "No interest detected to add."
            return state
        
        try:
            added = self.repository.add_interest(interest)
            current_interests = self.repository.get_interests_list()
            
            if added:
                state["result"] = self.formatter.format_interest_added(interest, current_interests)
            else:
                state["result"] = f"Interest '{interest}' already exists in your interests."
                
        except InterestManagementError as e:
            print(f"[ERROR] Failed to store interest: {e}")
            state["result"] = f"Failed to add interest: {str(e)}"
        except Exception as e:
            print(f"[ERROR] Unexpected error storing interest: {e}")
            state["result"] = "An unexpected error occurred while adding the interest."
        
        return state
    
    def list_interests(self, state: State) -> State:
        """
        List all current user interests.
        
        Args:
            state: Current state
            
        Returns:
            Updated state with formatted interests list
        """
        try:
            interests = self.repository.get_interests_list()
            state["result"] = self.formatter.format_interests_list(interests)
            
        except InterestManagementError as e:
            print(f"[ERROR] Failed to list interests: {e}")
            state["result"] = f"Failed to retrieve interests: {str(e)}"
        except Exception as e:
            print(f"[ERROR] Unexpected error listing interests: {e}")
            state["result"] = "An unexpected error occurred while retrieving interests."
        
        return state
    
    def remove_interest(self, state: State) -> State:
        """
        Remove an interest from the user's interest list.
        
        Args:
            state: Current state containing interest to remove
            
        Returns:
            Updated state with result message
        """
        interest = state.get("interest")
        
        if not interest:
            state["result"] = "No interest detected to remove."
            return state
        
        try:
            removed = self.repository.remove_interest(interest)
            current_interests = self.repository.get_interests_list()
            
            if removed:
                state["result"] = self.formatter.format_interest_removed(interest, current_interests)
            else:
                state["result"] = self.formatter.format_interest_not_found(interest)
                
        except InterestManagementError as e:
            print(f"[ERROR] Failed to remove interest: {e}")
            state["result"] = f"Failed to remove interest: {str(e)}"
        except Exception as e:
            print(f"[ERROR] Unexpected error removing interest: {e}")
            state["result"] = "An unexpected error occurred while removing the interest."
        
        return state
