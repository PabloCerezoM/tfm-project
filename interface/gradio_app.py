import gradio as gr
from agents.agent_graph import process_command

def chat_interface(message):
    result = process_command(message)
    visited = result.get("visited_nodes", [])
    # Markdown diagram with emoji
    nodes_list = [
        "parse_command",
        "store_interest",
        "fetch_news",
        "final_output"
    ]
    diagram = ""
    for node in nodes_list:
        if node in visited:
            diagram += f"**➡️ {node}**\n\n"
        else:
            diagram += f"{node}\n\n"
    return result["output"], diagram

iface = gr.Interface(
    fn=chat_interface,
    inputs=gr.Textbox(lines=2, placeholder="Type a command: Add AI, Show me news..."),
    outputs=[
        gr.Markdown(label="Agent Response"),
        gr.Markdown(label="Graph Node Path")
    ],
    title="Personalized News Agent"
)

def launch():
    iface.launch()


