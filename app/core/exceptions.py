"""
Custom exceptions for the TFM project.
"""


class TFMException(Exception):
    """Base exception for TFM project."""
    pass


class ConfigurationError(TFMException):
    """Raised when there's a configuration error."""
    pass


class NewsAPIError(TFMException):
    """Raised when there's an error with the News API."""
    pass


class LLMError(TFMException):
    """Raised when there's an error with the LLM."""
    pass


class InterestManagementError(TFMException):
    """Raised when there's an error managing user interests."""
    pass


class ContentScrapingError(TFMException):
    """Raised when there's an error scraping content."""
    pass


class ValidationError(TFMException):
    """Raised when there's a validation error."""
    pass
