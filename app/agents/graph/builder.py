"""
Graph builder for the news agent workflow.
"""
from typing import Callable
from langgraph.graph import StateGraph, END
from agents.state_types import State
from agents.nodes.command_parser import CommandParserNode
from agents.nodes.interest_nodes import InterestManagerNode
from agents.nodes.news_nodes import NewsProcessorNode
from agents.nodes.content_nodes import ContentProcessorNode
from config.llm_config import llm
from core.constants import NodeNames


class AgentGraphBuilder:
    """Builder class for creating the agent workflow graph."""
    
    def __init__(self):
        self.graph = StateGraph(State)
        self.llm = llm
        
        # Initialize node processors
        self.command_parser = CommandParserNode(self.llm)
        self.interest_manager = InterestManagerNode()
        self.news_processor = NewsProcessorNode(self.llm)
        self.content_processor = ContentProcessorNode(self.llm)
    
    def add_visited_node(self, state: State, node_name: str) -> State:
        """Add a node to the visited nodes list."""
        if "visited_nodes" not in state or state["visited_nodes"] is None:
            state["visited_nodes"] = []
        state["visited_nodes"].append(node_name)
        return state
    
    def make_node(self, fn: Callable[[State], State], node_name: str) -> Callable[[State], State]:
        """Wrapper to track visited nodes."""
        def wrapped(state: State) -> State:
            self.add_visited_node(state, node_name)
            return fn(state)
        return wrapped
    
    def route_action(self, state: State) -> str:
        """Route to appropriate action based on parsed command."""
        action = state.get("action")
        
        if action == "store_interest":
            return NodeNames.STORE_INTEREST
        elif action == "fetch_news":
            return NodeNames.FETCH_NEWS
        elif action == "list_interests":
            return NodeNames.LIST_INTERESTS
        elif action == "remove_interest":
            return NodeNames.REMOVE_INTEREST
        else:
            state["result"] = "Sorry, I didn't understand the command. Please try again."
            return "END"
    
    def build_graph(self) -> StateGraph:
        """Build and configure the complete workflow graph."""
        
        # Add nodes with tracking
        self.graph.add_node(
            NodeNames.PARSE_COMMAND, 
            self.make_node(self.command_parser.parse_command, NodeNames.PARSE_COMMAND)
        )
        self.graph.add_node(
            NodeNames.LIST_INTERESTS, 
            self.make_node(self.interest_manager.list_interests, NodeNames.LIST_INTERESTS)
        )
        self.graph.add_node(
            NodeNames.REMOVE_INTEREST, 
            self.make_node(self.interest_manager.remove_interest, NodeNames.REMOVE_INTEREST)
        )
        self.graph.add_node(
            NodeNames.STORE_INTEREST, 
            self.make_node(self.interest_manager.store_interest, NodeNames.STORE_INTEREST)
        )
        self.graph.add_node(
            NodeNames.FETCH_NEWS, 
            self.make_node(self.news_processor.fetch_news, NodeNames.FETCH_NEWS)
        )
        self.graph.add_node(
            NodeNames.FILTER_NEWS, 
            self.make_node(self.news_processor.filter_news, NodeNames.FILTER_NEWS)
        )
        self.graph.add_node(
            NodeNames.SCRAPE_CONTENT, 
            self.make_node(self.content_processor.scrape_content, NodeNames.SCRAPE_CONTENT)
        )
        self.graph.add_node(
            NodeNames.SUMMARIZE, 
            self.make_node(self.content_processor.summarize, NodeNames.SUMMARIZE)
        )
        
        # Add conditional routing from parse_command
        self.graph.add_conditional_edges(
            NodeNames.PARSE_COMMAND,
            self.route_action,
            {
                NodeNames.STORE_INTEREST: NodeNames.STORE_INTEREST,
                NodeNames.FETCH_NEWS: NodeNames.FETCH_NEWS,
                NodeNames.LIST_INTERESTS: NodeNames.LIST_INTERESTS,
                NodeNames.REMOVE_INTEREST: NodeNames.REMOVE_INTEREST,
                "final_output": END,
            },
        )
        
        # Add sequential edges for news processing workflow
        self.graph.add_edge(NodeNames.STORE_INTEREST, END)
        self.graph.add_edge(NodeNames.FETCH_NEWS, NodeNames.FILTER_NEWS)
        self.graph.add_edge(NodeNames.FILTER_NEWS, NodeNames.SCRAPE_CONTENT)
        self.graph.add_edge(NodeNames.SCRAPE_CONTENT, NodeNames.SUMMARIZE)
        self.graph.add_edge(NodeNames.SUMMARIZE, END)
        self.graph.add_edge(NodeNames.LIST_INTERESTS, END)
        self.graph.add_edge(NodeNames.REMOVE_INTEREST, END)
        
        # Set entry point
        self.graph.set_entry_point(NodeNames.PARSE_COMMAND)
        
        return self.graph
    
    def compile(self):
        """Build and compile the graph."""
        graph = self.build_graph()
        return graph.compile()


# Create a global instance
graph_builder = AgentGraphBuilder()
compiled_graph = graph_builder.compile()
