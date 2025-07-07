from typing import TypedDict, List, Optional

class State(TypedDict, total=False):
    user_input: str
    action: str
    interest: str
    news: List[dict]
    all_news_filtered: List[dict]  # Added for news filter display
    result: Optional[str]
    visited_nodes: List[str]
