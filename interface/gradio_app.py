import gradio as gr
from agents.agent_graph import process_command, process_command_stream
from services.memory import load_interests

def chat_interface(message):
    result = process_command(message)
    return result["output"]

def chat_interface_stream(message):
    for partial, _ in process_command_stream(message):
        yield partial

# Nueva función para mostrar intereses
def mostrar_intereses():
    intereses = load_interests()
    if intereses:
        return ", ".join(intereses)
    else:
        return "No hay intereses guardados."

with gr.Blocks() as demo:
    gr.Markdown("# Personalized News Agent")
    chat_in = gr.Textbox(lines=2, placeholder="Type a command: Add AI, Show me news...")
    chat_out = gr.Markdown(label="Agent Response")
    intereses_out = gr.Textbox(label="Show interests", interactive=False)
    with gr.Row():
        send_btn = gr.Button("Send")
        intereses_btn = gr.Button("Show interests")

    send_btn.click(chat_interface_stream, inputs=chat_in, outputs=chat_out)
    intereses_btn.click(mostrar_intereses, outputs=intereses_out)

def launch():
    demo.launch()


