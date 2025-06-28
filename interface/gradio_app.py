import gradio as gr
from agents.agent_core import process_command

def chat_interface(message):
    result = process_command(message)
    return result["result"]

iface = gr.Interface(
    fn=chat_interface,
    inputs=gr.Textbox(lines=2, placeholder="Type a command: Add AI, Show me news..."),
    outputs="text",
    title="Personalized News Agent"
)

def launch():
    iface.launch()
