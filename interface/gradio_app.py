import gradio as gr
from agents.agent_graph import process_command, process_command_stream

def chat_interface(message):
    result = process_command(message)
    return result["output"]

def chat_interface_stream(message):
    for partial, _ in process_command_stream(message):
        yield partial

iface = gr.Interface(
    fn=chat_interface_stream,
    inputs=gr.Textbox(lines=2, placeholder="Type a command: Add AI, Show me news..."),
    outputs=[
        gr.Textbox(label="Agent Response", lines=8, interactive=False)
    ],
    title="Personalized News Agent"
)

def launch():
    iface.launch()


