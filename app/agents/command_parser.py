from agents.state_types import State

SYSTEM_PROMPT = """
You are an assistant that interprets user commands about interests and news.
If the message is to add an interest, reply as follows:
{"action": "store_interest", "interest": "<INTEREST>"}
If the message is to remove/delete an interest, reply as follows:
{"action": "remove_interest", "interest": "<INTEREST>"}
If the message is to list interests, reply as follows:
{"action": "list_interests"}
If the message is to show news, reply as follows:
{"action": "fetch_news"}
If the message cannot be interpreted as any of the above actions, reply as follows:
{"action": "unknown"}
Examples:
 - input = 'Add AI' -> output = {'action': 'store_interest', 'interest': 'AI'}
 - input = 'Remove IA' -> output = {'action': 'remove_interest', 'interest': 'IA'}
 - input = 'Show interests' -> output = {'action': 'list_interests'}
 - input = 'Hello' -> output = {'action': 'unknown'}
""".strip()


def parse_command_node(llm):
    """
    Returns a node that uses the LLM to parse the user's command.
    """
    def node(state: State) -> State:
        message = state["user_input"]
        prompt = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": message},
        ]
        import ast
        try:
            result = llm.invoke(prompt)
            content = result.content.strip()
            if content.startswith("{") and content.endswith("}"):
                parsed = ast.literal_eval(content)
                state.update(parsed)
            else:
                state["action"] = "unknown"
        except Exception:
            state["action"] = "unknown"
        return state
    return node
