"""
Legacy command parser - delegates to new node implementation.
This file is kept for backward compatibility with existing code.
"""
from agents.nodes.command_parser import CommandParserNode
from agents.state_types import State


def parse_command_node(llm):
    """
    Returns a node that uses the LLM to parse the user's command.
    Legacy function that delegates to new CommandParserNode.
    """
    command_parser = CommandParserNode(llm)
    return command_parser.parse_command
