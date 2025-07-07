"""
Validation utilities for the TFM project.
"""
import ast
from typing import Dict, Any, Optional
from core.models import ActionType, UserCommand
from core.exceptions import ValidationError


class CommandValidator:
    """Validator for user commands and LLM responses."""
    
    @staticmethod
    def validate_user_input(user_input: str) -> str:
        """
        Validate and clean user input.
        
        Args:
            user_input: Raw user input string
            
        Returns:
            Cleaned user input
            
        Raises:
            ValidationError: If input is invalid
        """
        if not user_input or not user_input.strip():
            raise ValidationError("User input cannot be empty")
        
        cleaned_input = user_input.strip()
        
        if len(cleaned_input) > 1000:  # Reasonable limit
            raise ValidationError("User input is too long (max 1000 characters)")
        
        return cleaned_input
    
    @staticmethod
    def parse_llm_command_response(response: str) -> Optional[Dict[str, Any]]:
        """
        Parse and validate LLM command response.
        
        Args:
            response: LLM response string
            
        Returns:
            Parsed command dictionary or None if invalid
        """
        if not response:
            return None
        
        response = response.strip()
        
        # Check if it's a valid JSON-like structure
        if not (response.startswith("{") and response.endswith("}")):
            return None
        
        try:
            parsed = ast.literal_eval(response)
            
            # Validate required fields
            if not isinstance(parsed, dict):
                return None
            
            if "action" not in parsed:
                return None
            
            # Validate action type
            action_value = parsed["action"]
            valid_actions = [action.value for action in ActionType]
            
            if action_value not in valid_actions:
                parsed["action"] = ActionType.UNKNOWN.value
            
            return parsed
            
        except (ValueError, SyntaxError):
            return None
    
    @staticmethod
    def validate_interest(interest: str) -> str:
        """
        Validate and clean interest string.
        
        Args:
            interest: Interest string to validate
            
        Returns:
            Cleaned interest string
            
        Raises:
            ValidationError: If interest is invalid
        """
        if not interest or not interest.strip():
            raise ValidationError("Interest cannot be empty")
        
        cleaned_interest = interest.strip()
        
        if len(cleaned_interest) > 100:  # Reasonable limit
            raise ValidationError("Interest is too long (max 100 characters)")
        
        # Basic sanitization
        if any(char in cleaned_interest for char in ['<', '>', '"', "'"]):
            raise ValidationError("Interest contains invalid characters")
        
        return cleaned_interest


class NewsValidator:
    """Validator for news-related data."""
    
    @staticmethod
    def validate_news_url(url: str) -> bool:
        """
        Validate if URL looks like a valid news URL.
        
        Args:
            url: URL to validate
            
        Returns:
            True if URL appears valid
        """
        if not url or not url.strip():
            return False
        
        url = url.strip().lower()
        
        # Basic URL validation
        if not (url.startswith('http://') or url.startswith('https://')):
            return False
        
        # Check for common malicious patterns
        malicious_patterns = ['javascript:', 'data:', 'file:', 'ftp:']
        if any(pattern in url for pattern in malicious_patterns):
            return False
        
        return True
