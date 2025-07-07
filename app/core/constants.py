"""
Constants used throughout the application.
"""

# Node names
class NodeNames:
    PARSE_COMMAND = "parse_command"
    LIST_INTERESTS = "list_interests"
    REMOVE_INTEREST = "remove_interest"
    STORE_INTEREST = "store_interest"
    FETCH_NEWS = "fetch_news"
    FILTER_NEWS = "filter_news"
    SCRAPE_CONTENT = "scrape_content"
    SUMMARIZE = "summarize"


# UI Messages
class UIMessages:
    GENERATING_SUMMARIES = "📝 Generating summaries..."
    SUMMARIES_COMPLETED = "✅ Completed summaries for"
    NO_INTERESTS_CONFIGURED = "No user interests configured"
    NO_MATCH_WITH_INTERESTS = "No match with user interests"
    CONTENT_NOT_AVAILABLE = "Content not available for summary"
    

# API Response Status
class APIStatus:
    OK = "ok"
    ERROR = "error"


# Match Status Indicators
class MatchStatus:
    MATCH = "✅ MATCH"
    NO_MATCH = "❌ NO MATCH"


# Processing Indicators
class ProcessingIndicators:
    LOADING = "⏳"
    ARROW = "→"
