from typing import TypedDict, List, Optional

class State(TypedDict, total=False):
    user_input: str
    action: str
    interest: str
    result: str
    output: str
    visited_nodes: List[str]
