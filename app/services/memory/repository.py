"""
Repository for managing user interests persistence.
"""
import json
import os
from typing import List
from config.settings import settings
from core.exceptions import InterestManagementError
from services.memory.models import UserInterests


class InterestsRepository:
    """Repository for managing user interests storage."""
    
    def __init__(self, file_path: str = None):
        self.file_path = file_path or settings.USER_INTERESTS_FILE
        self._ensure_data_directory()
    
    def _ensure_data_directory(self):
        """Ensure the data directory exists."""
        os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
    
    def load_interests(self) -> UserInterests:
        """Load user interests from file."""
        try:
            if not os.path.exists(self.file_path):
                return UserInterests(interests=[])
            
            with open(self.file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    return UserInterests(interests=data)
                else:
                    raise InterestManagementError("Invalid interests file format")
        except (json.JSONDecodeError, IOError) as e:
            raise InterestManagementError(f"Failed to load interests: {str(e)}")
    
    def save_interests(self, interests: UserInterests):
        """Save user interests to file."""
        try:
            with open(self.file_path, "w", encoding="utf-8") as f:
                json.dump(interests.interests, f, indent=2)
        except IOError as e:
            raise InterestManagementError(f"Failed to save interests: {str(e)}")
    
    def add_interest(self, interest: str) -> bool:
        """Add an interest and save to file."""
        if not interest or not interest.strip():
            raise InterestManagementError("Interest cannot be empty")
        
        interest = interest.strip()
        interests = self.load_interests()
        added = interests.add_interest(interest)
        
        if added:
            self.save_interests(interests)
        
        return added
    
    def remove_interest(self, interest: str) -> bool:
        """Remove an interest and save to file."""
        if not interest or not interest.strip():
            raise InterestManagementError("Interest cannot be empty")
        
        interest = interest.strip()
        interests = self.load_interests()
        removed = interests.remove_interest(interest)
        
        if removed:
            self.save_interests(interests)
        
        return removed
    
    def get_interests_list(self) -> List[str]:
        """Get list of all interests."""
        return self.load_interests().interests
    
    def has_interests(self) -> bool:
        """Check if any interests are stored."""
        return not self.load_interests().is_empty()


# Global repository instance
interests_repository = InterestsRepository()
