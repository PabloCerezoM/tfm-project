"""
Data models for the TFM project.
"""
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from enum import Enum


class ActionType(Enum):
    """Enumeration of available action types."""
    STORE_INTEREST = "store_interest"
    REMOVE_INTEREST = "remove_interest"
    LIST_INTERESTS = "list_interests"
    FETCH_NEWS = "fetch_news"
    UNKNOWN = "unknown"


@dataclass
class NewsArticle:
    """Model for news articles."""
    title: str
    content: str = ""
    url: str = ""
    source: str = ""
    summary: str = ""
    matched_interests: bool = False
    match_reason: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "title": self.title,
            "content": self.content,
            "url": self.url,
            "source": self.source,
            "summary": self.summary,
            "matched_interests": self.matched_interests,
            "match_reason": self.match_reason,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'NewsArticle':
        """Create instance from dictionary."""
        return cls(
            title=data.get("title", ""),
            content=data.get("content", ""),
            url=data.get("url", ""),
            source=data.get("source", ""),
            summary=data.get("summary", ""),
            matched_interests=data.get("matched_interests", False),
            match_reason=data.get("match_reason", ""),
        )


@dataclass
class UserCommand:
    """Model for parsed user commands."""
    action: ActionType
    interest: Optional[str] = None
    raw_input: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "action": self.action.value,
            "interest": self.interest,
            "raw_input": self.raw_input,
        }


@dataclass
class ProcessingResult:
    """Model for processing results."""
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


@dataclass
class StreamingUpdate:
    """Model for streaming updates sent to the interface."""
    partial_response: str = ""
    visited_nodes: List[str] = field(default_factory=list)
    news_filter_info: str = ""
    summaries_info: str = ""
    
    def to_tuple(self) -> tuple:
        """Convert to tuple format expected by Gradio."""
        return (
            self.partial_response,
            self.visited_nodes,
            self.news_filter_info,
            self.summaries_info
        )
