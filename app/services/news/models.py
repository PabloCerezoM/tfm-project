"""
Data models for news service.
"""
from dataclasses import dataclass
from typing import Dict, Any, Optional


@dataclass
class NewsSource:
    """Model for news source."""
    name: str
    id: Optional[str] = None


@dataclass
class RawNewsArticle:
    """Model for raw news article from API."""
    title: str
    description: str
    url: str
    source: NewsSource
    published_at: Optional[str] = None
    url_to_image: Optional[str] = None
    
    @classmethod
    def from_api_response(cls, data: Dict[str, Any]) -> 'RawNewsArticle':
        """Create instance from News API response."""
        source_data = data.get("source", {})
        source = NewsSource(
            name=source_data.get("name", ""),
            id=source_data.get("id")
        )
        
        return cls(
            title=data.get("title", ""),
            description=data.get("description", "") or "",
            url=data.get("url", ""),
            source=source,
            published_at=data.get("publishedAt"),
            url_to_image=data.get("urlToImage"),
        )
