"""
Data models for memory/interests management.
"""
from dataclasses import dataclass
from typing import List
import json


@dataclass
class UserInterests:
    """Model for user interests."""
    interests: List[str]
    
    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.interests)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'UserInterests':
        """Create from JSON string."""
        interests = json.loads(json_str)
        return cls(interests=interests)
    
    def add_interest(self, interest: str) -> bool:
        """Add interest if not already present."""
        if interest not in self.interests:
            self.interests.append(interest)
            return True
        return False
    
    def remove_interest(self, interest: str) -> bool:
        """Remove interest if present."""
        if interest in self.interests:
            self.interests.remove(interest)
            return True
        return False
    
    def has_interest(self, interest: str) -> bool:
        """Check if interest exists."""
        return interest in self.interests
    
    def get_interests_string(self) -> str:
        """Get interests as comma-separated string."""
        return ", ".join(self.interests)
    
    def is_empty(self) -> bool:
        """Check if no interests are stored."""
        return len(self.interests) == 0
