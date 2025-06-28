from agents.state_types import State


def parse_command_node(llm):
    """
    Returns a node that uses the LLM to parse the user's command.
    """
    def node(state: State) -> State:
        message = state["user_input"]
        system_prompt = (
            "You are an assistant that interprets user commands about interests and news.\n"
            "If the message is to add an interest, reply as follows:\n"
            '{"action": "store_interest", "interest": "<INTEREST>"}\n'
            "If the message is to remove/delete an interest, reply as follows:\n"
            '{"action": "remove_interest", "interest": "<INTEREST>"}\n'
            "If the message is to list interests, reply as follows:\n"
            '{"action": "list_interests"}\n'
            "If the message is to show news, reply as follows:\n"
            '{"action": "fetch_news"}\n'
            "Examples:\n"
            " - input = 'Add AI' -> output = {'action': 'store_interest', 'interest': 'AI'}\n"
            " - input = 'Remove IA' -> output = {'action': 'remove_interest', 'interest': 'IA'}\n"
            " - input = 'Show interests' -> output = {'action': 'list_interests'}"
        )
        prompt = [
            {"role": "system", "content": system_prompt},
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
